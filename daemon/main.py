import json

import requests
from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
from requests import get
from werkzeug import Response

from detector.config import KUBE_PROXY_IP, AGENT_PORT, DAEMON_PORT, REQUESTS_TOKEN, KUBE_PROXY_PORT

app = Flask(__name__)
CORS(app)
data = None
nodes = list()


def get_nodes():
    global nodes
    nodes = list()
    if REQUESTS_TOKEN is None:
        response = requests.get("http://" + KUBE_PROXY_IP + ":" + str(KUBE_PROXY_PORT) + "/api/v1/nodes").json()["items"]
        for node in response:
            try:
                if requests.get(
                        "http://" + node["status"]["addresses"][0]["address"] + ":" + str(AGENT_PORT), timeout=2).status_code == 200:
                    nodes.append({
                        "name": node["metadata"]["name"],
                        "ip_address": node["status"]["addresses"][0]["address"],
                        "agent": "true"
                    })
                else:
                    raise Exception
            except Exception:
                nodes.append({
                    "name": node["metadata"]["name"],
                    "ip_address": node["status"]["addresses"][0]["address"],
                    "agent": "false"
                })
    else:
        response = requests.get("https://" + KUBE_PROXY_IP + "/api/v1/pods",
                                headers={'Authorization': 'Bearer ' + REQUESTS_TOKEN}).json()["items"]
        for pod in response:
            ip = pod["status"]["podIP"]
            name = pod["spec"]["nodeName"]
            try:
                if pod["metadata"]["name"].startswith("detector-agent-"):
                    if requests.get(f"http://{ip}:{AGENT_PORT}", timeout=2).status_code == 200:
                        nodes.append({
                            "name": name,
                            "ip_address": ip,
                            "agent": "true"
                        })
                    else:
                        raise Exception
            except Exception:
                nodes.append({
                    "name": pod["metadata"]["name"],
                    "ip_address": pod["status"]["addresses"][0]["address"],
                    "agent": "false"
                })

@app.route('/', methods=["GET"])
@app.route('/status', methods=["GET"])
def index():
    return jsonify(data), 200


@app.route('/agents', methods=["GET"])
def agents():
    global nodes
    get_nodes()
    return json.dumps(nodes), 200


@app.route('/proxy/<path:path>')
def proxy(path):
    if REQUESTS_TOKEN is None:
        response = Response(get(f'{path}').content)
    else:
        response = Response(get(f'{path}', headers={'Authorization': 'Bearer ' + REQUESTS_TOKEN}).content)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route("/start", methods=["POST"])
def start():
    global data
    try:
        # Retrieve info from POST body
        data = request.get_json()

        # Get nodes
        get_nodes()

        # Start monitoring agents
        for node in nodes:
            if node["agent"] == "true":
                response = requests.post("http://" + node["ip_address"] + ":" + str(AGENT_PORT) + "/start", json=data, timeout=5)
                if response.status_code != 200:
                    raise Exception
    except Exception:
        data = None
        nodes.clear()
        return make_response(jsonify({
            "message": "Failed to start the monitoring agents",
            "nodes": nodes
        }), 500)

    return make_response(jsonify({
        "message": "Started the monitoring agents successfully",
        "nodes": nodes
    }), 200)


@app.route("/stop", methods=["POST"])
def stop():
    global data
    try:
        # Stop monitoring agents
        for node in nodes:
            if node["agent"] == "true":
                response = requests.post("http://" + node["ip_address"] + ":" + str(AGENT_PORT) + "/stop", timeout=5)
                if response.status_code != 200:
                    raise Exception
    except Exception:
        data = None
        nodes.clear()
        return "Failed to stop the monitoring agents", 500
    data = None
    nodes.clear()
    return "Stopped the monitoring agents successfully", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=DAEMON_PORT, debug=True)
