import json
import traceback

import requests
from flask import render_template, Blueprint

from detector.config import *
from detector.utils import agents

dashboard = Blueprint("dashboard", __name__, template_folder="templates")


@dashboard.route("/")
@dashboard.route("/dashboard")
def dashboard_page():
    monitoring_status = False
    inspecting_status = 0
    try:
        response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/daemon/status", timeout=2)
        if response.status_code != 200:
            return render_template("error/daemon_not_detected.html")

        nodes = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/daemon/agents")
        if nodes.status_code != 200:
            raise Exception

        config = json.loads(response.content.decode())
        nodes = json.loads(nodes.content.decode())

        if config is not None:
            monitoring_status = True

        ids_config = list()
        if agents and agents[0].ids_config:
            ids_config += agents[0].ids_config
            inspecting_status = len(ids_config)
        return render_template("dashboard.html", is_dashboard=True, nodes=nodes, config=config, monitoring_status=monitoring_status, inspecting_status=inspecting_status, ids_config=ids_config)
    except Exception:
        return render_template("error/daemon_not_detected.html")


@dashboard.route("/alarms")
def alarms_page():
    return render_template("alarms.html")


@dashboard.route("/resources")
def resources_page():
    try:
        response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/daemon/status", timeout=2)
        if response.status_code != 200:
            return render_template("error/daemon_not_detected.html")

        pods = list()
        services = list()
        deployments = list()

        namespaces = json.loads(
            requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/namespaces").content.decode())
        nodes = json.loads(requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/nodes").content.decode())
        for namespace in namespaces:
            pods += json.loads(requests.get(
                "http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/pods?namespace=" + namespace["metadata"][
                    "name"]).content.decode())
            services += json.loads(requests.get(
                "http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/services?namespace=" + namespace["metadata"][
                    "name"]).content.decode())
            deployments += json.loads(requests.get(
                "http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/deployments?namespace=" + namespace["metadata"][
                    "name"]).content.decode())

        # Return the complete resources list
        return render_template("resources.html", pods=pods, services=services, deployments=deployments,
                               namespaces=namespaces, nodes=nodes)
    except Exception:
        return render_template("error/daemon_not_detected.html")


@dashboard.route("/help")
def help_page():
    algorithms = json.loads(
        requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/algorithms").content.decode())
    return render_template("help.html", algorithms=algorithms)
