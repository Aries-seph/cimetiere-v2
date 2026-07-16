# main.py
import flet as ft
from urllib.parse import urlparse, parse_qs
from flet import SharedPreferences

from pages.login_page import login_page
from pages.mfa_page import mfa_page
from pages.register_page import register_page

from pages.dashboard_page import dashboard_page
from pages.caveaux_page import caveaux_page
from pages.reservations_page import reservations_page
from pages.paiements_page import paiements_page
from pages.concessions_page import concessions_page
from pages.exhumations_page import exhumations_page
from pages.rapports_page import rapports_page
from pages.users_page import users_page

from pages.client_dashboard_page import client_dashboard_page
from pages.client_reserver_page import client_reserver_page
from pages.client_reservations_page import client_reservations_page
from pages.client_paiements_page import client_paiements_page
from pages.client_profil_page import client_profil_page
from pages.client_exhumations_page import client_exhumations_page
from pages.client_carte_page import client_carte_page

from theme import COLOR_BG, COLOR_PRIMARY
from api_client import api_client

# Clés de session
TOKEN_KEY = "cimetiere.access_token"
REFRESH_KEY = "cimetiere.refresh_token"
ROLE_KEY = "cimetiere.user_role"
EMAIL_KEY = "cimetiere.user_email"


async def main(page: ft.Page):
    page.title = "Gestion de Cimetière"
    page.bgcolor = COLOR_BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Initialiser SharedPreferences
    pref = SharedPreferences()
    
    # État de l'application
    app_state = {
        "route": "dashboard",
        "params": {},
        "initialized": False,
    }
    
    # --- Gestion de session ---
    async def persist_session():
        await pref.set(TOKEN_KEY, api_client.access_token or "")
        await pref.set(REFRESH_KEY, api_client.refresh_token or "")
        if api_client.user:
            await pref.set(ROLE_KEY, api_client.user.get("role", ""))
            await pref.set(EMAIL_KEY, api_client.user.get("email", ""))

    async def clear_session():
        for k in [TOKEN_KEY, REFRESH_KEY, ROLE_KEY, EMAIL_KEY]:
            if await pref.contains_key(k):
                await pref.remove(k)

    async def restore_session():
        token = await pref.get(TOKEN_KEY)
        if not token:
            return False
        api_client.access_token = token
        api_client.refresh_token = await pref.get(REFRESH_KEY)
        
        me = api_client.get_me()
        if me and "detail" not in me:
            api_client.user = {
                "role": await pref.get(ROLE_KEY),
                "email": await pref.get(EMAIL_KEY),
            }
            return True
        else:
            await clear_session()
            return False

    # --- Navigation ---
    async def on_logout():
        await clear_session()
        api_client.access_token = None
        api_client.refresh_token = None
        api_client.user = None
        await page.push_route("/login")
    
    def get_page(route, params=None):
        params = params or {}
        
        if route == "login":
            return login_page(page, show_mfa, show_register)
        elif route == "register":
            return register_page(page, lambda: page.push_route("/login"), lambda: page.push_route("/login"))
        elif route == "mfa":
            return mfa_page(page, params.get("email", ""), on_mfa_success)
        
        # Pages administrateur
        elif route == "dashboard":
            return dashboard_page(page, on_logout)
        elif route == "caveaux":
            return caveaux_page(page, on_logout, **params)
        elif route == "reservations":
            return reservations_page(page, on_logout)
        elif route == "paiements":
            return paiements_page(page, on_logout)
        elif route == "concessions":
            return concessions_page(page, on_logout)
        elif route == "exhumations":
            return exhumations_page(page, on_logout)
        elif route == "rapports":
            return rapports_page(page, on_logout)
        elif route == "users":
            return users_page(page, on_logout)
        
        # Pages client
        elif route == "client_dashboard":
            return client_dashboard_page(page, on_logout)
        elif route == "client_reserver":
            return client_reserver_page(page, on_logout, **params)
        elif route == "client_reservations":
            return client_reservations_page(page, on_logout)
        elif route == "client_paiements":
            return client_paiements_page(page, on_logout)
        elif route == "client_profil":
            return client_profil_page(page, on_logout)
        elif route == "client_exhumations":
            return client_exhumations_page(page, on_logout)
        elif route == "client_carte":
            return client_carte_page(page, on_logout)
        
        return ft.Container(content=ft.Text("Page non trouvée", color="#1F2937"), expand=True, bgcolor=COLOR_BG)

    def show_mfa(email):
        page.push_route(f"/mfa?email={email}")

    def show_register():
        page.push_route("/register")

    async def on_mfa_success():
        await persist_session()
        role = api_client.user.get("role") if api_client.user else "CLIENT"
        
        # Vérifier les paramètres de coordonnées
        from components.data_fetcher import get_pending_pick
        pick_data = get_pending_pick()
        
        if role == "CLIENT":
            await page.push_route("/client_dashboard")
        else:
            if pick_data and pick_data.get("has_pick"):
                params = {
                    "pick_lat": str(pick_data["latitude"]),
                    "pick_lng": str(pick_data["longitude"]),
                    "pick_caveau_id": str(pick_data["caveau_id"]) if pick_data.get("caveau_id") else None,
                }
                await page.push_route(f"/caveaux?pick_lat={params['pick_lat']}&pick_lng={params['pick_lng']}")
            else:
                await page.push_route("/dashboard")

    # --- Route change handler ---
    async def on_route_change(e):
        route = page.route.replace("/", "") or "dashboard"
        parsed = urlparse(page.route)
        params = parse_qs(parsed.query)
        params = {k: v[0] if v else None for k, v in params.items()}
        
        # Si ce n'est pas une page publique et qu'on n'est pas connecté
        if route not in ["login", "register"]:
            if not api_client.access_token:
                await page.push_route("/login")
                return
        
        # Si on est sur login ou register et déjà connecté, rediriger
        if route in ["login", "register"] and api_client.access_token:
            role = api_client.user.get("role") if api_client.user else "CLIENT"
            await page.push_route("/dashboard" if role != "CLIENT" else "/client_dashboard")
            return
        
        # Si route mfa sans email, rediriger vers login
        if route == "mfa" and not params.get("email"):
            await page.push_route("/login")
            return
        
        # Charger la page
        content = get_page(route, params)
        page.controls.clear()
        page.add(content)
        page.update()

    page.on_route_change = on_route_change

    # --- Initialisation ---
    # Restaurer la session
    session_ok = await restore_session()
    
    if session_ok:
        role = api_client.user.get("role") if api_client.user else "CLIENT"
        default_route = "/dashboard" if role != "CLIENT" else "/client_dashboard"
        await page.push_route(default_route)
    else:
        await page.push_route("/login")

# ✅ Remettre le port 8550
ft.run(main, view=ft.AppView.WEB_BROWSER, port=8551)