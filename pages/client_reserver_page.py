# pages/client_reserver_page.py
import flet as ft
from datetime import datetime
from components.navbar import build_navbar
from components.data_fetcher import get_caveaux_disponibles, create_reservation_client
from theme import (
    COLOR_BG,
    COLOR_CARD,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_PRIMARY,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_BORDER,
)


def client_reserver_page(page: ft.Page, on_logout, preselect_caveau_id=None):
    """Page de réservation moderne pour les clients."""

    is_mobile = page.width < 768
    navbar, _ = build_navbar(page, "CLIENT", on_logout)

    list_container = ft.Column(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)

    # --- DIALOG DE RÉSERVATION STYLE MODERNE ---
    def open_reservation_dialog(caveau):
        nom_defunt_field = ft.TextField(
            label="Nom complet du défunt",
            hint_text="Ex: Jean Dupont",
            prefix_icon=ft.icons.PERSON_OUTLINED,
            border_radius=8,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
        )

        date_deces_field = ft.TextField(
            label="Date de décès",
            hint_text="AAAA-MM-JJ",
            prefix_icon=ft.icons.CALENDAR_TODAY_OUTLINED,
            border_radius=8,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            read_only=True,
            expand=True,
        )

        def handle_date_change(e):
            if date_picker.value:
                date_deces_field.value = date_picker.value.strftime("%Y-%m-%d")
                page.update()

        date_picker = ft.DatePicker(
            first_date=datetime(1900, 1, 1),
            last_date=datetime.now(),
            on_change=handle_date_change,
        )
        page.overlay.append(date_picker)

        date_picker_button = ft.IconButton(
            icon=ft.icons.EDIT_CALENDAR_ROUNDED,
            icon_color=COLOR_PRIMARY,
            tooltip="Choisir la date",
            on_click=lambda e: setattr(date_picker, "open", True) or page.update(),
        )

        date_row = ft.Row([date_deces_field, date_picker_button], spacing=8, alignment=ft.MainAxisAlignment.CENTER)

        commentaire_field = ft.TextField(
            label="Remarques / Demandes particulières (Optionnel)",
            prefix_icon=ft.icons.CHAT_BUBBLE_OUTLINE,
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=8,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
        )

        error_text = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=COLOR_RED, size=16),
                ft.Text("", color=COLOR_RED, size=12, weight=ft.FontWeight.W_500),
            ], spacing=6),
            visible=False,
        )

        success_text = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=COLOR_GREEN, size=16),
                ft.Text("", color=COLOR_GREEN, size=12, weight=ft.FontWeight.W_500),
            ], spacing=6),
            visible=False,
        )

        def handle_submit(e):
            if not nom_defunt_field.value or not date_deces_field.value:
                error_text.content.controls[1].value = "Veuillez remplir les champs obligatoires."
                error_text.visible = True
                success_text.visible = False
                page.update()
                return

            payload = {
                "caveau_id": caveau["id"],
                "nom_defunt": nom_defunt_field.value,
                "date_deces": date_deces_field.value,
                "commentaire": commentaire_field.value or "",
            }
            result = create_reservation_client(payload)

            if result.get("success"):
                success_text.content.controls[1].value = "Demande envoyée avec succès !"
                success_text.visible = True
                error_text.visible = False
                page.update()
                refresh_list()
            else:
                error_text.content.controls[1].value = result.get("message", "Erreur lors de la soumission.")
                error_text.visible = True
                success_text.visible = False
                page.update()

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            shape=ft.RoundedRectangleBorder(radius=16),
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.BOOKMARK_ADD_ROUNDED, color=COLOR_PRIMARY, size=24),
                    ft.Text(f"Réserver le Caveau {caveau.get('reference', '')}", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ],
                spacing=10,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Veuillez renseigner les informations ci-dessous pour formuler votre demande de réservation.", size=13, color=COLOR_TEXT_MUTED),
                        ft.Divider(height=1, color=COLOR_BORDER),
                        nom_defunt_field,
                        date_row,
                        commentaire_field,
                        error_text,
                        success_text,
                    ],
                    spacing=14,
                    tight=True,
                ),
                width=380,
            ),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.Button(
                    "Confirmer la demande",
                    icon=ft.icons.SEND_ROUNDED,
                    bgcolor=COLOR_PRIMARY,
                    color=ft.colors.WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=handle_submit,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- CARTE DE CAVEAU (DESIGN MODERNE) ---
    def build_caveau_card(caveau):
        return ft.Container(
            content=ft.Row(
                [
                    # Côté Gauche : Infos
                    ft.Row(
                        [
                            # Icône d'illustration
                            ft.Container(
                                content=ft.Icon(ft.Icons.CROP_FREE_ROUNDED, color=COLOR_PRIMARY, size=22),
                                bgcolor=COLOR_BG,
                                padding=12,
                                border_radius=10,
                            ),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                f"Caveau {caveau.get('reference', '-')}",
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=COLOR_TEXT,
                                            ),
                                            # Badge Disponibilité
                                            ft.Container(
                                                content=ft.Text("Disponible", size=10, color=COLOR_GREEN, weight=ft.FontWeight.BOLD),
                                                bgcolor=ft.colors.with_opacity(0.15, COLOR_GREEN),
                                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                                border_radius=12,
                                            ),
                                        ],
                                        spacing=10,
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.STRAIGHTEN_ROUNDED, size=14, color=COLOR_TEXT_MUTED),
                                            ft.Text(
                                                f"Dimensions : {caveau.get('longueur', '-')} m × {caveau.get('largeur', '-')} m",
                                                size=13,
                                                color=COLOR_TEXT_MUTED,
                                            ),
                                        ],
                                        spacing=4,
                                    ),
                                ],
                                spacing=4,
                            ),
                        ],
                        spacing=16,
                    ),
                    # Côté Droit : Action
                    ft.Button(
                        "Réserver",
                        icon=ft.Icons.LOCATION_ON_OUTLINED,
                        bgcolor=COLOR_PRIMARY,
                        color=ft.colors.WHITE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e, c=caveau: open_reservation_dialog(c),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COLOR_CARD,
            padding=18,
            border_radius=12,
            border=ft.border.all(1, COLOR_BORDER),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.colors.with_opacity(0.04, ft.colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )

    # --- RAFRAÎCHISSEMENT DE LA LISTE ---
    def refresh_list():
        caveaux = get_caveaux_disponibles() or []
        list_container.controls.clear()

        if not caveaux or not isinstance(caveaux, list):
            # État Vide Stylisé
            list_container.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INBOX_OUTLINED, size=48, color=COLOR_TEXT_MUTED),
                            ft.Text("Aucun caveau disponible", size=16, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text("Revenez plus tard ou contactez l'administration.", size=13, color=COLOR_TEXT_MUTED),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    alignment=ft.alignment.center,
                    padding=40,
                )
            )
        else:
            for c in caveaux:
                list_container.controls.append(build_caveau_card(c))
        page.update()

    refresh_list()

    # Pre-selection
    if preselect_caveau_id:
        def open_preselected():
            try:
                cid = int(preselect_caveau_id)
                caveaux_dispo = get_caveaux_disponibles() or []
                match = next((c for c in caveaux_dispo if c["id"] == cid), None)
                if match:
                    open_reservation_dialog(match)
            except (ValueError, TypeError):
                pass
        page.after_update = open_preselected

    # --- STRUCTURE DE PAGE PRINCIPALE ---
    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=10),
                # Bannière d'en-tête (Hero section)
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Espace Réservation", size=24 if is_mobile else 28, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                    ft.Text("Consultez les emplacements disponibles et effectuez vos demandes en ligne.", size=14, color=COLOR_TEXT_MUTED),
                                ],
                                spacing=4,
                            ),
                        ],
                    ),
                    padding=ft.padding.only(bottom=10),
                ),
                ft.Divider(height=1, color=COLOR_BORDER),
                ft.Container(height=10),
                list_container,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.only(left=24, top=0, right=24, bottom=24),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content