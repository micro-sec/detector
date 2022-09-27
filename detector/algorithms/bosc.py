import pickle
import sys
from collections import Counter

from detector.utils import get_batch, add_alarm, get_classifier, set_classifier

NORMAL = 0
ANOMALY = 1
WINDOW_SIZE = 1


class Bosc:
    def __init__(self, ):
        self.behaviour_db = dict()

    def predict(self, ):
        while True:
            try:
                batch = pickle.loads(get_batch(node_ip_address))

                for i in range(0, len(batch), WINDOW_SIZE):
                    window = batch[i:i + WINDOW_SIZE]
                    window = [i.decode() for i in window]
                    counter = Counter(window)
                    keys = sorted(counter.elements())
                    results = list()
                    for key in keys:
                        temp = str(key) + "," + str(counter[key])
                        results.append(temp)

                    first = "|".join(results)
                    anomaly = False

                    if first not in self.behaviour_db.keys():
                        add_alarm(
                            "Alarm detected in the node \"" + node_name + "\" (" + node_ip_address + ") id=" + identifier + " | " + first)
                        continue

                    cur_dict = self.behaviour_db[first]
                    for j, syscall in enumerate(window[1:]):
                        key = str(syscall.decode())
                        if key not in cur_dict:
                            anomaly = True
                            break
                        cur_dict = cur_dict[key]

                    if anomaly:
                        add_alarm(
                            "Alarm detected in the node \"" + node_name + "\" (" + node_ip_address + ") id=" + identifier + " | " + first)
            except TypeError:
                continue

    def train(self, ):
        while True:
            try:
                batch = pickle.loads(get_batch(node_ip_address))

                # BOSC implementation
                for i in range(0, len(batch), WINDOW_SIZE):
                    window = batch[i:i + WINDOW_SIZE]
                    window = [i.decode() for i in window]
                    counter = Counter(window)
                    keys = sorted(counter.elements())
                    results = list()
                    for key in keys:
                        temp = str(key) + "," + str(counter[key])
                        results.append(temp)

                    first = "|".join(results)

                    if first not in self.behaviour_db.keys():
                        self.behaviour_db[first] = dict()

                    cur_dict = self.behaviour_db[first]
                    for j, syscall in enumerate(window[1:]):
                        key = str(syscall.decode())
                        if key not in cur_dict:
                            cur_dict[key] = dict()
                        cur_dict = cur_dict[key]

                # Save classifier data in redis
                set_classifier(algorithm, node_ip_address, self.behaviour_db)
            except TypeError:
                continue


if __name__ == '__main__':
    algorithm = "bosc"
    node_name = sys.argv[1]
    node_ip_address = sys.argv[2]
    monitoring_type = sys.argv[3]
    identifier = sys.argv[4]
    sysdig_format = sys.argv[5]

    classifier = Bosc()
    if monitoring_type == "training":
        classifier.train()
    elif monitoring_type == "detection":
        try:
            data = get_classifier(algorithm, node_ip_address)
            if data:
                classifier.behaviour_db = data
                classifier.predict()
        except TypeError:
            classifier.predict()
