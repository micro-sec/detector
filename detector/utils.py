import asyncio
import json
import logging
import os
import pickle
import subprocess
import sys
import traceback
from multiprocessing import Process
from time import time, ctime, sleep

import blosc2
import redis
import requests
import websockets
from jsonschema import validate

from detector.classes import IntrusionDetectionConfig, Agent
from detector.config import *

redis_connection = redis.Redis(host=REDIS_IP, port=REDIS_PORT, db=0)
agents = list()
sysdig_format = str()

schema_monitoring = {
    "type": "object",
    "required": ["sysdig_args", "sysdig_format", "syscalls_window", "syscalls_compression"],
    "properties": {
        "sysdig_args": {"type": "string"},
        "sysdig_format": {"type": "string"},
        "syscalls_window": {"type": "number"},
        "syscalls_compression": {"type": "string", "enum": ["true", "false"]},
    },
}

schema_inspecting = {
    "type": "object",
    "required": ["type", "algorithm", "duration"],
    "properties": {
        "type": {"type": "string"},
        "algorithm": {"type": "string"},
        "duration": {"type": "number"}
    },
}


def reset_redis_keys():
    # Batches of system calls
    for key in redis_connection.scan_iter(match="batch-*"):
        redis_connection.delete(key)

    for key in redis_connection.scan_iter(match="classifier-*"):
        redis_connection.delete(key)

    # Monitoring Statistics
    redis_connection.set("monitoring_total_syscalls", 0)
    redis_connection.set("monitoring_total_size", 0)
    redis_connection.set("monitoring_total_batches", 0)
    redis_connection.set("monitoring_batch_length", 0)

    # List of alarms generated
    redis_connection.set("alarms", json.dumps({
        "total": 0,
        "totalNotFiltered": 0,
        "rows": []
    }))
    logging.info("Redis keys were reset")


def add_alarm(description):
    alarms = json.loads(redis_connection.get("alarms"))
    alarms["total"] += 1
    alarms["totalNotFiltered"] += 1
    alarms["rows"].append({
        "description": description,
        "timestamp": ctime(time())
    })
    redis_connection.set("alarms", json.dumps(alarms))
    # print("Alarm generated (total_alarms: " + str(alarms["total"]) + ")")


def get_classifier(algorithm, node_ip_address):
    return pickle.loads(redis_connection.get("classifier-" + algorithm + node_ip_address))


def set_classifier(algorithm, node_ip_address, data):
    return redis_connection.set("classifier-" + algorithm + node_ip_address, pickle.dumps(data))


def get_batch(host_ip):
    return redis_connection.lpop("batch-" + host_ip)


async def syscall_transfer(agent):
    while True:
        try: # retry in case the agent is not ready
            async with websockets.connect("ws://" + agent.ip_address + ":" + str(agent.ws_port),
                                        max_size=agent.ws_max_size, ping_interval=None) as websocket:
                try:
                    print("Receiving system calls from node \"" + agent.name + "\" (" + agent.ip_address + ")")
                    async for data in websocket:
                        # Handle the system calls received
                        if agent.syscalls_compression == "true":
                            decompressed_pickle = blosc2.decompress(data)
                            batch = pickle.loads(decompressed_pickle)
                        else:
                            batch = pickle.loads(data)

                        batch_length = len(batch)

                        # Store batch in redis (push to queue)
                        redis_connection.rpush("batch-" + agent.ip_address, decompressed_pickle)

                        # Limit the number of batches to REDIS_MAX_BATCH
                        redis_connection.ltrim("batch-" + agent.ip_address, - int(REDIS_MAX_BATCH), -1)

                        print("Received batch from " + agent.ip_address + " containing " + str(
                            batch_length) + " system calls with a size of " + str(
                            sys.getsizeof(data)) + " bytes")

                        # Store stats in redis
                        redis_connection.incrby("monitoring_total_syscalls", batch_length)
                        redis_connection.incrby("monitoring_total_size", sys.getsizeof(data))
                        redis_connection.incrby("monitoring_total_batches", 1)
                        redis_connection.set("monitoring_batch_length", batch_length)
                except (KeyboardInterrupt, Exception):
                    # traceback.print_exc()
                    stop_monitoring()
                    os._exit(1)
        except:
            pass


