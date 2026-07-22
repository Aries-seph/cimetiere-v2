# pages/rapports_page.py
import flet as ft
import os
import subprocess
import sys
import base64
from components.navbar import build_navbar
from components.data_fetcher import get_occupation_par_bloc, get_revenus_par_canal, download_export
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_BORDER

CANAL_LABELS = {
    "MOBILE_MONEY": "Mobile Money",
    "AIRTEL_MONEY": "Airtel Money",
    "ESPECES": "Espèces",
    "VIREMENT": "Virement",
}


def rapports_page(page: ft.Page, on_logout):
    """Page des rapports et exports."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "ADMIN", on_logout)
    
    occupation_data = get_occupation_par_bloc() or []
    revenus_data = get_revenus_par_canal() or []

    export_status = ft.Text("", size=12, color=COLOR_GREEN, visible=False)

    def handle_export(export_type, extension):
        """Télécharge le fichier via le navigateur."""
        result = download_export(export_type)
        
        if result and result.get("status_code") == 200:
            content = result.get("content")
            content_type = result.get("content_type", "")
            
            # Créer un fichier temporaire dans le conteneur
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Ouvrir le fichier dans le navigateur pour téléchargement
            # Flet permet de télécharger des fichiers via page.launch_url avec data URI
            import base64
            b64_content = base64.b64encode(content).decode('utf-8')
            data_uri = f"data:{content_type};base64,{b64_content}"
            
            # Ouvrir dans un nouvel onglet pour téléchargement
            page.launch_url(data_uri)
            
            export_status.value = f"Fichier {extension.upper()} téléchargé"
            export_status.color = COLOR_GREEN
            export_status.visible = True
            page.update()
            
            # Nettoyer le fichier temporaire
            try:
                os.unlink(tmp_path)
            except:
                pass
        else:
            export_status.value = "Erreur lors de l'export"
            export_status.color = "#EF4444"
            export_status.visible = True
            page.update()

    # --- Occupation Table ---
    if occupation_data and isinstance(occupation_data, list):
        occ_columns = [
            ft.DataColumn(ft.Text("Section / Bloc", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ratio", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Taux", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
        ]
        
        occ_rows = []
        for item in occupation_data:
            occ_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item.get('section', '-')} - {item.get('bloc', '-')}", color=COLOR_TEXT, weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(f"{item.get('occupes', 0)}/{item.get('total_caveaux', 0)}", color=COLOR_TEXT_MUTED)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(item.get("taux_occupation", "0%"), size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                bgcolor=COLOR_PRIMARY,
                                padding=ft.Padding(left=10, top=2, right=10, bottom=2),
                                border_radius=20,
                            )
                        ),
                    ]
                )
            )
        
        occupation_table = ft.Container(
            content=ft.Row([
                ft.DataTable(
                    columns=occ_columns,
                    rows=occ_rows,
                    divider_thickness=1,
                    horizontal_lines=ft.BorderSide(1, COLOR_BORDER),
                    heading_row_height=45,
                    data_row_min_height=45,
                )
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    else:
        occupation_table = ft.Text("Aucune donnée disponible", size=13, color=COLOR_TEXT_MUTED)

    occupation_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Occupation par bloc", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=10),
                occupation_table,
            ],
        ),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )

    # --- Revenus Table ---
    if revenus_data and isinstance(revenus_data, list):
        rev_columns = [
            ft.DataColumn(ft.Text("Canal", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Volume", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
        ]
        
        rev_rows = []
        for item in revenus_data:
            canal = CANAL_LABELS.get(item.get("canal"), item.get("canal", "-"))
            total = float(item.get("total", 0) or 0)
            nombre = item.get("nombre", 0)
            rev_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(canal, color=COLOR_TEXT, weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(f"{nombre} paiement(s)", color=COLOR_TEXT_MUTED)),
                        ft.DataCell(ft.Text(f"{total:,.0f} FCFA", color=COLOR_GREEN, weight=ft.FontWeight.BOLD)),
                    ]
                )
            )
            
        revenus_table = ft.Container(
            content=ft.Row([
                ft.DataTable(
                    columns=rev_columns,
                    rows=rev_rows,
                    divider_thickness=1,
                    horizontal_lines=ft.BorderSide(1, COLOR_BORDER),
                    heading_row_height=45,
                    data_row_min_height=45,
                )
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    else:
        revenus_table = ft.Text("Aucune donnée disponible", size=13, color=COLOR_TEXT_MUTED)

    revenus_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Revenus par canal de paiement", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=10),
                revenus_table,
            ],
        ),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )

    bottom_section = (
        ft.Column([occupation_card, revenus_card], spacing=16)
        if is_mobile
        else ft.Row([occupation_card, revenus_card], spacing=16, expand=True)
    )

    # --- Structure principale ---
    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Rapports et analyses", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                ),
                ft.Container(height=10),
                
                # Boutons d'export
                ft.Row(
                    [
                        ft.Button(
                            "CSV",
                            icon=ft.Icons.SIM_CARD_DOWNLOAD_OUTLINED,
                            bgcolor="#1F2937",
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda e: handle_export("csv", "csv"),
                        ),
                        ft.Button(
                            "Excel",
                            icon=ft.Icons.DOWNLOAD_FOR_OFFLINE_OUTLINED,
                            bgcolor=COLOR_PRIMARY,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda e: handle_export("excel", "xlsx"),
                        ),
                    ],
                    spacing=12,
                ),
                export_status,
                
                ft.Container(height=20),
                bottom_section,
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content