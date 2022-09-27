import base64
from random import choice
from locust import HttpUser, TaskSet, task, LoadTestShape, constant


class WebsiteUser(HttpUser):
    
    @task
    def load(self):
        #base64string = base64.b64encode('%s:%s'.encode() % ('user'.encode(), 'password'.encode())).replace('\n'.encode(), ''.encode())
        base64string = base64.b64encode("user:password".encode("ascii")) # -> dXNlcjpwYXNzd29yZA==

        catalogue = self.client.get("/catalogue").json()
        category_item = choice(catalogue)
        item_id = category_item["id"] # 03fef6ac-1896-4ce8-bd69-b798f85c6e0b

        self.client.get("/")
        self.client.get("/login", headers={"Authorization": "Basic dXNlcjpwYXNzd29yZA=="})
        self.client.get("/category.html")
        self.client.get("/detail.html?id={}".format(item_id))
