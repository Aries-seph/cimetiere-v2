import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_BLUE, COLOR_GREEN, COLOR_ORANGE, COLOR_BORDER
from components.sidebar import build_sidebar
from components.stat_card import build_stat_card
from components.charts import build_evolution_chart, build_repartition_donut
from components.data_fetcher import get_dashboard_stats, get_evolution_7_jours

MOBILE_BREAKPOINT = 768


def admin_dashboard(page: ft.Page, on_navigate, on_logout):

    stats = get_dashboard_stats() or {}
    if not isinstance(stats, dict) or stats.get("success") is False:
        stats = {}
    caveaux_stats = stats.get("caveaux", {})
    finances_stats = stats.get("finances", {})

    evolution_data = get_evolution_7_jours() or []
    if not isinstance(evolution_data, list):
        evolution_data = []

    is_mobile = page.width < MOBILE_BREAKPOINT

    drawer_ref = {"control": None, "overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar(page, "dashboard", on_navigate, on_logout, on_close=close_drawer)
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
        header_controls.append(
            ft.IconButton(icon=ft.icons.MENU, icon_color=COLOR_TEXT, on_click=lambda e: open_drawer())
        )
    header_controls.append(
        ft.Text("Tableau de Bord", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT)
    )
    header_controls.append(ft.Container(expand=True))
    if not is_mobile:
        header_controls.append(
            ft.Row(
                [
                    ft.Icon(ft.icons.NOTIFICATIONS_OUTLINED, color=COLOR_TEXT_MUTED),
                    ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON), bgcolor=COLOR_PRIMARY),
                    ft.Text("Admin", color=COLOR_TEXT),
                ],
                spacing=14,
            )
        )
    else:
        header_controls.append(
            ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON), bgcolor=COLOR_PRIMARY, radius=16)
        )

    header = ft.Row(header_controls)

    card_defs = [
        ("Caveaux disponibles", str(caveaux_stats.get("disponibles", 0)), ft.icons.GRID_VIEW_OUTLINED, COLOR_GREEN, f"sur {caveaux_stats.get('total', 0)} au total"),
        ("Réservations en attente", str(stats.get("reservations_en_attente", 0)), ft.icons.EVENT_NOTE_OUTLINED, COLOR_PRIMARY, "à traiter"),
        ("Taux d'occupation", caveaux_stats.get("taux_occupation", "0%"), ft.icons.PIE_CHART_OUTLINE, COLOR_BLUE, "du cimetière"),
        ("Revenus totaux", f"{finances_stats.get('total_revenus', 0):,.0f} FCFA", ft.icons.PAYMENTS_OUTLINED, COLOR_ORANGE, "paiements validés"),
    ]

    cards = [build_stat_card(t, v, i, c, subtitle=s) for (t, v, i, c, s) in card_defs]
    stats_section = ft.Column(cards, spacing=12) if is_mobile else ft.Row(cards, spacing=16)

    evolution_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Évolution des revenus (7 derniers jours)", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=10),
                build_evolution_chart(evolution_data),
            ],
        ),
        bgcolor=COLOR_CARD, padding=20, border_radius=14, border=ft.border.all(1, COLOR_BORDER), expand=True,
    )

    legend_items = [
        ("Disponible", caveaux_stats.get("disponibles", 0), COLOR_GREEN),
        ("Réservé", caveaux_stats.get("reserves", 0), COLOR_ORANGE),
        ("Occupé", caveaux_stats.get("occupes", 0), "#EF4444"),
        ("Inexploitable", caveaux_stats.get("inexploitables", 0), "#6B7280"),
    ]

    legend = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(width=10, height=10, bgcolor=color, border_radius=5),
                    ft.Text(f"{label}", size=12, color=COLOR_TEXT_MUTED, expand=True),
                    ft.Text(f"{value}", size=12, color=COLOR_TEXT, weight=ft.FontWeight.W_500),
                ],
                spacing=8,
            )
            for label, value, color in legend_items
        ],
        spacing=10,
    )

    repartition_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Répartition des caveaux", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=10),
                ft.Row(
                    [
                        build_repartition_donut(caveaux_stats),
                        ft.Container(width=16),
                        ft.Container(content=legend, expand=True),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
        ),
        bgcolor=COLOR_CARD, padding=20, border_radius=14, border=ft.border.all(1, COLOR_BORDER), expand=True,
    )

    resume_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Activité récente", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=16),
                ft.Row([ft.Icon(ft.icons.FOLDER_SPECIAL_OUTLINED, color=COLOR_TEXT_MUTED, size=18),
                        ft.Text(f"Exhumations en attente : {stats.get('exhumations_en_attente', 0)}", color=COLOR_TEXT_MUTED, size=13)], spacing=8),
                ft.Row([ft.Icon(ft.icons.ASSIGNMENT_OUTLINED, color=COLOR_TEXT_MUTED, size=18),
                        ft.Text(f"Concessions actives : {stats.get('concessions_actives', 0)}", color=COLOR_TEXT_MUTED, size=13)], spacing=8),
            ],
            spacing=12,
        ),
        bgcolor=COLOR_CARD, padding=20, border_radius=14, border=ft.border.all(1, COLOR_BORDER), expand=True,
    )

    bottom_section = (
        ft.Column([repartition_card, resume_card], spacing=16)
        if is_mobile
        else ft.Row([repartition_card, resume_card], spacing=16, expand=True)
    )

    content = ft.Container(
        content=ft.Column(
            [
                header,
                ft.Container(height=20),
                stats_section,
                ft.Container(height=20),
                evolution_card,
                ft.Container(height=20),
                bottom_section,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=16 if is_mobile else 30,
        expand=True,
        bgcolor=COLOR_BG,
    )

    if is_mobile:
        return content

    sidebar = build_sidebar(page, "dashboard", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)