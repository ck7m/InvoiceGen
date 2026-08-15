import flet as ft
from datetime import datetime
from src.domain.models import Customer

class CustomerFormComponent(ft.Container):
    def __init__(self, on_change_callback):
        self.on_change_callback = on_change_callback

        self.txt_inv_number = ft.TextField(
            label="Invoice Number",
            value="SKN/2026-27/001",
            dense=True,
            expand=1,
            on_change=self.on_change_callback,
        )
        self.txt_inv_date = ft.TextField(
            label="Invoice Date",
            value=datetime.now().strftime("%Y-%m-%d"),
            dense=True,
            expand=1,
            on_change=self.on_change_callback,
        )

        self.txt_cust_name = ft.TextField(
            label="Customer Name",
            value="Grand Cyber Tech Systems India Ltd",
            dense=True,
            expand=2,
            on_change=self.on_change_callback,
        )
        self.txt_cust_gstin = ft.TextField(
            label="Customer GSTIN",
            value="37AAACG1234F1Z9",
            dense=True,
            expand=1,
            on_change=self.on_change_callback,
        )
        self.txt_cust_state = ft.TextField(
            label="State",
            value="Andhra Pradesh",
            dense=True,
            expand=1,
            on_change=self.on_change_callback,
        )
        self.txt_cust_address = ft.TextField(
            label="Customer Address",
            value="Plot 45, IT Park, Mangalagiri, Guntur District, AP - 522503",
            multiline=True,
            min_lines=2,
            max_lines=3,
            dense=True,
            expand=True,
            on_change=self.on_change_callback,
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("Invoice & Customer Information", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_800),
                    ft.Row([self.txt_inv_number, self.txt_inv_date]),
                    ft.Row([self.txt_cust_name, self.txt_cust_gstin, self.txt_cust_state]),
                    ft.Row([self.txt_cust_address]),
                ],
                spacing=10,
            ),
            padding=ft.Padding.all(12),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
        )

    def get_customer(self) -> Customer:
        return Customer(
            customer_name=self.txt_cust_name.value.strip(),
            customer_address=self.txt_cust_address.value.strip(),
            customer_gstin=self.txt_cust_gstin.value.strip(),
            customer_state=self.txt_cust_state.value.strip(),
            customer_state_code="37" if "Andhra" in self.txt_cust_state.value else "",
        )

    def get_invoice_number(self) -> str:
        return self.txt_inv_number.value.strip()

    def get_invoice_date(self) -> str:
        return self.txt_inv_date.value.strip()

    def set_invoice_number(self, invoice_number: str):
        self.txt_inv_number.value = invoice_number
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def load_customer(self, customer: Customer, invoice_number: str, invoice_date: str):
        self.txt_inv_number.value = invoice_number
        self.txt_inv_date.value = invoice_date
        self.txt_cust_name.value = customer.customer_name
        self.txt_cust_address.value = customer.customer_address
        self.txt_cust_gstin.value = customer.customer_gstin
        self.txt_cust_state.value = customer.customer_state
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def reset(self, next_invoice_number: str = "SKN/2026-27/001"):
        self.txt_inv_number.value = next_invoice_number
        self.txt_inv_date.value = datetime.now().strftime("%Y-%m-%d")
        self.txt_cust_name.value = ""
        self.txt_cust_address.value = ""
        self.txt_cust_gstin.value = ""
        self.txt_cust_state.value = "Andhra Pradesh"
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

