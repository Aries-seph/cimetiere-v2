import flet as ft
from pages.login_page import login_page
from pages.mfa_page import mfa_page
from pages.register_page import register_page
from pages.admin_dashboard import admin_dashboard
from pages.caveaux_page import caveaux_page
from pages.reservations_page import reservations_page
from pages.paiements_page import paiements_page
from pages.concessions_page import concessions_page
from pages.exhumations_page import exhumations_page
from pages.rapports_page import rapports_page
from pages.utilisateurs_page import utilisateurs_page
from pages.client_dashboard import client_dashboard
from pages.client_reserver_page import client_reserver_page
from pages.client_reservations_page import client_reservations_page
from pages.client_paiements_page import client_paiements_page
from pages.client_profil_page import client_profil_page
from pages.client_exhumations_page import client_exhumations_page
from pages.client_carte_page import client_carte_page
from theme import COLOR_BG
from api_client import api_client
from urllib.parse import urlparse, parse_qs
import os

TOKEN_KEY = "cimetiere.access_token"
REFRESH_KEY = "cimetiere.refresh_token"
ROLE_KEY = "cimetiere.user_role"
EMAIL_KEY = "cimetiere.user_email"


async def main(page: ft.Page):
    page.title = "Gestion de Cimetière"
    page.bgcolor = COLOR_BG
    page.padding = 0

    current_view = {"name": "login", "used_preselect": False}

    # --- Lecture des paramètres URL ---
    parsed_route = urlparse(page.route or "/")
    qs = parse_qs(parsed_route.query)
    preselect_caveau_id = qs.get("caveau_id", [None])[0]

    # Variables pick (GPS depuis carte admin)
    pick_lat = None
    pick_lng = None
    pick_caveau_id = None

    # --- Session ---
    async def persist_session():
        await page.shared_preferences.set(TOKEN_KEY, api_client.access_token or "")
        await page.shared_preferences.set(REFRESH_KEY, api_client.refresh_token or "")
        if api_client.user:
            await page.shared_preferences.set(ROLE_KEY, api_client.user.get("role", ""))
            await page.shared_preferences.set(EMAIL_KEY, api_client.user.get("email", ""))

    async def clear_session():
        for k in [TOKEN_KEY, REFRESH_KEY, ROLE_KEY, EMAIL_KEY]:
            if await page.shared_preferences.contains_key(k):
                await page.shared_preferences.remove(k)

    async def restore_session():
        """Restaure la session depuis le navigateur. Retourne True si session valide."""
        token = await page.shared_preferences.get(TOKEN_KEY)
        if not token:
            return False
        api_client.access_token = token
        api_client.refresh_token = await page.shared_preferences.get(REFRESH_KEY)
        role = await page.shared_preferences.get(ROLE_KEY)
        email = await page.shared_preferences.get(EMAIL_KEY)
        me = api_client.get_me()
        if me and "detail" not in me:
            api_client.user = {"role": role, "email": email}
            return True
        else:
            await clear_session()
            return False

    # --- Navigation ---
    def show_mfa(email):
        current_view["name"] = "mfa"
        current_view["email"] = email
        render()

    def show_register():
        current_view["name"] = "register"
        render()

    def back_to_login():
        current_view["name"] = "login"
        render()

    async def on_mfa_success():
        role = api_client.user.get("role") if api_client.user else None
        await persist_session()
        if role == "CLIENT":
            if preselect_caveau_id and not current_view["used_preselect"]:
                current_view["name"] = "client_reserver"
            else:
                current_view["name"] = "client_dashboard"
        else:
            current_view["name"] = "dashboard"
        render()

    def on_navigate(route):
        current_view["name"] = route
        render()

    async def on_logout():
        await clear_session()
        api_client.access_token = None
        api_client.refresh_token = None
        api_client.user = None
        current_view["name"] = "login"
        render()

    def render():
        nonlocal pick_lat, pick_lng, pick_caveau_id

        page.controls.clear()
        page.overlay.clear()
        name = current_view["name"]

        if name == "login":
            page.add(login_page(page, show_mfa, show_register))
        elif name == "register":
            page.add(register_page(page, back_to_login, back_to_login))
        elif name == "mfa":
            page.add(mfa_page(page, current_view["email"], on_mfa_success))
        elif name == "dashboard":
            page.add(admin_dashboard(page, on_navigate, on_logout))
        elif name == "caveaux":
            # Consomme les coordonnées pick et remet à None après passage
            plat = pick_lat
            plng = pick_lng
            pcid = pick_caveau_id
            pick_lat = None
            pick_lng = None
            pick_caveau_id = None
            page.add(caveaux_page(page, on_navigate, on_logout,
                                  pick_lat=plat, pick_lng=plng, pick_caveau_id=pcid))
        elif name == "reservations":
            page.add(reservations_page(page, on_navigate, on_logout))
        elif name == "paiements":
            page.add(paiements_page(page, on_navigate, on_logout))
        elif name == "concessions":
            page.add(concessions_page(page, on_navigate, on_logout))
        elif name == "exhumations":
            page.add(exhumations_page(page, on_navigate, on_logout))
        elif name == "rapports":
            page.add(rapports_page(page, on_navigate, on_logout))
        elif name == "utilisateurs":
            page.add(utilisateurs_page(page, on_navigate, on_logout))
        elif name == "client_dashboard":
            page.add(client_dashboard(page, on_navigate, on_logout))
        elif name == "client_reserver":
            cid = preselect_caveau_id if not current_view["used_preselect"] else None
            current_view["used_preselect"] = True
            page.add(client_reserver_page(page, on_navigate, on_logout, preselect_caveau_id=cid))
        elif name == "client_reservations":
            page.add(client_reservations_page(page, on_navigate, on_logout))
        elif name == "client_paiements":
            page.add(client_paiements_page(page, on_navigate, on_logout))
        elif name == "client_profil":
            page.add(client_profil_page(page, on_navigate, on_logout))
        elif name == "client_exhumations":
            page.add(client_exhumations_page(page, on_navigate, on_logout))
        elif name == "client_carte":
            page.add(client_carte_page(page, on_navigate, on_logout))
        else:
            page.add(ft.Text(f"Page '{name}' à venir", color="white"))
        page.update()

    def handle_resize(e):
        render()

    page.on_resize = handle_resize

    # --- Démarrage initial ---
    session_ok = await restore_session()

    if session_ok:
        role = api_client.user.get("role") if api_client.user else None

        # Vérifier si des coordonnées GPS sont en attente (retour depuis carte admin)
        from components.data_fetcher import get_pending_pick
        pick_data = get_pending_pick()

        if pick_data and pick_data.get("has_pick"):
            # L'admin revient de la carte avec des coordonnées → aller directement aux caveaux
            pick_lat = str(pick_data["latitude"])
            pick_lng = str(pick_data["longitude"])
            pick_caveau_id = str(pick_data["caveau_id"]) if pick_data.get("caveau_id") else None
            current_view["name"] = "caveaux"
        elif role == "CLIENT":
            if preselect_caveau_id:
                current_view["name"] = "client_reserver"
            else:
                current_view["name"] = "client_dashboard"
        else:
            current_view["name"] = "dashboard"
    else:
        current_view["name"] = "login"

    render()


port = int(os.getenv('PORT', 8550))
ft.run(main, view=ft.AppView.WEB_BROWSER, port=port)