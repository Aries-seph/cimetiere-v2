import httpx
import os

BASE_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000/api')
print(f"===== BASE_URL = {BASE_URL} =====")


class APIClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.user = None

    def register(self, username: str, email: str, password: str, telephone: str = ""):
        response = httpx.post(f"{BASE_URL}/users/register/", json={
            "username": username,
            "email": email,
            "password": password,
            "telephone": telephone
        }, timeout=60.0)
        return response.json()

    def login(self, email, password):
        response = httpx.post(
            f"{BASE_URL}/users/login/",
            json={"email": email, "password": password},
            timeout=60.0
        )
        if response.status_code != 200:
            print(f"ERREUR BACKEND ({response.status_code}): {response.text}")
            return {"error": True, "message": f"Erreur serveur {response.status_code}"}
        return response.json()

    def verify_mfa(self, email: str, code: str):
        response = httpx.post(
            f"{BASE_URL}/users/verify-mfa/",
            json={"email": email, "code": code},
            timeout=60.0
        )
        data = response.json()
        if data.get("success"):
            self.access_token = data.get("access")
            self.refresh_token = data.get("refresh")
            self.user = data.get("user")
        return data

    def get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_me(self):
        try:
            print(f"===== TOKEN = {self.access_token} =====")
            response = httpx.get(
                f"{BASE_URL}/users/me",
                headers=self.get_headers(),
                timeout=30.0
            )
            print(f"===== get_me status = {response.status_code} =====")
            return response.json()
        except Exception as e:
            print(f"===== get_me erreur = {e} =====")
            return {}


api_client = APIClient()