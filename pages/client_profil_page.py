import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_my_profile, update_my_profile
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_RED, COLOR_BORDER


def client_profil_page(page: ft.Page, on_logout):
    """Page de profil du client (Flet 0.85+ compatible)."""
    
    is_mobile = page.width < 768
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    
    profile = get_my_profile() or {}
    username_val = profile.get("username", "")
    role_val = profile.get("role", "CLIENT")
    email_val = profile.get("email", "")
    telephone_val = profile.get("telephone", "")

    initials = username_val[:2].upper() if len(username_val) >= 2 else "CL"

    username_field = ft.TextField(
        label="Nom d'utilisateur",
        hint_text="Ex: John Doe",
        expand=True,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
        prefix_icon=ft.IconsPERSON_OUTLINE,
        border_radius=10,
        value=username_val,
    )

    telephone_field = ft.TextField(
        label="Téléphone",
        hint_text="Ex: +242 06 ...",
        expand=True,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
        prefix_icon=ft.IconsPHONE_OUTLINED,
        border_radius=10,
        keyboard_type=ft.KeyboardType.PHONE,
        value=telephone_val,
    )

    email_field = ft.TextField(
        label="Email (compte vérifié)",
        expand=True,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT_MUTED,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_BORDER,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
        prefix_icon=ft.IconsLOCK_OUTLINED,
        suffix_icon=ft.IconsVERIFIED_ROUNDED,
        border_radius=10,
        value=email_val,
        read_only=True,
    )

    error_text = ft.Text("", color=COLOR_RED, size=12, visible=False, weight=ft.FontWeight.W_500)
    success_text = ft.Text("", color=COLOR_GREEN, size=12, visible=False, weight=ft.FontWeight.W_500)

    def handle_save(e):
        error_text.visible = False
        success_text.visible = False

        payload = {}
        if username_field.value != profile.get("username", ""):
            payload["username"] = username_field.value
        if telephone_field.value != profile.get("telephone", ""):
            payload["telephone"] = telephone_field.value

        if not payload:
            error_text.value = "Aucune modification détectée"
            error_text.visible = True
            page.update()
            return

        result = update_my_profile(payload)

        if result.get("success"):
            success_text.value = "Votre profil a été mis à jour avec succès !"
            success_text.visible = True
            page.update()
        else:
            error_text.value = result.get("message", "Erreur lors de la mise à jour")
            error_text.visible = True
            page.update()

    profile_header_card = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Text(initials, size=22, weight=ft.FontWeight.BOLD, color="white"),
                    alignment=ft.Alignment.CENTER,
                    width=68,
                    height=68,
                    bgcolor=COLOR_PRIMARY,
                    border_radius=34,
                    border=ft.border.all(3, COLOR_BORDER),
                ),
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(username_val or "Utilisateur", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                ft.Container(
                                    content=ft.Text(role_val, size=10, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                                    bgcolor=COLOR_BG,
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    border_radius=12,
                                    border=ft.border.all(1, COLOR_PRIMARY),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        ft.Text(email_val or "Email non renseigné", size=13, color=COLOR_TEXT_MUTED),
                    ],
                    spacing=4,
                    expand=True,
                ),
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=16,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    security_notice_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SHIELD_OUTLINE, color=COLOR_PRIMARY, size=20),
                        ft.Text("Politique de sécurité", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "Pour garantir la traçabilité des réservations et des paiements, "
                    "un délai d'attente de 48 heures est appliqué entre deux modifications successives des informations de profil.",
                    size=12,
                    color=COLOR_TEXT_MUTED,
                ),
            ],
            spacing=8,
        ),
        bgcolor=COLOR_CARD,
        padding=18,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    form_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.MANAGE_ACCOUNTS, color=COLOR_PRIMARY, size=20),
                        ft.Text("Modifier mes informations", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                    spacing=8,
                ),
                ft.Divider(color=COLOR_BORDER, height=1),
                ft.Container(height=6),
                username_field,
                telephone_field,
                email_field,
                error_text,
                success_text,
                ft.Container(height=8),
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=18),
                            ft.Text("Enregistrer les modifications", weight=ft.FontWeight.BOLD, size=14),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    height=46,
                    bgcolor=COLOR_PRIMARY,
                    color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
                    on_click=handle_save,
                ),
            ],
            spacing=14,
        ),
        bgcolor=COLOR_CARD,
        padding=24,
        border_radius=16,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    if is_mobile:
        layout_content = ft.Column(
            [
                profile_header_card,
                form_card,
                security_notice_card,
            ],
            spacing=16,
        )
    else:
        layout_content = ft.Column(
            [
                profile_header_card,
                ft.Row(
                    [
                        ft.Container(content=form_card, expand=2),
                        ft.Container(content=security_notice_card, expand=1),
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=16,
        )

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=16),
                ft.Row(
                    [
                        ft.Text("Mon profil", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                ),
                ft.Container(height=12),
                layout_content,
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=ft.Padding.only(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content