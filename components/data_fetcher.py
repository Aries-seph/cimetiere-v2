# components/data_fetcher.py
import httpx
from api_client import api_client, BASE_URL


# ============ CAVEAUX ============

def get_caveaux():
    try:
        response = httpx.get(
            f"{BASE_URL}/caveaux/",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return None

def get_caveaux_disponibles():
    """Récupère la liste des caveaux disponibles."""
    try:
        response = httpx.get(
            f"{BASE_URL}/caveaux/",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        data = response.json()
        if isinstance(data, list):
            return [c for c in data if c.get("statut") == "DISPONIBLE"]
        return []
    except Exception:
        return []
    
def get_blocs():
    """Récupère la liste de tous les blocs avec leur section."""
    try:
        response = httpx.get(
            f"{BASE_URL}/caveaux/blocs",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        data = response.json()
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def create_caveau(data: dict):
    try:
        response = httpx.post(
            f"{BASE_URL}/caveaux/",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {"success": False, "message": "Erreur de connexion"}


def update_caveau(caveau_id: int, data: dict):
    try:
        response = httpx.patch(
            f"{BASE_URL}/caveaux/{caveau_id}",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {"success": False, "message": "Erreur de connexion"}


def delete_caveau(caveau_id: int):
    try:
        response = httpx.delete(
            f"{BASE_URL}/caveaux/{caveau_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {"success": False, "message": "Erreur de connexion"}


# ============ SECTIONS ============
def get_sections():
    """Récupère la liste de toutes les sections."""
    try:
        response = httpx.get(
            f"{BASE_URL}/caveaux/sections",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        data = response.json()
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def create_section(data: dict):
    """Crée une nouvelle section."""
    try:
        response = httpx.post(
            f"{BASE_URL}/caveaux/sections",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        if response.status_code in [200, 201]:
            try:
                return response.json()
            except Exception as json_err:
                print(f"🔴 Le serveur n'a pas renvoyé de JSON valide : {json_err}")
                print(f"🔴 Contenu reçu : {response.text}")
                return {"success": False, "message": f"Erreur serveur (HTML reçu) : {response.text[:100]}"}
        else:
            return {"success": False, "message": f"Erreur {response.status_code} : {response.text[:200]}"}
    except Exception as e:
        print(f"infos {e}")


def delete_section(section_id: int):
    """Supprime une section."""
    try:
        response = httpx.delete(
            f"{BASE_URL}/caveaux/sections/{section_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {"success": False, "message": "Erreur de connexion"}


# ============ BLOCS ============
def create_bloc(data: dict):
    """Crée un nouveau bloc."""
    try:
        response = httpx.post(
            f"{BASE_URL}/caveaux/blocs",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {"success": False, "message": "Erreur de connexion"}


def delete_bloc(bloc_id: int):
    """Supprime un bloc."""
    try:
        response = httpx.delete(
            f"{BASE_URL}/caveaux/blocs/{bloc_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {"success": False, "message": "Erreur de connexion"}


# ============ RÉSERVATIONS ============
def get_all_reservations():
    """Récupère toutes les réservations (admin)."""
    try:
        response = httpx.get(
            f"{BASE_URL}/reservations/admin",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def get_mes_reservations():
    """Récupère les réservations de l'utilisateur connecté."""
    try:
        response = httpx.get(
            f"{BASE_URL}/reservations/mes-reservations",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def create_reservation_client(data: dict):
    """Crée une réservation pour le client."""
    try:
        response = httpx.post(
            f"{BASE_URL}/reservations/",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def validate_reservation(reservation_id: int):
    """Valide une réservation."""
    try:
        response = httpx.post(
            f"{BASE_URL}/reservations/validate/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def reject_reservation(reservation_id: int):
    """Refuse une réservation."""
    try:
        response = httpx.post(
            f"{BASE_URL}/reservations/reject/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def get_reservation_by_id(reservation_id: int):
    """Récupère une réservation par ID."""
    try:
        response = httpx.get(
            f"{BASE_URL}/reservations/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def get_reservation_audit(reservation_id: int):
    """Récupère l'historique d'une réservation."""
    try:
        response = httpx.get(
            f"{BASE_URL}/reservations/audit/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


# ============ PAIEMENTS ============
def get_all_paiements():
    """Récupère tous les paiements (admin)."""
    try:
        response = httpx.get(
            f"{BASE_URL}/finances/admin",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def get_mes_paiements():
    """Récupère les paiements de l'utilisateur."""
    try:
        response = httpx.get(
            f"{BASE_URL}/finances/mes-paiements",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def create_paiement_client(data: dict):
    """Crée un paiement pour le client."""
    try:
        response = httpx.post(
            f"{BASE_URL}/finances/",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def validate_paiement(paiement_id: int):
    """Valide un paiement."""
    try:
        response = httpx.post(
            f"{BASE_URL}/finances/validate/{paiement_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def reject_paiement(paiement_id: int):
    """Refuse un paiement."""
    try:
        response = httpx.post(
            f"{BASE_URL}/finances/reject/{paiement_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def get_historique_paiements(reservation_id: int):
    """Récupère l'historique des paiements d'une réservation."""
    try:
        response = httpx.get(
            f"{BASE_URL}/finances/historique/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return None
    

def get_all_paiements(sort_by="-created_at"):
    """Récupère tous les paiements avec tri."""
    try:
        response = httpx.get(
            f"{BASE_URL}/finances/admin?sort={sort_by}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return None


# ============ CONCESSIONS ============
def get_all_concessions():
    """Récupère toutes les concessions."""
    try:
        response = httpx.get(
            f"{BASE_URL}/concessions/",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def create_concession(data: dict):
    """Crée une nouvelle concession."""
    try:
        response = httpx.post(
            f"{BASE_URL}/concessions/",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def renouveler_concession(concession_id: int, nouvelle_date_fin: str):
    """Renouvelle une concession temporaire."""
    try:
        response = httpx.post(
            f"{BASE_URL}/concessions/renouveler/{concession_id}",
            params={"nouvelle_date_fin": nouvelle_date_fin},
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def resilier_concession(concession_id: int):
    """Résilie une concession."""
    try:
        response = httpx.post(
            f"{BASE_URL}/concessions/resilier/{concession_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


# ============ EXHUMATIONS ============
def get_all_exhumations():
    """Récupère toutes les exhumations."""
    try:
        response = httpx.get(
            f"{BASE_URL}/exhumations/",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def get_mes_exhumations():
    """Récupère les exhumations de l'utilisateur."""
    try:
        response = httpx.get(
            f"{BASE_URL}/exhumations/",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def create_exhumation_client(data: dict):
    """Crée une demande d'exhumation."""
    try:
        response = httpx.post(
            f"{BASE_URL}/exhumations/",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def approuver_exhumation(exhumation_id: int, observations: str = "", date_exhumation: str = None):
    """Approuve une exhumation."""
    try:
        payload = {"observations": observations}
        if date_exhumation:
            payload["date_exhumation"] = date_exhumation
        response = httpx.post(
            f"{BASE_URL}/exhumations/approuver/{exhumation_id}",
            json=payload,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def refuser_exhumation(exhumation_id: int):
    """Refuse une exhumation."""
    try:
        response = httpx.post(
            f"{BASE_URL}/exhumations/refuser/{exhumation_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def marquer_exhumation_effectuee(exhumation_id: int):
    """Marque une exhumation comme effectuée."""
    try:
        response = httpx.post(
            f"{BASE_URL}/exhumations/effectuee/{exhumation_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def get_exhumation_by_id(exhumation_id: int):
    """Récupère une exhumation par ID."""
    try:
        response = httpx.get(
            f"{BASE_URL}/exhumations/{exhumation_id}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


# ============ DASHBOARD ============
def get_dashboard_stats():
    """Récupère les statistiques du dashboard."""
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/stats",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {}


def get_evolution_7_jours():
    """Récupère l'évolution des revenus sur 7 jours."""
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/evolution-7-jours",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def get_occupation_par_bloc():
    """Récupère l'occupation par bloc."""
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/occupation-par-bloc",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def get_revenus_par_canal():
    """Récupère les revenus par canal de paiement."""
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/revenus-par-canal",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def download_export(export_type: str):
    """Télécharge un export (csv ou excel)."""
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/export-{export_type}",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.content
    except Exception:
        return None


# ============ UTILISATEURS ============
def get_all_users():
    """Récupère tous les utilisateurs."""
    try:
        response = httpx.get(
            f"{BASE_URL}/users/",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return []


def update_user_role(user_id: int, role: str):
    """Met à jour le rôle d'un utilisateur."""
    try:
        response = httpx.patch(
            f"{BASE_URL}/users/{user_id}/role",
            params={"role": role},
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


def toggle_user_active(user_id: int):
    """Active/désactive un utilisateur."""
    try:
        response = httpx.patch(
            f"{BASE_URL}/users/{user_id}/toggle-active",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


# ============ PROFIL ============
def get_my_profile():
    """Récupère le profil de l'utilisateur connecté."""
    try:
        response = httpx.get(
            f"{BASE_URL}/users/me",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {}


def update_my_profile(data: dict):
    """Met à jour le profil de l'utilisateur connecté."""
    try:
        response = httpx.patch(
            f"{BASE_URL}/users/me",
            json=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Erreur: {str(e)}"}


# ============ SÉLECTION SUR LA CARTE ============
def get_pending_pick():
    """Récupère les coordonnées en attente de sélection."""
    try:
        response = httpx.get(
            f"{BASE_URL}/users/pending-pick",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return {"has_pick": False}