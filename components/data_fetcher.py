import httpx
from api_client import api_client, BASE_URL


def get_dashboard_stats():
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/stats",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def get_occupation_par_bloc():
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/occupation-par-bloc",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None
    
def get_evolution_7_jours():
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/evolution-7-jours",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None
    
def get_caveaux():
    try:
        response = httpx.get(
            f"{BASE_URL}/caveaux/",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        print(f"🔍 get_caveaux status: {response.status_code}")
        print(f"🔍 get_caveaux response: {response.text[:200]}")
        return response.json()
    except Exception as e:
        print(f"❌ get_caveaux erreur: {e}")
        return None
    


def get_blocs():
    try:
        response = httpx.get(
            f"{BASE_URL}/caveaux/blocs",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def create_caveau(data: dict):
    try:
        response = httpx.post(
            f"{BASE_URL}/caveaux/",
            json=data,
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_caveau(caveau_id: int, data: dict):
    try:
        response = httpx.patch(
            f"{BASE_URL}/caveaux/{caveau_id}",
            json=data,
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def delete_caveau(caveau_id: int):
    try:
        response = httpx.delete(
            f"{BASE_URL}/caveaux/{caveau_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
    

def get_all_reservations():
    try:
        response = httpx.get(
            f"{BASE_URL}/reservations/admin",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def validate_reservation(reservation_id: int):
    try:
        response = httpx.post(
            f"{BASE_URL}/reservations/validate/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def reject_reservation(reservation_id: int):
    try:
        response = httpx.post(
            f"{BASE_URL}/reservations/reject/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_reservation_by_id(reservation_id: int):
    try:
        response = httpx.get(
            f"{BASE_URL}/reservations/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_reservation_audit(reservation_id: int):
    try:
        response = httpx.get(
            f"{BASE_URL}/reservations/audit/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None
    

def get_all_paiements():
    try:
        response = httpx.get(
            f"{BASE_URL}/finances/admin",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def validate_paiement(paiement_id: int):
    try:
        response = httpx.post(
            f"{BASE_URL}/finances/validate/{paiement_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def reject_paiement(paiement_id: int):
    try:
        response = httpx.post(
            f"{BASE_URL}/finances/reject/{paiement_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_historique_paiements(reservation_id: int):
    try:
        response = httpx.get(
            f"{BASE_URL}/finances/historique/{reservation_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None
    

def get_all_concessions():
    try:
        response = httpx.get(
            f"{BASE_URL}/concessions/",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def create_concession(data: dict):
    try:
        response = httpx.post(
            f"{BASE_URL}/concessions/",
            json=data,
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def renouveler_concession(concession_id: int, nouvelle_date_fin: str):
    try:
        response = httpx.post(
            f"{BASE_URL}/concessions/renouveler/{concession_id}",
            params={"nouvelle_date_fin": nouvelle_date_fin},
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def resilier_concession(concession_id: int):
    try:
        response = httpx.post(
            f"{BASE_URL}/concessions/resilier/{concession_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_all_exhumations():
    try:
        response = httpx.get(
            f"{BASE_URL}/exhumations/",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def approuver_exhumation(exhumation_id: int, observations: str = "", date_exhumation: str = None):
    try:
        payload = {"observations": observations}
        if date_exhumation:
            payload["date_exhumation"] = date_exhumation
        response = httpx.post(
            f"{BASE_URL}/exhumations/approuver/{exhumation_id}",
            json=payload,
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def refuser_exhumation(exhumation_id: int):
    try:
        response = httpx.post(
            f"{BASE_URL}/exhumations/refuser/{exhumation_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def marquer_exhumation_effectuee(exhumation_id: int):
    try:
        response = httpx.post(
            f"{BASE_URL}/exhumations/effectuee/{exhumation_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_exhumation_by_id(exhumation_id: int):
    try:
        response = httpx.get(
            f"{BASE_URL}/exhumations/{exhumation_id}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_occupation_par_bloc():
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/occupation-par-bloc",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def get_revenus_par_canal():
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/revenus-par-canal",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def download_export(export_type: str):
    """export_type: 'csv' ou 'excel'"""
    try:
        response = httpx.get(
            f"{BASE_URL}/dashboard/export-{export_type}",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.content
    except Exception:
        return None
    
def get_all_users():
    try:
        response = httpx.get(
            f"{BASE_URL}/users/",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def update_user_role(user_id: int, role: str):
    try:
        response = httpx.patch(
            f"{BASE_URL}/users/{user_id}/role",
            params={"role": role},
            headers=api_client.get_headers(),
            timeout=30.0
        )
        print(f"update_user_role status: {response.status_code}")
        print(f"update_user_role response: {response.text}")
        return response.json()
    except Exception as e:
        print(f"update_user_role erreur: {e}")
        return {"success": False, "message": str(e)}

def toggle_user_active(user_id: int):
    try:
        response = httpx.patch(
            f"{BASE_URL}/users/{user_id}/toggle-active",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_caveaux_disponibles():
    try:
        response = httpx.get(
            f"{BASE_URL}/caveaux/",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        data = response.json()
        if isinstance(data, list):
            return [c for c in data if c.get("statut") == "DISPONIBLE"]
        return []
    except Exception:
        return None


def get_mes_reservations():
    try:
        response = httpx.get(
            f"{BASE_URL}/reservations/mes-reservations",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def create_reservation_client(data: dict):
    try:
        response = httpx.post(
            f"{BASE_URL}/reservations/",
            json=data,
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_mes_paiements():
    try:
        response = httpx.get(
            f"{BASE_URL}/finances/mes-paiements",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None
    
def create_paiement_client(data: dict):
    try:
        response = httpx.post(
            f"{BASE_URL}/finances/",
            json=data,
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_my_profile():
    try:
        response = httpx.get(
            f"{BASE_URL}/users/me",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def update_my_profile(data: dict):
    try:
        response = httpx.patch(
            f"{BASE_URL}/users/me",
            json=data,
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_mes_exhumations():
    try:
        response = httpx.get(
            f"{BASE_URL}/exhumations/",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None


def create_exhumation_client(data: dict):
    try:
        response = httpx.post(
            f"{BASE_URL}/exhumations/",
            json=data,
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_pending_pick():
    try:
        response = httpx.get(
            f"{BASE_URL}/users/pending-pick",
            headers=api_client.get_headers(),
            timeout=60.0
        )
        return response.json()
    except Exception:
        return None
    

def get_sections():
    try:
        response = httpx.get(
            f"{BASE_URL}/caveaux/sections",
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception:
        return None

def create_section(data: dict):
    try:
        response = httpx.post(
            f"{BASE_URL}/caveaux/sections",
            params=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_bloc(data: dict):
    try:
        response = httpx.post(
            f"{BASE_URL}/caveaux/blocs",
            params=data,
            headers=api_client.get_headers(),
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}