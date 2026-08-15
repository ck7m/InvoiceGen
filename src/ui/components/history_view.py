import os
import flet as ft
from typing import Callable, List
from src.db.repository import InvoiceRepository
from src.pdf.generator import PDFGenerator
from src.services.print_service import PrintService
from src.services.config import ConfigService

class HistoryViewComponent(ft.Container):
    def __init__(
        self,
        repository: InvoiceRepository,
        pdf_generator: PDFGenerator,
        config_service: ConfigService,
        on_open_invoice: Callable[[str], None],
    ):
        self.repo = repository
        self.pdf_gen = pdf_generator
        self.config_service = config_service
        self.on_open_invoice = on_open_invoice

        self.txt_search = ft.TextField(
            label="Search Invoices",
            hint_text="Search by Invoice No, Customer Name, or Date...",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            expand=True,
            on_change=lambda _: self.refresh_list(),
        )

        self.btn_refresh = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh History List",
            on_click=lambda _: self.refresh_list(),
        )

        self.txt_status = ft.Text("", size=12, color=ft.Colors.GREEN_800, weight=ft.FontWeight.BOLD)

        self.list_container = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        super().__init__(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.HISTORY, size=28, color=ft.Colors.BLUE_800),
                            ft.Text("Invoice History & Management", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_300),

                    # Search & Action bar
                    ft.Row(
                        controls=[
                            self.txt_search,
                            self.btn_refresh,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.txt_status,

                    # Invoices Table Container
                    self.list_container,
                ],
                spacing=12,
                expand=True,
            ),
            padding=ft.Padding.all(16),
            expand=True,
        )

        # Initial load
        self.refresh_list()

    def refresh_list(self):
        query = self.txt_search.value.strip() if self.txt_search.value else ""
        invoices = self.repo.list_invoices(search_query=query)

        self.list_container.controls.clear()

        if not invoices:
            empty_msg = "No historical invoices found." if not query else f"No invoices matching '{query}'."
            self.list_container.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=48, color=ft.Colors.GREY_400),
                            ft.Text(empty_msg, color=ft.Colors.GREY_600, size=14),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.all(40),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for inv in invoices:
                card = self._build_invoice_card(inv)
                self.list_container.controls.append(card)

        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def _build_invoice_card(self, inv: dict) -> ft.Container:
        inv_num = inv["invoice_number"]
        inv_date = inv["invoice_date"]
        cust_name = inv["customer_name"]
        item_count = inv["item_count"]
        grand_total = inv["grand_total"]
        taxable = inv["subtotal"]
        tax = inv["total_tax"]

        btn_open = ft.FilledButton(
            "Open in Editor",
            icon=ft.Icons.EDIT_DOCUMENT,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE),
            on_click=lambda _, num=inv_num: self.on_open_invoice(num),
        )

        btn_pdf = ft.OutlinedButton(
            "Export PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=lambda _, num=inv_num: self._export_pdf(num),
        )

        btn_print = ft.OutlinedButton(
            "Print",
            icon=ft.Icons.PRINT,
            on_click=lambda _, num=inv_num: self._print_invoice(num),
        )

        btn_delete = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_600,
            tooltip="Delete Invoice",
            on_click=lambda _, num=inv_num: self._delete_invoice(num),
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    # Left info
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(inv_num, size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                                    ft.Container(
                                        content=ft.Text(f"{inv_date}", size=11, color=ft.Colors.GREY_700),
                                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                        bgcolor=ft.Colors.GREY_100,
                                        border_radius=4,
                                    ),
                                ],
                                spacing=10,
                            ),
                            ft.Text(f"Customer: {cust_name}", size=13, weight=ft.FontWeight.W_500),
                            ft.Text(f"Items: {item_count} | Taxable: ₹{taxable} | Tax: ₹{tax}", size=11, color=ft.Colors.GREY_600),
                        ],
                        spacing=4,
                        expand=True,
                    ),

                    # Right Amount & Actions
                    ft.Column(
                        controls=[
                            ft.Text(f"₹ {grand_total}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800),
                            ft.Row(
                                controls=[btn_open, btn_pdf, btn_print, btn_delete],
                                spacing=6,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=4,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.all(12),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
        )

    def _export_pdf(self, invoice_number: str):
        invoice = self.repo.get_invoice_by_number(invoice_number)
        if not invoice:
            self.set_status(f"Invoice {invoice_number} not found.", is_error=True)
            return

        try:
            clean_num = invoice_number.replace("/", "_").replace("\\", "_")
            pdf_dir = self.config_service.get_pdf_export_dir()
            os.makedirs(pdf_dir, exist_ok=True)
            output_pdf = os.path.join(pdf_dir, f"Invoice_{clean_num}.pdf")
            self.pdf_gen.generate_pdf(invoice, output_pdf)
            self.set_status(f"PDF generated successfully at: {output_pdf}")
        except Exception as e:
            self.set_status(f"Error exporting PDF: {e}", is_error=True)

    def _print_invoice(self, invoice_number: str):
        invoice = self.repo.get_invoice_by_number(invoice_number)
        if not invoice:
            self.set_status(f"Invoice {invoice_number} not found.", is_error=True)
            return

        try:
            clean_num = invoice_number.replace("/", "_").replace("\\", "_")
            pdf_dir = self.config_service.get_pdf_export_dir()
            os.makedirs(pdf_dir, exist_ok=True)
            output_pdf = os.path.join(pdf_dir, f"Invoice_{clean_num}.pdf")
            self.pdf_gen.generate_pdf(invoice, output_pdf)
            success, msg = PrintService.print_pdf(output_pdf)
            self.set_status(msg, is_error=not success)
        except Exception as e:
            self.set_status(f"Error printing: {e}", is_error=True)

    def _delete_invoice(self, invoice_number: str):
        deleted = self.repo.delete_invoice(invoice_number)
        if deleted:
            self.set_status(f"Invoice {invoice_number} deleted from SQLite.")
            self.refresh_list()
        else:
            self.set_status(f"Failed to delete {invoice_number}.", is_error=True)

    def set_status(self, message: str, is_error: bool = False):
        self.txt_status.value = message
        self.txt_status.color = ft.Colors.RED_700 if is_error else ft.Colors.GREEN_800
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass
