import json
import traceback
from time import time, ctime

import requests
from flask import Blueprint, make_response, request, jsonify

from detector.config import DAEMON_IP, DAEMON_PORT, WS_PORT, WS_MAX_SIZE, ALGORITHMS_FILE, KUBE_PROXY_IP, KUBE_PROXY_PORT, REQUESTS_TOKEN
from detector.utils import start_monitoring, stop_monitoring, redis_connection, start_inspecting, stop_inspecting

api = Blueprint("api", __name__, template_folder="templates")


@api.route("/api", methods=["GET"])
@api.route("/api/status", methods=["GET"])
def api_status():
    return "The detector API", 200


@api.route("/api/daemon/status", methods=["GET"])
def api_daemon_status():
    try:
        response = requests.get("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/status")
        return response.content, response.status_code
    except Exception:
        return "Failed to connect to Daemon", 500


@api.route("/api/daemon/agents", methods=["GET"])
def api_daemon_agents():
    try:
        response = requests.get("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/agents")
        return response.content, response.status_code
    except Exception:
        return "Failed to retrieve agents from Daemon", 500


@api.route("/api/monitoring/start", methods=["POST"])
def api_start_monitoring():
    data = request.get_json()
    data["start_time"] = ctime(round(time()))
    data["start_time_timestamp"] = round(time())
    data["ws_port"] = WS_PORT
    data["ws_max_size"] = WS_MAX_SIZE

    data["nodes"] = ["worker-1"]
    return start_monitoring(data)


@api.route("/api/monitoring/stop", methods=["POST"])
def api_stop_monitoring():
    return stop_monitoring()


@api.route("/api/inspecting/start", methods=["POST"])
def api_start_inspecting():
    data = request.get_json()
    data["start_time"] = ctime(round(time()))
    data["start_time_timestamp"] = round(time())
    return start_inspecting(data)


@api.route("/api/inspecting/stop", methods=["POST"])
def api_stop_inspecting():
    if request.args.get("id"):
        return stop_inspecting(request.args.get("id"))
    return stop_inspecting()


@api.route("/api/alarms", methods=["GET"])
def api_alarms():
    try:
        alarms_list = json.loads(redis_connection.get("alarms"))
        alarms_list["rows"].sort(key=lambda x: x["timestamp"], reverse=True)
        if request.args.get("size"):
            return jsonify(alarms_list["rows"][:int(request.args.get("size"))])
        else:
            return jsonify(alarms_list)
    except Exception:
        traceback.print_exc()
        return {}


@api.route("/api/alarms", methods=["DELETE"])
def api_alarms_delete():
    try:
        redis_connection.set("alarms", json.dumps({
            "total": 0,
            "totalNotFiltered": 0,
            "rows": []
        }))
        return jsonify({})
    except Exception:
        traceback.print_exc()
        return jsonify({})


@api.route("/api/algorithms", methods=["GET"])
def api_algorithms():
    try:
        with open(r"" + ALGORITHMS_FILE) as file:
            return jsonify(json.load(file))
    except Exception:
        traceback.print_exc()


@api.route("/api/resources/pods", methods=["GET"])
def api_resources_pods():
    pods = list()
    namespace = "default"
    if request.args.get("namespace"):
        namespace = request.args.get("namespace")
    try:
        if REQUESTS_TOKEN is None:
            pods += \
                requests.get("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/http://" + KUBE_PROXY_IP + ":" + str(
                    KUBE_PROXY_PORT) + "/api/v1/namespaces/" + namespace + "/pods",
                            timeout=5).json()["items"]
        else:
            pods += \
                requests.get("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/https://" + KUBE_PROXY_IP + "/api/v1/namespaces/" + namespace + "/pods",
                         timeout=5).json()["items"]
    except requests.exceptions.ConnectionError as e:
        print(e)
    return jsonify(pods)


@api.route("/api/resources/services", methods=["GET"])
def api_resources_services():
    services = list()
    namespace = "default"
    if request.args.get("namespace"):
        namespace = request.args.get("namespace")
    try:
        if REQUESTS_TOKEN is None:
            services += \
                requests.get(
                    "http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/http://" + KUBE_PROXY_IP + ":" + str(
                        KUBE_PROXY_PORT) + "/api/v1/namespaces/" + namespace + "/services",
                    timeout=5).json()["items"]
        else:
            services += \
                requests.get(
                    "http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/https://" + KUBE_PROXY_IP  + "/api/v1/namespaces/" + namespace + "/services",
                    timeout=5).json()["items"]
    except requests.exceptions.ConnectionError as e:
        print(e)
    return jsonify(services)


@api.route("/api/resources/deployments", methods=["GET"])
def api_resources_deployments():
    deployments = list()
    namespace = "default"
    if request.args.get("namespace"):
        namespace = request.args.get("namespace")
    try:
        if REQUESTS_TOKEN is None:
            deployments += \
                requests.get(
                    "http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/http://" + KUBE_PROXY_IP + ":" + str(
                        KUBE_PROXY_PORT) + "/apis/apps/v1/namespaces/" + namespace + "/deployments",
                    timeout=5).json()["items"]
        else:
            deployments += \
                requests.get(
                    "http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/https://" + KUBE_PROXY_IP  + "/apis/apps/v1/namespaces/" + namespace + "/deployments",
                    timeout=5).json()["items"]
    except requests.exceptions.ConnectionError as e:
        print(e)
    return jsonify(deployments)


@api.route("/api/resources/namespaces", methods=["GET"])
def api_resources_namespaces():
    namespaces = list()
    try:
        if REQUESTS_TOKEN is None:
            namespaces = \
                requests.get("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/http://" + KUBE_PROXY_IP + ":" + str(
                    KUBE_PROXY_PORT) + "/api/v1/namespaces", timeout=5).json()["items"]
        else:
            namespaces = \
                requests.get("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/https://" + KUBE_PROXY_IP + "/api/v1/namespaces", timeout=5).json()["items"]
    except requests.exceptions.ConnectionError as e:
        print(e)
    return jsonify(namespaces)


@api.route("/api/resources/nodes", methods=["GET"])
def api_resources_nodes():
    nodes = list()
    try:
        if REQUESTS_TOKEN is None:
            nodes = \
                requests.get("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/http://" + KUBE_PROXY_IP + ":" + str(
                    KUBE_PROXY_PORT) + "/api/v1/nodes", timeout=5).json()["items"]
        else:
            nodes = \
                requests.get("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/proxy/https://" + KUBE_PROXY_IP + "/api/v1/nodes", timeout=5).json()["items"]
    except requests.exceptions.ConnectionError as e:
        print(e)
    return jsonify(nodes)


@api.route("/api/stats", methods=["GET"])
def api_stats():
    x = time() * 1000
    response = make_response(json.dumps({
        "monitoring": {
            "total_syscalls": int(redis_connection.get("monitoring_total_syscalls")),
            "total_size": int(redis_connection.get("monitoring_total_size")),
            "total_batches": int(redis_connection.get("monitoring_total_batches")),
            "batch_length": int(redis_connection.get("monitoring_batch_length"))
        },
        "alarms": {
            "total": json.loads(redis_connection.get("alarms"))["total"]
        },
        "syscalls": {
            "x": x, "y": int(redis_connection.get("monitoring_batch_length"))
        },
    }))
    response.content_type = "application/json"
    return response
