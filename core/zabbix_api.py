import requests

class ZabbixAPI:
    def __init__(self, url, username, password):
        self.url = url.rstrip("/") + "/api_jsonrpc.php"
        self.username = username
        self.password = password

        self.auth = None
        self.id = 0


    def login(self):
        result = self.call(
            "user.login",
            {
                "username": self.username,
                "password": self.password
            },
            auth=None
        )

        self.auth = result

    def call(self, method, params=None, auth=True):
        self.id += 1

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.id
        }

        if auth is None:
            payload["auth"] = None
        elif auth:
            payload["auth"] = self.auth

        response = requests.post(self.url, json=payload)

        data = response.json()

        if "error" in data:
            raise Exception(data["error"])

        return data["result"]