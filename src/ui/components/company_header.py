import flet as ft
from src.domain.models import CompanySettings

class CompanyHeaderComponent(ft.Container):
    def __init__(self, company: CompanySettings):
        self.company = company
        self.lbl_title = ft.Text(self.company.company_name, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
        self.lbl_subtitle = ft.Text(
            f"GSTIN: {self.company.gstin} | State: {self.company.state} (Code: {self.company.state_code})",
            size=12,
            color=ft.Colors.GREY_700,
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.RECEIPT_LONG, size=32, color=ft.Colors.BLUE_700),
                            ft.Column(
                                controls=[
                                    self.lbl_title,
                                    self.lbl_subtitle,
                                ],
                                spacing=2,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                ],
                spacing=8,
            ),
            padding=ft.Padding.all(12),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
        )

    def update_company(self, company: CompanySettings):
        self.company = company
        self.lbl_title.value = self.company.company_name
        self.lbl_subtitle.value = f"GSTIN: {self.company.gstin} | State: {self.company.state} (Code: {self.company.state_code})"
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass
