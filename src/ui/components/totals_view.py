import flet as ft
from decimal import Decimal
from src.domain.models import Invoice

class TotalsViewComponent(ft.Container):
    def __init__(self):
        self.lbl_subtotal = ft.Text("₹0.00", weight=ft.FontWeight.BOLD, size=13)
        self.lbl_cgst = ft.Text("₹0.00", size=13)
        self.lbl_sgst = ft.Text("₹0.00", size=13)
        self.lbl_total_tax = ft.Text("₹0.00", weight=ft.FontWeight.BOLD, size=13)
        self.lbl_grand_total = ft.Text("₹0.00", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.BLUE_900)
        self.lbl_words = ft.Text("INR Zero Rupees Only", italic=True, size=12, color=ft.Colors.GREY_800)

        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Amount & Tax Words:", weight=ft.FontWeight.BOLD, size=12),
                            self.lbl_words,
                        ],
                        expand=2,
                        spacing=4,
                    ),
                    ft.Column(
                        controls=[
                            ft.Row([ft.Text("Taxable Subtotal:", expand=1), self.lbl_subtotal]),
                            ft.Row([ft.Text("Total CGST:", expand=1), self.lbl_cgst]),
                            ft.Row([ft.Text("Total SGST:", expand=1), self.lbl_sgst]),
                            ft.Row([ft.Text("Total Tax:", expand=1), self.lbl_total_tax]),
                            ft.Divider(height=1),
                            ft.Row([ft.Text("Grand Total:", expand=1, weight=ft.FontWeight.BOLD, size=14), self.lbl_grand_total]),
                        ],
                        expand=1,
                        spacing=4,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=ft.Padding.all(12),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
            border=ft.Border.all(1, ft.Colors.BLUE_200),
        )

    def update_totals(self, invoice: Invoice):
        self.lbl_subtotal.value = f"₹{invoice.subtotal:.2f}"
        self.lbl_cgst.value = f"₹{invoice.total_cgst:.2f}"
        self.lbl_sgst.value = f"₹{invoice.total_sgst:.2f}"
        self.lbl_total_tax.value = f"₹{invoice.total_tax:.2f}"
        self.lbl_grand_total.value = f"₹{invoice.grand_total:.2f}"
        self.lbl_words.value = invoice.amount_in_words
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

