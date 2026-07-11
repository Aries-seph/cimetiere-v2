# api_client.py
import httpx
import json
from typing import Optional, Dict, Any

BASE_URL = "https://cimetiere-backend-v2-production.up.railway.app/api"

class APIClient:
    """Client API pour communiquer avec le backend."""
    
    def __init__(self):
        self.base_url = BASE_URL  # ← AJOUTER CETTE LIGNE
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user: Optional[Dict[str, Any]] = None

    def register(self, username: str, email: str, password: str, telephone: str = "") -> Dict[str, Any]:
        """Inscription d'un nouvel utilisateur."""
        try:
            response = httpx.post(
                f"{self.base_url}/users/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "telephone": telephone
                },
                timeout=30.0
            )
            return response.json()
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Connexion de l'utilisateur."""
        try:
            response = httpx.post(
                f"{self.base_url}/users/login",
                json={"email": email, "password": password},
                timeout=30.0
            )
            
            # Vérifier le statut
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"Erreur serveur (status {response.status_code})"
                }
            
            # Tenter de parser le JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                print(f"❌ Réponse non-JSON: {response.text[:200]}")
                return {
                    "success": False,
                    "message": "Le serveur a renvoyé une réponse invalide"
                }
                
        except httpx.TimeoutException:
            return {"success": False, "message": "Le serveur ne répond pas (timeout)"}
        except httpx.ConnectError:
            return {"success": False, "message": "Impossible de se connecter au serveur"}
        except Exception as e:
            print(f"❌ Erreur login: {e}")
            return {"success": False, "message": str(e)}

    def verify_mfa(self, email: str, code: str) -> Dict[str, Any]:
        """Vérification du code MFA."""
        try:
            response = httpx.post(
                f"{self.base_url}/users/verify-mfa",
                json={"email": email, "code": code},
                timeout=30.0
            )
            data = response.json()
            if data.get("success"):
                self.access_token = data.get("access")
                self.refresh_token = data.get("refresh")
                self.user = data.get("user")
            return data
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_headers(self) -> Dict[str, str]:
        """Récupère les headers d'authentification."""
        return {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}

    def get_me(self) -> Dict[str, Any]:
        """Récupère le profil de l'utilisateur connecté."""
        try:
            response = httpx.get(
                f"{self.base_url}/users/me",
                headers=self.get_headers(),
                timeout=30.0
            )
            return response.json()
        except Exception as e:
            return {"success": False, "message": str(e)}


# Instance globale du client
api_client = APIClient()