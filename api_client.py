import httpx
import os

# En production : variable d'environnement BACKEND_URL
# En local : http://127.0.0.1:8000/api
BASE_URL = os.getenv('BACKEND_URL', 'https://cimetiere-backend-production.up.railway.app')


class APIClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.user = None

    def register(self, username: str, email: str, password: str, telephone: str = ""):
        response = httpx.post(f"{BASE_URL}/users/register", json={
            "username": username,
            "email": email,
            "password": password,
            "telephone": telephone
        }, timeout=30.0)
        return response.json()

    def login(self, email: str, password: str):
        response = httpx.post(
            f"{BASE_URL}/users/login/",
            json={"email": email, "password": password},
            timeout=30.0
        )
        return response.json()

    def verify_mfa(self, email: str, code: str):
        response = httpx.post(
            f"{BASE_URL}/users/verify-mfa",
            json={"email": email, "code": code},
            timeout=30.0
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
        response = httpx.get(
            f"{BASE_URL}/users/me",
            headers=self.get_headers(),
            timeout=30.0
        )
        return response.json()


api_client = APIClient()
