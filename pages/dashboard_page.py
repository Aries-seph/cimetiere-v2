# pages/dashboard_page.py
import flet as ft
from components.navbar import build_navbar
from components.stat_card import build_stat_card
from components.charts import build_evolution_chart, build_repartition_donut
from components.data_fetcher import get_dashboard_stats, get_evolution_7_jours
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_BLUE, COLOR_GREEN, COLOR_ORANGE, COLOR_BORDER


def dashboard_page(page: ft.Page, on_logout):
    """Page Dashboard pour administrateur"""
    
    stats = get_dashboard_stats() or {}
    if not isinstance(stats, dict) or stats.get("success") is False:
        stats = {}
    
    caveaux_stats = stats.get("caveaux", {})
    finances_stats = stats.get("finances", {})
    evolution_data = get_evolution_7_jours() or []
    
    if not isinstance(evolution_data, list):
        evolution_data = []
    
    is_mobile = page.width < 768
    
    # Construction de la navbar
    navbar, _ = build_navbar(page, "ADMIN", on_logout)
    
    # Statistiques
    card_defs = [
        ("Caveaux disponibles", str(caveaux_stats.get("disponibles", 0)), ft.Icons.GRID_VIEW_OUTLINED, COLOR_GREEN, f"sur {caveaux_stats.get('total', 0)} au total"),
        ("Réservations en attente", str(stats.get("reservations_en_attente", 0)), ft.Icons.EVENT_NOTE_OUTLINED, COLOR_PRIMARY, "à traiter"),
        ("Taux d'occupation", caveaux_stats.get("taux_occupation", "0%"), ft.Icons.PIE_CHART_OUTLINE, COLOR_BLUE, "du cimetière"),
        ("Revenus totaux", f"{finances_stats.get('total_revenus', 0):,.0f} FCFA", ft.Icons.PAYMENTS_OUTLINED, COLOR_ORANGE, "paiements validés"),
    ]
    
    cards = [build_stat_card(t, v, i, c, subtitle=s) for (t, v, i, c, s) in card_defs]
    stats_row = ft.Row(cards, spacing=16, wrap=True) if not is_mobile else ft.Column(cards, spacing=12)
    
    # Graphiques
    evolution_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Évolution des revenus (7 derniers jours)", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=10),
                build_evolution_chart(evolution_data),
            ],
        ),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )
    
    # Répartition
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
                    ft.Text(label, size=12, color=COLOR_TEXT_MUTED, expand=True),
                    ft.Text(str(value), size=12, color=COLOR_TEXT, weight=ft.FontWeight.W_500),
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
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )
    
    # Résumé activité
    resume_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Activité récente", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(height=16),
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER_SPECIAL_OUTLINED, color=COLOR_TEXT_MUTED, size=18),
                    ft.Text(f"Exhumations en attente : {stats.get('exhumations_en_attente', 0)}", color=COLOR_TEXT_MUTED, size=13)
                ], spacing=8),
                ft.Row([
                    ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, color=COLOR_TEXT_MUTED, size=18),
                    ft.Text(f"Concessions actives : {stats.get('concessions_actives', 0)}", color=COLOR_TEXT_MUTED, size=13)
                ], spacing=8),
            ],
            spacing=12,
        ),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )
    
    bottom_row = ft.Row([repartition_card, resume_card], spacing=16, expand=True) if not is_mobile else ft.Column([repartition_card, resume_card], spacing=16)
    
    # Contenu principal
    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                stats_row,
                ft.Container(height=20),
                evolution_card,
                ft.Container(height=20),
                bottom_row,
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