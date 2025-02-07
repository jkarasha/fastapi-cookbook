from locust import HttpUser, task

class ProtoAppUser(HttpUser):
    host = "http://localhost:8000"

    @task
    def read_main(self):
        self.client.get("/home")