def ws_client(agent):
    asyncio.run(syscall_transfer(agent))


def duration_handler(duration, identifier):
    try:
        sleep(duration)
        requests.post("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/inspecting/stop?id=" + identifier)
    except Exception:
        return


def verify_algorithm(algorithm):
    with open(r"" + ALGORITHMS_FILE) as file:
        for item in json.load(file):
            if algorithm == item["name"]:
                return
    raise Exception


def start_monitoring(data):
    global agents, sysdig_format
    try:
        # Validate data
        validate(instance=data, schema=schema_monitoring)

        # Send POST request "/start" to Daemon
        response = requests.post("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/start", json=data)

        if response.status_code == 200:
            # Reset redis keys
            reset_redis_keys()

            # Start the websocket client for every node returned in the response
            nodes = response.json()["nodes"]
            for node in nodes:
                if node["agent"] == "true":
                    # Create Agent
                    agent = Agent(node["name"], node["ip_address"])
                    agent.ws_port = data["ws_port"]
                    agent.ws_max_size = data["ws_max_size"]
                    agent.syscalls_compression = data["syscalls_compression"]

                    sysdig_format = data["sysdig_format"]

                    # Start the ws_client_thread
                    p = Process(target=ws_client, args=(agent,))
                    p.start()

                    # Associate ws_client_thread to Agent
                    agent.ws_client_thread = p

                    # Add Agent to agents list
                    agents.append(agent)
        return response.json()["message"], response.status_code
    except Exception:
        traceback.print_exc()


def stop_monitoring():
    global agents, sysdig_format
    try:
        # Send POST request "/stop" to Daemon
        response = requests.post("http://" + DAEMON_IP + ":" + str(DAEMON_PORT) + "/stop")

        # Kill all child processes and threads spawned
        if response.status_code != 200:
            raise Exception

        for agent in agents:
            agent.stop_monitoring()
        agents.clear()

        sysdig_format = str()

        # Reset redis keys
        reset_redis_keys()

        return response.content.decode(), response.status_code
    except Exception:
        traceback.print_exc()


def start_inspecting(data):
    global agents
    try:
        # Validate data and verify if algorithm exists
        validate(instance=data, schema=schema_inspecting)
        verify_algorithm(data["algorithm"])

        identifier = str(data["type"]) + str(data["algorithm"]) + str(data["start_time_timestamp"])

        # Run the algorithm in each agent
        for agent in agents:
            ids_process = subprocess.Popen(
                ("python3", "detector/algorithms/" + data["algorithm"].lower() + ".py", agent.name,
                 agent.ip_address, data["type"], identifier, sysdig_format))

            # Start the thread that will stop inspecting the system calls after a predefined duration
            duration_thread = None
            if data["duration"] > 0:
                duration_thread = Process(target=duration_handler, args=(data["duration"], identifier))
                duration_thread.start()

            agent.ids_config.append(
                IntrusionDetectionConfig(identifier, data["type"], data["algorithm"], data["duration"],
                                         data["start_time"],
                                         data["start_time_timestamp"], ids_process, duration_thread))
        return "Started inspecting the system calls successfully", 200
    except Exception:
        traceback.print_exc()
        return "Failed to start inspecting the system calls", 500


def stop_inspecting(identifier=None):
    global agents
    try:
        for agent in agents:
            if identifier is None:
                agent.stop_inspecting()
            else:
                agent.stop_inspecting(identifier)
        return "Stopped inspecting the system calls successfully", 200
    except Exception:
        traceback.print_exc()
        return "Failed to stop inspecting the system calls", 500


def sigint_handler(signum, frame):
    stop_monitoring()
    sys.exit()
