# api_client.py
import httpx
from typing import Optional, Dict, Any
import os
BASE_URL = "https://cimetiere-backend-v2-production.up.railway.app/api"



class APIClient:
    """Client API pour communiquer avec le backend."""
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user: Optional[Dict[str, Any]] = None

    def register(self, username: str, email: str, password: str, telephone: str = "") -> Dict[str, Any]:
        """Inscription d'un nouvel utilisateur."""
        response = httpx.post(
            f"{BASE_URL}/users/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "telephone": telephone
            },
            timeout=30.0
        )
        return response.json()
    
    def login(self, email: str, password: str):
        try:
            response = httpx.post(
                f"{self.base_url}/users/login",
                json={"email": email, "password": password},
                timeout=30.0
            )
                        
            print(f"Status: {response.status_code}")
            print(f"Content: {response.text[:200]}")
            
            return response.json()
        except httpx.JSONDecodeError as e:
            print(f"Erreur JSON: {e}")
            return {
                "success": False,
                "message": f"Erreur de réponse du serveur (status {response.status_code})"
            }
        except Exception as e:
            print(f"Erreur: {e}")
            return {"success": False, "message": str(e)}

    def verify_mfa(self, email: str, code: str) -> Dict[str, Any]:
        """Vérification du code MFA."""
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

    def get_headers(self) -> Dict[str, str]:
        """Récupère les headers d'authentification."""
        return {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}

    def get_me(self) -> Dict[str, Any]:
        """Récupère le profil de l'utilisateur connecté."""
        response = httpx.get(
            f"{BASE_URL}/users/me",
            headers=self.get_headers(),
            timeout=30.0
        )
        return response.json()


api_client = APIClient()