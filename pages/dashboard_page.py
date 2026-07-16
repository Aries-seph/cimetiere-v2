# pages/dashboard_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_dashboard_stats, get_evolution_7_jours, get_occupation_par_bloc
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from datetime import datetime
import random


def dashboard_page(page: ft.Page, on_logout):
    """Page Dashboard pour administrateur - Version 2.0"""
    
    stats = get_dashboard_stats() or {}
    if not isinstance(stats, dict) or stats.get("success") is False:
        stats = {}
    
    caveaux_stats = stats.get("caveaux", {})
    finances_stats = stats.get("finances", {})
    evolution_data = get_evolution_7_jours() or []
    occupation_blocs = get_occupation_par_bloc() or []
    
    if not isinstance(evolution_data, list):
        evolution_data = []
    
    is_mobile = page.width < 768
    
    # Construction de la navbar
    navbar, _ = build_navbar(page, "ADMIN", on_logout)
    
    # ----- HEADER AVEC MÉTÉO -----
    current_hour = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%d %B %Y")
    temp = random.randint(22, 32)
    
    header_card = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Bonjour Administrateur", size=24 if not is_mobile else 18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(f"{current_date} • {current_hour}", size=14, color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE), size=16),
                                ft.Text("Dernière mise à jour: à l'instant", size=12, color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                            ],
                            spacing=6,
                        ),
                    ],
                    spacing=4,
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.WB_SUNNY, color=ft.Colors.AMBER, size=36),
                            ft.Column(
                                [
                                    ft.Text(f"{temp}°C", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text("Ensoleillé", size=12, color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                    border_radius=14,
                    padding=ft.Padding(left=16, top=10, right=16, bottom=10),
                ),
            ],
            spacing=20,
        ),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[COLOR_PRIMARY, COLOR_PRIMARY_LIGHT],
        ),
        padding=ft.Padding(left=24, top=20, right=24, bottom=20),
        border_radius=14,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.2, COLOR_PRIMARY),
        ),
    )
    
    # ----- KPI CARDS AVEC BARRES DE PROGRESSION -----
    total_caveaux = caveaux_stats.get("total", 0)
    disponibles = caveaux_stats.get("disponibles", 0)
    occupes = caveaux_stats.get("occupes", 0)
    taux_occupation = float(caveaux_stats.get("taux_occupation", "0%").replace("%", "")) if caveaux_stats.get("taux_occupation") else 0
    
    def build_kpi_card(title, value, icon, color, progress=None, progress_label=None):
        content_items = [
            ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=ft.Colors.WHITE, size=18),
                        bgcolor=color,
                        width=38,
                        height=38,
                        border_radius=10,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        [
                            ft.Text(title, size=11, color=COLOR_TEXT_MUTED),
                            ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=10,
            ),
        ]
        
        if progress is not None:
            content_items.append(
                ft.Column(
                    [
                        ft.ProgressBar(
                            value=progress / 100,
                            height=6,
                            color=color,
                            bgcolor=ft.Colors.with_opacity(0.15, color),
                            border_radius=3,
                        ),
                        ft.Text(progress_label or f"{progress}%", size=10, color=COLOR_TEXT_MUTED),
                    ],
                    spacing=2,
                )
            )
        
        return ft.Container(
            content=ft.Column(content_items, spacing=6),
            bgcolor=COLOR_CARD,
            padding=ft.Padding(left=16, top=14, right=16, bottom=14),
            border_radius=12,
            border=ft.Border.all(1, COLOR_BORDER),
            expand=True,
        )
    
    kpi_cards = ft.Row(
        [
            build_kpi_card("Caveaux", total_caveaux, ft.Icons.GRID_VIEW_ROUNDED, COLOR_PRIMARY),
            build_kpi_card("Disponibles", disponibles, ft.Icons.CHECK_CIRCLE_OUTLINE, COLOR_GREEN),
            build_kpi_card("Occupés", occupes, ft.Icons.LOCATION_ON, "#EF4444"),
            build_kpi_card("Taux occup.", f"{taux_occupation:.1f}%", ft.Icons.SPEED, COLOR_ORANGE, progress=taux_occupation),
        ],
        spacing=12,
        wrap=True,
    ) if not is_mobile else ft.Column(
        [
            ft.Row([build_kpi_card("Caveaux", total_caveaux, ft.Icons.GRID_VIEW_ROUNDED, COLOR_PRIMARY),
                    build_kpi_card("Disponibles", disponibles, ft.Icons.CHECK_CIRCLE_OUTLINE, COLOR_GREEN)], spacing=12),
            ft.Row([build_kpi_card("Occupés", occupes, ft.Icons.LOCATION_ON, "#EF4444"),
                    build_kpi_card("Taux occup.", f"{taux_occupation:.1f}%", ft.Icons.SPEED, COLOR_ORANGE, progress=taux_occupation)], spacing=12),
        ],
        spacing=12,
    )
    
    # ----- SECTION GRAPHIQUE RADIAL (remplace le donut) -----
    def build_radial_gauge():
        percentage = min(taux_occupation, 100)
        
        if percentage < 50:
            gauge_color = COLOR_GREEN
        elif percentage < 75:
            gauge_color = COLOR_ORANGE
        else:
            gauge_color = COLOR_RED
        
        return ft.Container(
            content=ft.Stack(
                [
                    # Anneau de fond
                    ft.Container(
                        width=140,
                        height=140,
                        border_radius=70,
                        border=ft.Border.all(8, ft.Colors.with_opacity(0.15, COLOR_TEXT_MUTED)),
                    ),
                    # Anneau de progression
                    ft.Container(
                        width=140,
                        height=140,
                        border_radius=70,
                        border=ft.Border.all(8, gauge_color),
                        rotate=ft.Rotate(
                            angle=percentage / 100 * 3.6 - 1.8,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ),
                    # Texte central
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(f"{percentage:.0f}%", size=28, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                ft.Text("Occupation", size=11, color=COLOR_TEXT_MUTED),
                            ],
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.Alignment(0, 0),
                        width=140,
                        height=140,
                    ),
                ],
                alignment=ft.Alignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
        )
    
    def build_horizontal_bar_chart(data):
        if not data:
            data = [{"jour": "-", "montant": 0} for _ in range(7)]
        
        max_val = max([item.get("montant", 0) for item in data], default=1)
        
        bars = []
        colors = [COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, "#60A5FA", "#93C5FD", "#BFDBFE", "#DBEAFE", "#EFF6FF"]
        
        for i, item in enumerate(data):
            val = item.get("montant", 0)
            pct = (val / max_val * 100) if max_val > 0 else 0
            color = colors[i % len(colors)]
            
            bars.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(item.get("jour", "-")[:3], size=11, color=COLOR_TEXT_MUTED, width=30),
                            ft.Column(
                                [
                                    ft.Container(
                                        width=max(2, pct * 2),
                                        height=28,
                                        bgcolor=color,
                                        border_radius=ft.BorderRadius(4, 4, 4, 4),
                                    ),
                                ],
                                expand=True,
                            ),
                            ft.Text(f"{val:,.0f}" if val > 0 else "0", size=10, color=COLOR_TEXT_MUTED, width=60, text_align=ft.TextAlign.RIGHT),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    padding=ft.Padding(left=0, top=2, right=0, bottom=2),
                )
            )
        
        return ft.Column(bars, spacing=4)
    
    # ----- SECTION ACTIVITÉ EN TEMPS RÉEL -----
    def build_activity_timeline():
        activities = [
            {"icon": ft.Icons.PAYMENT, "color": COLOR_GREEN, "text": "Paiement validé - Caveau A12", "time": "Il y a 2min"},
            {"icon": ft.Icons.EVENT_NOTE, "color": COLOR_PRIMARY, "text": "Nouvelle réservation - Caveau B07", "time": "Il y a 15min"},
            {"icon": ft.Icons.FOLDER_SPECIAL, "color": COLOR_ORANGE, "text": "Demande d'exhumation #EXH-004", "time": "Il y a 32min"},
            {"icon": ft.Icons.ASSIGNMENT, "color": "#8B5CF6", "text": "Concession renouvelée - C03", "time": "Il y a 1h"},
        ]
        
        items = []
        for act in activities:
            items.append(
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(act["icon"], color=ft.Colors.WHITE, size=14),
                            bgcolor=act["color"],
                            width=30,
                            height=30,
                            border_radius=15,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text(act["text"], size=13, color=COLOR_TEXT),
                                ft.Text(act["time"], size=10, color=COLOR_TEXT_MUTED),
                            ],
                            spacing=0,
                        ),
                        ft.Container(expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=COLOR_TEXT_MUTED),
                    ],
                    spacing=10,
                )
            )
        
        return ft.Column(items, spacing=12)
    
    # ----- NOUVELLES CARTES -----
    echeances_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING_AMBER, size=18, color=COLOR_ORANGE),
                        ft.Text("Échéances à venir", size=15, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("Concession C12", size=13, color=COLOR_TEXT),
                            ft.Text("Expire dans 3 jours", size=11, color=COLOR_RED),
                        ], spacing=0),
                        ft.Container(expand=True),
                        ft.Text("⚠️", size=20),
                    ],
                ),
                ft.Divider(color=COLOR_BORDER, height=1),
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("Concession B45", size=13, color=COLOR_TEXT),
                            ft.Text("Expire dans 7 jours", size=11, color=COLOR_ORANGE),
                        ], spacing=0),
                        ft.Container(expand=True),
                        ft.Text("📅", size=20),
                    ],
                ),
                ft.Divider(color=COLOR_BORDER, height=1),
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("Réservation #R23", size=13, color=COLOR_TEXT),
                            ft.Text("En attente depuis 2h", size=11, color=COLOR_PRIMARY),
                        ], spacing=0),
                        ft.Container(expand=True),
                        ft.Text("⏳", size=20),
                    ],
                ),
                ft.Container(height=4),
                ft.TextButton("Voir toutes les échéances", on_click=lambda e: page.push_route("/concessions")),
            ],
            spacing=6,
        ),
        bgcolor=COLOR_CARD,
        padding=18,
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )
    
    repartition_stats = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(width=12, height=12, bgcolor=COLOR_GREEN, border_radius=4),
                    ft.Text(f"Disponible ({caveaux_stats.get('disponibles', 0)})", size=13, color=COLOR_TEXT, expand=True),
                    ft.Text(f"{caveaux_stats.get('disponibles', 0)/total_caveaux*100:.0f}%" if total_caveaux > 0 else "0%", size=13, weight=ft.FontWeight.W_500, color=COLOR_GREEN),
                ],
                spacing=8,
            ),
            ft.Row(
                [
                    ft.Container(width=12, height=12, bgcolor=COLOR_ORANGE, border_radius=4),
                    ft.Text(f"Réservé ({caveaux_stats.get('reserves', 0)})", size=13, color=COLOR_TEXT, expand=True),
                    ft.Text(f"{caveaux_stats.get('reserves', 0)/total_caveaux*100:.0f}%" if total_caveaux > 0 else "0%", size=13, weight=ft.FontWeight.W_500, color=COLOR_ORANGE),
                ],
                spacing=8,
            ),
            ft.Row(
                [
                    ft.Container(width=12, height=12, bgcolor="#EF4444", border_radius=4),
                    ft.Text(f"Occupé ({caveaux_stats.get('occupes', 0)})", size=13, color=COLOR_TEXT, expand=True),
                    ft.Text(f"{caveaux_stats.get('occupes', 0)/total_caveaux*100:.0f}%" if total_caveaux > 0 else "0%", size=13, weight=ft.FontWeight.W_500, color="#EF4444"),
                ],
                spacing=8,
            ),
            ft.Row(
                [
                    ft.Container(width=12, height=12, bgcolor="#6B7280", border_radius=4),
                    ft.Text(f"Inexploitable ({caveaux_stats.get('inexploitables', 0)})", size=13, color=COLOR_TEXT, expand=True),
                    ft.Text(f"{caveaux_stats.get('inexploitables', 0)/total_caveaux*100:.0f}%" if total_caveaux > 0 else "0%", size=13, weight=ft.FontWeight.W_500, color="#6B7280"),
                ],
                spacing=8,
            ),
        ],
        spacing=8,
    )
    
    repartition_rapide_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.PIE_CHART_OUTLINE, size=18, color=COLOR_TEXT_MUTED),
                        ft.Text("Répartition des caveaux", size=15, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                repartition_stats,
            ],
            spacing=6,
        ),
        bgcolor=COLOR_CARD,
        padding=18,
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )
    
    # ----- ASSEMBLAGE FINAL -----
    charts_section = ft.Row(
        [
            ft.Container(
                content=build_radial_gauge(),
                bgcolor=COLOR_CARD,
                padding=20,
                border_radius=12,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=1,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.TIMELINE, size=18, color=COLOR_TEXT_MUTED),
                                ft.Text("Activité récente", size=15, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ],
                            spacing=8,
                        ),
                        ft.Container(height=8),
                        build_activity_timeline(),
                    ],
                    spacing=4,
                ),
                bgcolor=COLOR_CARD,
                padding=18,
                border_radius=12,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=2,
            ),
        ],
        spacing=16,
    ) if not is_mobile else ft.Column(
        [
            ft.Container(
                content=build_radial_gauge(),
                bgcolor=COLOR_CARD,
                padding=20,
                border_radius=12,
                border=ft.Border.all(1, COLOR_BORDER),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.TIMELINE, size=18, color=COLOR_TEXT_MUTED),
                                ft.Text("Activité récente", size=15, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ],
                            spacing=8,
                        ),
                        ft.Container(height=8),
                        build_activity_timeline(),
                    ],
                    spacing=4,
                ),
                bgcolor=COLOR_CARD,
                padding=18,
                border_radius=12,
                border=ft.Border.all(1, COLOR_BORDER),
            ),
        ],
        spacing=16,
    )
    
    evolution_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.TRENDING_UP, size=18, color=COLOR_TEXT_MUTED),
                        ft.Text("Évolution des revenus (7 derniers jours)", size=15, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text("+12% vs semaine dernière", size=11, color=COLOR_GREEN),
                            bgcolor=ft.Colors.with_opacity(0.15, COLOR_GREEN),
                            padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                            border_radius=12,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=10),
                build_horizontal_bar_chart(evolution_data),
            ],
            spacing=4,
        ),
        bgcolor=COLOR_CARD,
        padding=18,
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER),
    )
    
    bottom_section = ft.Row(
        [echeances_card, repartition_rapide_card],
        spacing=16,
        expand=True,
    ) if not is_mobile else ft.Column([echeances_card, repartition_rapide_card], spacing=16)
    
    # Contenu principal
    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=16),
                header_card,
                ft.Container(height=16),
                kpi_cards,
                ft.Container(height=16),
                charts_section,
                ft.Container(height=16),
                evolution_section,
                ft.Container(height=16),
                bottom_section,
                ft.Container(height=16),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )
    
    return content