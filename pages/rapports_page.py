import flet as ft
import os
import subprocess
import sys
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_BORDER
from components.sidebar import build_sidebar
from components.data_fetcher import get_occupation_par_bloc, get_revenus_par_canal
from api_client import api_client, BASE_URL

MOBILE_BREAKPOINT = 768

CANAL_LABELS = {
    "MOBILE_MONEY": "Mobile Money",
    "AIRTEL_MONEY": "Airtel Money",
    "ESPECES": "Espèces",
    "VIREMENT": "Virement",
}


def rapports_page(page: ft.Page, on_navigate, on_logout):

    is_mobile = page.width < MOBILE_BREAKPOINT

    occupation_data = get_occupation_par_bloc() or []
    revenus_data = get_revenus_par_canal() or []

    export_status = ft.Text("", size=12, color=COLOR_GREEN, visible=False)

    def handle_export(export_type, extension):
        token = api_client.access_token

        if not token:
            export_status.value = "Session expirée, veuillez vous reconnecter."
            export_status.color = "#EF4444"
            export_status.visible = True
            page.update()
            return

        endpoint = "export-csv" if export_type == "csv" else "export-excel"
        url = f"{BASE_URL}/dashboard/{endpoint}?token={token}"

        page.launch_url(url, web_popup_window_name=ft.UrlTarget.SELF)

        export_status.value = "Téléchargement lancé..."
        export_status.color = "#10B981"
        export_status.visible = True
        page.update()
    occupation_rows = []
    if occupation_data and isinstance(occupation_data, list):
        for item in occupation_data:
            occupation_rows.append(
                ft.Row(
                    [
                        ft.Text(f"{item.get('section', '-')} - {item.get('bloc', '-')}", size=13, color=COLOR_TEXT, expand=True),
                        ft.Text(f"{item.get('occupes', 0)}/{item.get('total_caveaux', 0)}", size=13, color=COLOR_TEXT_MUTED),
                        ft.Container(
                            content=ft.Text(item.get("taux_occupation", "0%"), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                            bgcolor=COLOR_PRIMARY,
                            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                            border_radius=20,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
    else:
        occupation_rows.append(ft.Text("Aucune donnée disponible", size=13, color=COLOR_TEXT_MUTED))

    occupation_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Occupation par bloc", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=14),
                ft.Column(occupation_rows, spacing=12),
            ],
        ),
        bgcolor=COLOR_CARD, padding=20, border_radius=14, border=ft.Border.all(1, COLOR_BORDER), expand=True,
    )

    revenus_rows = []
    if revenus_data and isinstance(revenus_data, list):
        for item in revenus_data:
            canal = CANAL_LABELS.get(item.get("canal"), item.get("canal", "-"))
            total = float(item.get("total", 0) or 0)
            nombre = item.get("nombre", 0)
            revenus_rows.append(
                ft.Row(
                    [
                        ft.Text(canal, size=13, color=COLOR_TEXT, expand=True),
                        ft.Text(f"{nombre} paiement(s)", size=12, color=COLOR_TEXT_MUTED),
                        ft.Text(f"{total:,.0f} FCFA", size=13, color=COLOR_GREEN, weight=ft.FontWeight.W_500),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
    else:
        revenus_rows.append(ft.Text("Aucune donnée disponible", size=13, color=COLOR_TEXT_MUTED))

    revenus_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Revenus par canal de paiement", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=14),
                ft.Column(revenus_rows, spacing=12),
            ],
        ),
        bgcolor=COLOR_CARD, padding=20, border_radius=14, border=ft.Border.all(1, COLOR_BORDER), expand=True,
    )

    export_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Exporter les registres", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=14),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Exporter en CSV",
                            icon=ft.Icons.DESCRIPTION_OUTLINED,
                            bgcolor=COLOR_PRIMARY,
                            color=COLOR_TEXT,
                            on_click=lambda e: handle_export("csv", "csv"),
                        ),
                        ft.ElevatedButton(
                            "Exporter en Excel",
                            icon=ft.Icons.TABLE_CHART_OUTLINED,
                            bgcolor=COLOR_GREEN,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: handle_export("excel", "xlsx"),
                        ),
                    ],
                    spacing=12,
                ),
                ft.Container(height=8),
                export_status,
            ],
        ),
        bgcolor=COLOR_CARD, padding=20, border_radius=14, border=ft.Border.all(1, COLOR_BORDER),
    )

    bottom_section = (
        ft.Column([occupation_card, revenus_card], spacing=16)
        if is_mobile
        else ft.Row([occupation_card, revenus_card], spacing=16, expand=True)
    )

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar(page, "rapports", on_navigate, on_logout, on_close=close_drawer)
        overlay = ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=260, content=sidebar_mobile, bgcolor="#13131F"),
                    ft.Container(expand=True, bgcolor="#00000099", on_click=lambda e: close_drawer()),
                ],
                spacing=0,
            ),
            expand=True,
        )
        drawer_ref["overlay"] = overlay
        page.overlay.append(overlay)
        page.update()

    header_controls = []
    if is_mobile:
        header_controls.append(ft.IconButton(icon=ft.Icons.MENU, icon_color=COLOR_TEXT, on_click=lambda e: open_drawer()))
    header_controls.append(ft.Text("Rapports", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))

    header = ft.Row(header_controls)

    content_column = ft.Column(
        [
            header,
            ft.Container(height=20),
            export_card,
            ft.Container(height=20),
            bottom_section,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    content = ft.Container(
        content=content_column,
        padding=16 if is_mobile else 30,
        expand=True,
        bgcolor=COLOR_BG,
    )

    if is_mobile:
        return content

    sidebar = build_sidebar(page, "rapports", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)