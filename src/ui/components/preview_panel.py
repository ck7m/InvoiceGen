import flet as ft
from typing import Callable

class ActionPanelComponent(ft.Container):
    def __init__(
        self,
        on_save_draft: Callable,
        on_export_pdf: Callable,
        on_print: Callable = None,
        on_new_invoice: Callable = None,
    ):
        self.on_save_draft = on_save_draft
        self.on_export_pdf = on_export_pdf
        self.on_print = on_print
        self.on_new_invoice = on_new_invoice

        btn_new = ft.OutlinedButton(
            "New Invoice",
            icon=ft.Icons.ADD_BOX,
            on_click=lambda _: self.on_new_invoice() if self.on_new_invoice else None,
        )

        btn_save = ft.FilledButton(
            "Save Draft (SQLite)",
            icon=ft.Icons.SAVE_OUTLINED,
            on_click=lambda _: self.on_save_draft(),
        )

        btn_pdf = ft.FilledButton(
            "Export PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_700,
                color=ft.Colors.WHITE,
            ),
            on_click=lambda _: self.on_export_pdf(),
        )

        btn_print = ft.FilledButton(
            "Print",
            icon=ft.Icons.PRINT,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_GREY_700,
                color=ft.Colors.WHITE,
            ),
            on_click=lambda _: self.on_print() if self.on_print else None,
        )

        self.txt_status = ft.Text("", size=12, color=ft.Colors.GREEN_800, weight=ft.FontWeight.BOLD)

        action_buttons = [btn_new, btn_save, btn_pdf]
        if self.on_print:
            action_buttons.append(btn_print)

        super().__init__(
            content=ft.Row(
                controls=[
                    self.txt_status,
                    ft.Row(action_buttons, spacing=10),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.all(10),
        )

    def set_status(self, message: str, is_error: bool = False):
        self.txt_status.value = message
        self.txt_status.color = ft.Colors.RED_700 if is_error else ft.Colors.GREEN_800
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass


