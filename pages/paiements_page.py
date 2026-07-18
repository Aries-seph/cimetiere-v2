# pages/paiements_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_all_paiements, validate_paiement, reject_paiement
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER

STATUT_COLORS = {
    "EN_ATTENTE": COLOR_ORANGE,
    "VALIDE": COLOR_GREEN,
    "REFUSE": COLOR_RED,
}

STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "VALIDE": "Validé",
    "REFUSE": "Refusé",
}

CANAL_LABELS = {
    "MOBILE_MONEY": "Mobile Money",
    "AIRTEL_MONEY": "Airtel Money",
    "ESPECES": "Espèces",
    "VIREMENT": "Virement",
}


def paiements_page(page: ft.Page, on_logout):
    """Page de gestion des paiements sous forme de tableau."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "ADMIN", on_logout)
    
    sort_option = "-created_at"
    
    # Conteneur principal pour accueillir la table
    table_container = ft.Container(expand=True)

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=10, top=2, right=10, bottom=2),
            border_radius=20,
        )

    def handle_validate(paiement_id):
        result = validate_paiement(paiement_id)
        if result.get("success"):
            refresh_list()

    def handle_reject(paiement_id):
        result = reject_paiement(paiement_id)
        if result.get("success"):
            refresh_list()

    def refresh_list():
        nonlocal sort_option
        paiements = get_all_paiements(sort_by=sort_option) or []
        table_container.content = None
        
        if not paiements or not isinstance(paiements, list):
            table_container.content = ft.Text("Aucun paiement enregistré", color=COLOR_TEXT_MUTED, size=14)
        else:
            columns = [
                ft.DataColumn(ft.Text("Référence", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Montant", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Méthode & Date", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Statut", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ]
            
            rows = []
            for p in paiements:
                if not isinstance(p, dict):
                    continue
                    
                statut = p.get("statut")
                actions = []
                
                if statut == "EN_ATTENTE":
                    actions.append(
                        ft.IconButton(
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            icon_color=COLOR_GREEN,
                            icon_size=20,
                            tooltip="Valider",
                            on_click=lambda e, pid=p["id"]: handle_validate(pid),
                        )
                    )
                    actions.append(
                        ft.IconButton(
                            icon=ft.Icons.CANCEL_OUTLINED,
                            icon_color=COLOR_RED,
                            icon_size=20,
                            tooltip="Refuser",
                            on_click=lambda e, pid=p["id"]: handle_reject(pid),
                        )
                    )

                montant = float(p.get("montant", 0) or 0)
                canal = CANAL_LABELS.get(p.get("canal"), p.get("canal", ""))
                
                created_at = p.get("created_at", "")
                date_display = ""
                if created_at:
                    try:
                        date_parts = created_at.split("T")
                        if len(date_parts) > 0:
                            date_display = date_parts[0]
                    except:
                        pass

                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(p.get("reference", "-"), color=COLOR_TEXT, weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(f"{montant:,.0f} FCFA", color=COLOR_TEXT)),
                            ft.DataCell(ft.Text(f"{canal} • {date_display}", color=COLOR_TEXT_MUTED)),
                            ft.DataCell(status_badge(statut)),
                            ft.DataCell(
                                ft.Row(actions, spacing=2, tight=True) if actions else ft.Text("-", color=COLOR_TEXT_MUTED)
                            ),
                        ]
                    )
                )

            table_container.content = ft.Row(
                [
                    ft.DataTable(
                        columns=columns,
                        rows=rows,
                        divider_thickness=1,
                        horizontal_lines=ft.BorderSide(1, COLOR_BORDER),
                        heading_row_height=45,
                        data_row_min_height=48,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        page.update()

    def change_sort(e):
        nonlocal sort_option
        if sort_option == "-created_at":
            sort_option = "created_at"
            sort_icon.name = ft.Icons.ARROW_UPWARD
            sort_text.value = "Plus ancien d'abord"
        else:
            sort_option = "-created_at"
            sort_icon.name = ft.Icons.ARROW_DOWNWARD
            sort_text.value = "Plus récent d'abord"
        page.update()
        refresh_list()

    sort_icon = ft.Icon(ft.Icons.ARROW_DOWNWARD, color=COLOR_TEXT_MUTED, size=18)
    sort_text = ft.Text("Plus récent d'abord", size=13, color=COLOR_TEXT_MUTED)
    
    sort_button = ft.Container(
        content=ft.Row([sort_icon, sort_text], spacing=6),
        padding=ft.Padding(left=12, top=6, right=12, bottom=6),
        bgcolor=COLOR_CARD,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER),
        on_click=change_sort,
        ink=True,
    )

    refresh_list()

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Gestion des paiements", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        sort_button,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(height=15),
                table_container,
                ft.Container(height=20),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content