# main.py
import flet as ft
from urllib.parse import urlparse, parse_qs

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

from theme import COLOR_BG
from api_client import api_client

# Clés de session
TOKEN_KEY = "cimetiere.access_token"
REFRESH_KEY = "cimetiere.refresh_token"
ROLE_KEY = "cimetiere.user_role"
EMAIL_KEY = "cimetiere.user_email"

# Variables globales pour les paramètres de sélection
_pick_lat = None
_pick_lng = None
_pick_caveau_id = None
_preselect_caveau_id = None


async def main(page: ft.Page):
    global _pick_lat, _pick_lng, _pick_caveau_id, _preselect_caveau_id
    
    page.title = "CIMETIERE de VILLE"
    page.bgcolor = COLOR_BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # --- Gestion de session ---
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
        token = await page.shared_preferences.get(TOKEN_KEY)
        if not token:
            return False
        api_client.access_token = token
        api_client.refresh_token = await page.shared_preferences.get(REFRESH_KEY)
        
        try:
            me = api_client.get_me()
            if me and "detail" not in me:
                api_client.user = {
                    "role": await page.shared_preferences.get(ROLE_KEY),
                    "email": await page.shared_preferences.get(EMAIL_KEY),
                }
                return True
        except Exception:
            pass
        
        await clear_session()
        return False

    # --- Navigation ---
    async def on_logout():
        await clear_session()
        api_client.access_token = None
        api_client.refresh_token = None
        api_client.user = None
        page.go("/login")
    
    def show_mfa(email):
        page.go(f"/mfa?email={email}")

    def show_register():
        page.go("/register")

    async def on_mfa_success():
        await persist_session()
        role = api_client.user.get("role") if api_client.user else "CLIENT"
        
        # Vérifier les coordonnées en attente
        try:
            from components.data_fetcher import get_pending_pick
            pick_data = get_pending_pick()
        except Exception:
            pick_data = None
        
        if role == "CLIENT":
            page.go("/client_dashboard")
        else:
            if pick_data and pick_data.get("has_pick"):
                params = f"?pick_lat={pick_data['latitude']}&pick_lng={pick_data['longitude']}"
                if pick_data.get("caveau_id"):
                    params += f"&pick_caveau_id={pick_data['caveau_id']}"
                page.go(f"/caveaux{params}")
            else:
                page.go("/dashboard")

    # --- Route change handler ---
    async def on_route_change(e):
        global _pick_lat, _pick_lng, _pick_caveau_id, _preselect_caveau_id
        
        route = page.route.replace("/", "") or "dashboard"
        parsed = urlparse(page.route)
        params = parse_qs(parsed.query)
        params = {k: v[0] if v else None for k, v in params.items()}
        
        # Extraire les paramètres
        _pick_lat = params.get("pick_lat")
        _pick_lng = params.get("pick_lng")
        _pick_caveau_id = params.get("pick_caveau_id")
        _preselect_caveau_id = params.get("caveau_id")
        
        # Si ce n'est pas une page publique et qu'on n'est pas connecté
        if route not in ["login", "register"]:
            if not api_client.access_token:
                page.go("/login")
                return
        
        # Si on est sur login ou register et déjà connecté
        if route in ["login", "register"] and api_client.access_token:
            role = api_client.user.get("role") if api_client.user else "CLIENT"
            page.go("/dashboard" if role != "CLIENT" else "/client_dashboard")
            return
        
        # Si route mfa sans email
        if route == "mfa" and not params.get("email"):
            page.go("/login")
            return
        
        # Charger la page avec les paramètres appropriés
        page.controls.clear()
        
        try:
            if route == "login":
                page.add(login_page(page, show_mfa, show_register))
            elif route == "register":
                page.add(register_page(page, lambda: page.go("/login"), lambda: page.go("/login")))
            elif route == "mfa":
                page.add(mfa_page(page, params.get("email", ""), on_mfa_success))
            elif route == "dashboard":
                page.add(dashboard_page(page, on_logout))
            elif route == "caveaux":
                page.add(caveaux_page(
                    page, 
                    on_logout, 
                    pick_lat=_pick_lat, 
                    pick_lng=_pick_lng, 
                    pick_caveau_id=_pick_caveau_id
                ))
            elif route == "reservations":
                page.add(reservations_page(page, on_logout))
            elif route == "paiements":
                page.add(paiements_page(page, on_logout))
            elif route == "concessions":
                page.add(concessions_page(page, on_logout))
            elif route == "exhumations":
                page.add(exhumations_page(page, on_logout))
            elif route == "rapports":
                page.add(rapports_page(page, on_logout))
            elif route == "users":
                page.add(users_page(page, on_logout))
            elif route == "client_dashboard":
                page.add(client_dashboard_page(page, on_logout))
            elif route == "client_reserver":
                page.add(client_reserver_page(
                    page, 
                    on_logout, 
                    preselect_caveau_id=_preselect_caveau_id
                ))
            elif route == "client_reservations":
                page.add(client_reservations_page(page, on_logout))
            elif route == "client_paiements":
                page.add(client_paiements_page(page, on_logout))
            elif route == "client_profil":
                page.add(client_profil_page(page, on_logout))
            elif route == "client_exhumations":
                page.add(client_exhumations_page(page, on_logout))
            elif route == "client_carte":
                page.add(client_carte_page(page, on_logout))
            else:
                page.add(ft.Container(
                    content=ft.Text("Page non trouvée", color="#1F2937"), 
                    expand=True, 
                    bgcolor=COLOR_BG
                ))
        except Exception as e:
            # En cas d'erreur, afficher une page d'erreur
            page.controls.clear()
            page.add(ft.Container(
                content=ft.Column([
                    ft.Text("Erreur lors du chargement de la page", size=20, color="#EF4444"),
                    ft.Text(str(e), size=14, color="#6B7280"),
                    ft.ElevatedButton("Retour à l'accueil", on_click=lambda e: page.go("/dashboard"))
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=COLOR_BG
            ))
        
        page.update()

    page.on_route_change = on_route_change

    # --- Gestion du redimensionnement ---
    def on_resize(e):
        # Forcer le re-rendu si nécessaire
        pass
    
    page.on_resize = on_resize

    # --- Initialisation ---
    session_ok = await restore_session()
    
    if session_ok:
        role = api_client.user.get("role") if api_client.user else "CLIENT"
        default_route = "/dashboard" if role != "CLIENT" else "/client_dashboard"
        page.go(default_route)
    else:
        page.go("/login")


ft.run(main, view=ft.AppView.WEB_BROWSER, port=8551)