# theme.py
import flet as ft

# Couleurs principales - Bleu et Blanc
COLOR_PRIMARY = "#1A56DB"      # Bleu principal
COLOR_PRIMARY_LIGHT = "#3B82F6"  # Bleu clair
COLOR_PRIMARY_DARK = "#1E3A8A"   # Bleu foncé
COLOR_BG = "#F0F4FF"            # Fond bleu très clair
COLOR_CARD = "#FFFFFF"           # Blanc pour les cartes
COLOR_SIDEBAR = "#1A56DB"        # Bleu pour la navbar
COLOR_TEXT = "#1F2937"           # Texte foncé
COLOR_TEXT_MUTED = "#6B7280"     # Texte grisé
COLOR_BORDER = "#E5E7EB"         # Bordures claires
COLOR_GREEN = "#10B981"
COLOR_ORANGE = "#F59E0B"
COLOR_RED = "#EF4444"

# Styles réutilisables
def get_primary_btn_style():
    return ft.ButtonStyle(
        bgcolor=COLOR_PRIMARY,
        color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=8),
        padding=ft.Padding(16, 10, 16, 10),
    )

def get_outline_btn_style():
    return ft.ButtonStyle(
        bgcolor=ft.Colors.TRANSPARENT,
        color=COLOR_PRIMARY,
        shape=ft.RoundedRectangleBorder(radius=8),
        side=ft.BorderSide(1, COLOR_PRIMARY),
        padding=ft.Padding(16, 10, 16, 10),
    )

def get_card_style():
    return ft.Border(
        left=ft.BorderSide(0, COLOR_BORDER),
        top=ft.BorderSide(0, COLOR_BORDER),
        right=ft.BorderSide(0, COLOR_BORDER),
        bottom=ft.BorderSide(0, COLOR_BORDER),
    )