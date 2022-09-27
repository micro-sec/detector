import base64
import csv
import sys
from random import choice
from locust import HttpUser, task, LoadTestShape

LOAD_FILE = "30min_variable_load.csv"
try:
    with open(LOAD_FILE, "r") as file:
        load = list(csv.reader(file, delimiter=","))
except Exception:
    print("Failed to load file.")
    sys.exit(-1)


class WebsiteUser(HttpUser):

    @task
    def load(self):
        # base64string = base64.b64encode('%s:%s'.encode() % ('user'.encode(), 'password'.encode())).replace('\n'.encode(), ''.encode())
        base64string = base64.b64encode("user:password".encode("ascii"))  # -> dXNlcjpwYXNzd29yZA==

        catalogue = self.client.get("/catalogue").json()
        category_item = choice(catalogue)
        item_id = category_item["id"]  # 03fef6ac-1896-4ce8-bd69-b798f85c6e0b

        self.client.get("/")
        self.client.get("/login", headers={"Authorization": "Basic dXNlcjpwYXNzd29yZA=="})
        self.client.get("/category.html")
        self.client.get("/detail.html?id={}".format(item_id))


class Shape(LoadTestShape):
    time_limit = len(load)
    spawn_rate = 1

    def tick(self):
        run_time = round(self.get_run_time())
        if run_time < self.time_limit:
            user_count = int(float(load[run_time][1]))
            return round(user_count), self.spawn_rate
        else:
            return None