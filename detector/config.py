import os
from pathlib import Path

DETECTOR_IP = os.environ.get('DETECTOR_IP', "0.0.0.0")
DETECTOR_PORT = os.environ.get('DETECTOR_PORT', 5001)

DAEMON_IP = os.environ.get('DAEMON_IP', "127.0.0.1")
DAEMON_PORT = os.environ.get('DAEMON_PORT', 9001)

AGENT_PORT = os.environ.get('AGENT_PORT', 9002)

KUBE_PROXY_IP = os.environ.get('KUBE_PROXY_IP', "127.0.0.1")
KUBE_PROXY_PORT = os.environ.get('KUBE_PROXY_PORT', 8001)

REDIS_IP = os.environ.get('REDIS_IP', "127.0.0.1")
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_MAX_BATCH = os.environ.get('REDIS_MAX_BATCH', 10)

WS_PORT = os.environ.get('WS_PORT', 9003)
WS_MAX_SIZE = os.environ.get('WS_MAX_SIZE', 1073741824)

# Algorithms
ALGORITHMS_FILE = os.environ.get('ALGORITHMS_FILE', "detector/algorithms/algorithms.json")

REQUESTS_TOKEN_FILE = os.environ.get('REQUESTS_TOKEN_FILE', None)
REQUESTS_TOKEN = Path(REQUESTS_TOKEN_FILE).read_text() if REQUESTS_TOKEN_FILE is not None else None
