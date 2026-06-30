import flet as ft
import flet_charts as fc
from theme import COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_TEXT_MUTED, COLOR_GREEN, COLOR_ORANGE, COLOR_RED


def build_evolution_chart(data: list):
    """Graphique en courbe — évolution des revenus sur 7 jours."""

    if not data:
        data = [{"jour": "-", "montant": 0} for _ in range(7)]

    points = [
        fc.LineChartDataPoint(i, item["montant"])
        for i, item in enumerate(data)
    ]

    max_val = max([item["montant"] for item in data], default=0)
    max_y = max_val * 1.2 if max_val > 0 else 100

    line_data = fc.LineChartData(
        points=points,
        curved=True,
        color=COLOR_PRIMARY_LIGHT,
        stroke_width=3,
        rounded_stroke_cap=True,
        below_line_bgcolor=ft.Colors.with_opacity(0.15, COLOR_PRIMARY_LIGHT),
        point=True,
    )

    bottom_labels = [
        fc.ChartAxisLabel(
            value=i,
            label=ft.Text(item["jour"], size=11, color=COLOR_TEXT_MUTED)
        )
        for i, item in enumerate(data)
    ]

    chart = fc.LineChart(
        data_series=[line_data],
        border=ft.Border.all(0, "transparent"),
        horizontal_grid_lines=fc.ChartGridLines(interval=max_y / 4 if max_y else 25, color="#2D2D44", width=1),
        left_axis=fc.ChartAxis(title=ft.Text("")),
        bottom_axis=fc.ChartAxis(labels=bottom_labels),
        min_y=0,
        max_y=max_y,
        min_x=0,
        max_x=len(data) - 1,
        interactive=True,
        expand=True,
    )

    return ft.Container(content=chart, height=260)


def build_repartition_donut(caveaux_stats: dict):
    """Donut chart — répartition des caveaux par statut."""

    disponibles = caveaux_stats.get("disponibles", 0)
    reserves = caveaux_stats.get("reserves", 0)
    occupes = caveaux_stats.get("occupes", 0)
    inexploitables = caveaux_stats.get("inexploitables", 0)

    sections = [
        fc.PieChartSection(
            value=disponibles if disponibles > 0 else 0.001,
            color=COLOR_GREEN,
            radius=50,
            title=f"{disponibles}",
            title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        ),
        fc.PieChartSection(
            value=reserves if reserves > 0 else 0.001,
            color=COLOR_ORANGE,
            radius=50,
            title=f"{reserves}",
            title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        ),
        fc.PieChartSection(
            value=occupes if occupes > 0 else 0.001,
            color=COLOR_RED,
            radius=50,
            title=f"{occupes}",
            title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        ),
        fc.PieChartSection(
            value=inexploitables if inexploitables > 0 else 0.001,
            color="#6B7280",
            radius=50,
            title=f"{inexploitables}",
            title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        ),
    ]

    chart = fc.PieChart(
        sections=sections,
        sections_space=2,
        center_space_radius=40,
        width=180,
        height=180,
    )

    return chart