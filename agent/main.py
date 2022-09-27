import subprocess

from flask import Flask, request

from detector.config import AGENT_PORT

app = Flask(__name__)
p1 = None
p2 = None


@app.route('/', methods=["GET"])
def index():
    return "Monitoring Agent is running", 200


@app.route("/start", methods=["POST"])
def start():
    global p1, p2

    # Retrieve info from POST body
    data = request.get_json()

    sysdig_args = data["sysdig_args"]
    sysdig_format = "\"" + data["sysdig_format"] + "\""
    ws_port = data["ws_port"]
    ws_max_size = data["ws_max_size"]
    window_size = data["syscalls_window"]  # Sends batches of system calls every x seconds
    syscalls_compression = data["syscalls_compression"]

    if p1 is None and p2 is None:
        p1 = subprocess.Popen(
            ('sysdig', '-p', sysdig_format, sysdig_args, "--unbuffered"),
            stdout=subprocess.PIPE)
        p2 = subprocess.Popen(('python3', 'agent/ws_server.py', str(ws_port), str(ws_max_size), str(window_size), str(syscalls_compression)), stdin=p1.stdout)
        return "Started the monitoring agents successfully", 200
    return "Failed to start the monitoring agents", 500


@app.route("/stop", methods=["POST"])
def stop():
    global p1, p2
    if p1:
        p1.terminate()
        p1 = None
    if p2:
        p2.terminate()
        p2 = None
    return "Stopped monitoring agents successfully", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=AGENT_PORT, debug=True)
