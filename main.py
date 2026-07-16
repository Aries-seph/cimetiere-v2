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
    
    # Initialiser SharedPreferences
    pref = SharedPreferences()
    
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
        
        # Vérifier que le token est valide en interrogeant /me
        try:
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
        except Exception:
            await clear_session()
            return False

    # --- Navigation ---
    async def on_logout():
        await clear_session()
        api_client.access_token = None
        api_client.refresh_token = None
        api_client.user = None
        # ✅ Utiliser push_route au lieu de go
        await page.push_route("/login")
        page.update()
    
    def show_mfa(email):
        page.push_route(f"/mfa?email={email}")

    def show_register():
        page.push_route("/register")

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
            await page.push_route("/client_dashboard")
        else:
            if pick_data and pick_data.get("has_pick"):
                params = f"?pick_lat={pick_data['latitude']}&pick_lng={pick_data['longitude']}"
                if pick_data.get("caveau_id"):
                    params += f"&pick_caveau_id={pick_data['caveau_id']}"
                await page.push_route(f"/caveaux{params}")
            else:
                await page.push_route("/dashboard")
        page.update()

    # --- Route change handler ---
    async def on_route_change(e):
        global _pick_lat, _pick_lng, _pick_caveau_id, _preselect_caveau_id

        parsed = urlparse(page.route)
        route = parsed.path.strip("/") or "dashboard"
        params = parse_qs(parsed.query)
        params = {k: v[0] if v else None for k, v in params.items()}

        # Extraire les paramètres
        _pick_lat = params.get("pick_lat")
        _pick_lng = params.get("pick_lng")
        _pick_caveau_id = params.get("pick_caveau_id")
        _preselect_caveau_id = params.get("caveau_id")
        
        print(f"📍 Route: {route}, params: {params}")
        print(f"🔑 Token présent: {bool(api_client.access_token)}")
        
        # Si ce n'est pas une page publique et qu'on n'est pas connecté
        if route not in ["login", "register", "mfa"]:
            if not api_client.access_token:
                print("❌ Pas de token, redirection vers login")
                await page.push_route("/login")
                page.update()
                return
        
        # Si on est sur login ou register et déjà connecté
        if route in ["login", "register"] and api_client.access_token:
            role = api_client.user.get("role") if api_client.user else "CLIENT"
            await page.push_route("/dashboard" if role != "CLIENT" else "/client_dashboard")
            page.update()
            return
        
        # Si route mfa sans email
        if route == "mfa" and not params.get("email"):
            await page.push_route("/login")
            page.update()
            return
        
        # Charger la page
        page.controls.clear()
        
        try:
            # Pages d'authentification
            if route == "login":
                page.add(login_page(page, show_mfa, show_register, on_mfa_success))
            elif route == "register":
                page.add(register_page(page, lambda: page.push_route("/login"), lambda: page.push_route("/login")))
            elif route == "mfa":
                page.add(mfa_page(page, params.get("email", ""), on_mfa_success))
            
            # Pages administrateur
            elif route == "dashboard":
                page.add(dashboard_page(page, on_logout))
            elif route == "caveaux":
                page.add(caveaux_page(page, on_logout, pick_lat=_pick_lat, pick_lng=_pick_lng, pick_caveau_id=_pick_caveau_id))
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
            
            # Pages client
            elif route == "client_dashboard":
                page.add(client_dashboard_page(page, on_logout))
            elif route == "client_reserver":
                page.add(client_reserver_page(page, on_logout, preselect_caveau_id=_preselect_caveau_id))
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
            import traceback
            print(f"❌ Erreur: {e}")
            traceback.print_exc()
            page.controls.clear()
            page.add(ft.Container(
                content=ft.Column([
                    ft.Text("Erreur lors du chargement de la page", size=20, color="#EF4444"),
                    ft.Text(str(e), size=14, color="#6B7280"),
                    ft.TextButton("Retour à l'accueil", on_click=lambda e: page.push_route("/dashboard"))
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=COLOR_BG
            ))
        
        page.update()

    page.on_route_change = on_route_change

    # --- Gestion du redimensionnement ---
    def on_resize(e):
        pass
    
    page.on_resize = on_resize

    # --- Initialisation ---
    session_ok = await restore_session()
    
    if session_ok:
        role = api_client.user.get("role") if api_client.user else "CLIENT"
        default_route = "/dashboard" if role != "CLIENT" else "/client_dashboard"
        print(f"✅ Session restaurée, redirection vers {default_route}")
        await page.push_route(default_route)
    else:
        print("❌ Pas de session valide, redirection vers login")
        await page.push_route("/login")
    
    page.update()


# ✅ Revenir au port 8550 pour la compatibilité
ft.run(main, view=ft.AppView.WEB_BROWSER, port=8551)