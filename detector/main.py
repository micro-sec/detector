import signal
import logging
import sys

from flask import Flask

from detector import dashboard, api
from detector.config import DETECTOR_IP, DETECTOR_PORT
from detector.utils import reset_redis_keys, sigint_handler

if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger(__name__)
    log.info("Started the detector component")
    signal.signal(signal.SIGINT, sigint_handler)
    reset_redis_keys()

    app = Flask(__name__, template_folder="template")
    app.register_blueprint(dashboard.dashboard)
    app.register_blueprint(api.api)

    # from waitress import serve
    # serve(app, host=DETECTOR_IP, port=DETECTOR_PORT)
    app.run(host=DETECTOR_IP, port=DETECTOR_PORT, debug=True)
