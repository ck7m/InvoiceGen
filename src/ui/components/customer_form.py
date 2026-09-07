import flet as ft
from datetime import datetime
from typing import Callable, List, Optional
from src.domain.models import Customer

class CustomerFormComponent(ft.Container):
    def __init__(
        self,
        on_change_callback: Callable,
        on_search_customer: Optional[Callable[[str], List[Customer]]] = None,
        on_save_customer: Optional[Callable[[Customer], int]] = None,
    ):
        self.on_change_callback = on_change_callback
        self.on_search_customer = on_search_customer
        self.on_save_customer = on_save_customer
        self._suppress_search = False

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
        self.txt_po_number = ft.TextField(
            label="PO Number",
            value="",
            hint_text="e.g. PO-2026-001",
            dense=True,
            expand=1,
            on_change=self.on_change_callback,
        )
        self.txt_po_date = ft.TextField(
            label="PO Date",
            value="",
            hint_text="YYYY-MM-DD",
            dense=True,
            expand=1,
            on_change=self.on_change_callback,
        )

        self.dd_inv_type = ft.Dropdown(
            label="Invoice Type",
            value="Original",
            options=[
                ft.dropdown.Option("Original"),
                ft.dropdown.Option("Duplicate"),
                ft.dropdown.Option("Transport"),
            ],
            dense=True,
            expand=1,
            on_select=lambda e: self.on_change_callback(e),
        )
        self.dd_terms = ft.Dropdown(
            label="Terms of Payment",
            value="100% Advance",
            options=[
                ft.dropdown.Option("100% Advance"),
                ft.dropdown.Option("30 days Credit"),
                ft.dropdown.Option("45 days credit"),
            ],
            dense=True,
            expand=1,
            on_select=lambda e: self.on_change_callback(e),
        )

        self.txt_cust_name = ft.TextField(
            label="Customer Name",
            value="",
            hint_text="Type name to search or enter new",
            dense=True,
            expand=2,
            on_change=self._handle_customer_input_change,
        )
        self.txt_cust_gstin = ft.TextField(
            label="Customer GSTIN",
            value="",
            hint_text="15-character GSTIN",
            dense=True,
            expand=1,
            on_change=self._handle_customer_input_change,
        )
        self.txt_cust_state = ft.TextField(
            label="State",
            value="Tamilnadu",
            dense=True,
            expand=1,
            on_change=self.on_change_callback,
        )
        self.txt_cust_address = ft.TextField(
            label="Customer Address",
            value="",
            multiline=True,
            min_lines=2,
            max_lines=3,
            dense=True,
            expand=True,
            on_change=self.on_change_callback,
        )

        self.txt_edit_notice = ft.Text(
            "",
            size=11,
            color=ft.Colors.GREEN_800,
            weight=ft.FontWeight.W_500,
            visible=False,
        )

        btn_save_cust = ft.TextButton(
            "Save / Update Customer in DB",
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(color=ft.Colors.BLUE_800),
            tooltip="Save or update these customer details in the SQLite database",
            on_click=self._handle_manual_save_customer,
        )

        # Scrollable container for matches, capped to 160px so it never takes up the whole screen
        self.suggestions_column = ft.Column(
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
        )
        self.txt_suggestions_title = ft.Text(
            "Saved Customers (Click to load details):",
            weight=ft.FontWeight.BOLD,
            size=12,
            color=ft.Colors.BLUE_900,
        )
        self.suggestions_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.PEOPLE, size=16, color=ft.Colors.BLUE_700),
                                        self.txt_suggestions_title,
                                    ],
                                    spacing=6,
                                ),
                                ft.IconButton(
                                    ft.Icons.CLOSE,
                                    icon_size=14,
                                    tooltip="Dismiss",
                                    on_click=lambda _: self.hide_suggestions(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        # Capped container to ensure it never occupies whole screen
                        ft.Container(
                            content=self.suggestions_column,
                            height=160,
                        ),
                    ],
                    spacing=6,
                ),
                padding=8,
            ),
            visible=False,
        )

        header_row = ft.Row(
            [
                ft.Text(
                    "Invoice & Customer Information",
                    weight=ft.FontWeight.BOLD,
                    size=14,
                    color=ft.Colors.BLUE_800,
                ),
                ft.Row([self.txt_edit_notice, btn_save_cust], spacing=8),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    header_row,
                    ft.Row([self.txt_inv_number, self.txt_inv_date, self.txt_po_number, self.txt_po_date]),
                    ft.Row([self.dd_terms, self.dd_inv_type]),
                    ft.Row([self.txt_cust_name, self.txt_cust_gstin, self.txt_cust_state]),
                    self.suggestions_card,
                    ft.Row([self.txt_cust_address]),
                ],
                spacing=10,
            ),
            padding=ft.Padding.all(12),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
        )

    def _get_state_code(self, state_name: str) -> str:
        s = state_name.lower().replace(" ", "").replace("-", "")
        if "tamil" in s:
            return "33"
        elif "andhra" in s:
            return "37"
        elif "telangana" in s:
            return "36"
        elif "karnataka" in s:
            return "29"
        elif "kerala" in s:
            return "32"
        elif "maharashtra" in s:
            return "27"
        elif "delhi" in s:
            return "07"
        return "33" if "tamil" in s else ""

    def _handle_customer_input_change(self, e):
        # Call global change callback first
        self.on_change_callback(e)

        if self._suppress_search or not self.on_search_customer:
            return

        query = (e.control.value or "").strip()
        if len(query) < 2:
            self.hide_suggestions()
            return

        try:
            matches = self.on_search_customer(query)
        except Exception:
            matches = []

        if not matches:
            self.hide_suggestions()
            return

        # Always show matched customer options so the user can choose to load them,
        # or continue freely editing their text without the field getting overwritten!
        self._display_customer_choices(matches)

    def _display_customer_choices(self, customers: List[Customer]):
        self.suggestions_column.controls.clear()
        count = len(customers)
        self.txt_suggestions_title.value = (
            f"Found {count} saved customer{'s' if count != 1 else ''} (Click to load):"
        )
        for cust in customers:
            btn = ft.OutlinedButton(
                content=ft.Text(
                    f"{cust.customer_name} | GSTIN: {cust.customer_gstin or 'None'} | {cust.customer_state}",
                    size=12,
                ),
                icon=ft.Icons.PERSON,
                style=ft.ButtonStyle(alignment=ft.Alignment(-1, 0)),
                on_click=lambda _, c=cust: self.apply_customer(c),
            )
            self.suggestions_column.controls.append(btn)

        self.suggestions_card.visible = True
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def hide_suggestions(self):
        self.suggestions_card.visible = False
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def apply_customer(self, customer: Customer, trigger_callback: bool = True):
        self._suppress_search = True
        try:
            self.txt_cust_name.value = customer.customer_name
            self.txt_cust_gstin.value = customer.customer_gstin
            self.txt_cust_address.value = customer.customer_address
            self.txt_cust_state.value = customer.customer_state or "Tamilnadu"
            self.hide_suggestions()
            self.txt_edit_notice.value = "✓ Customer details loaded. All fields are editable."
            self.txt_edit_notice.visible = True
            if trigger_callback:
                self.on_change_callback(None)
            try:
                if self.page:
                    self.page.update()
            except RuntimeError:
                pass
        finally:
            self._suppress_search = False

    def _handle_manual_save_customer(self, _):
        cust = self.get_customer()
        if not cust.customer_name and not cust.customer_gstin:
            self.txt_edit_notice.value = "Enter Customer Name or GSTIN to save."
            self.txt_edit_notice.color = ft.Colors.RED_700
            self.txt_edit_notice.visible = True
        elif self.on_save_customer:
            try:
                self.on_save_customer(cust)
                self.txt_edit_notice.value = f"✓ '{cust.customer_name}' saved to DB!"
                self.txt_edit_notice.color = ft.Colors.GREEN_800
                self.txt_edit_notice.visible = True
            except Exception as ex:
                self.txt_edit_notice.value = f"Error saving: {ex}"
                self.txt_edit_notice.color = ft.Colors.RED_700
                self.txt_edit_notice.visible = True
        else:
            self.txt_edit_notice.value = "✓ Customer info ready."
            self.txt_edit_notice.visible = True

        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def get_customer(self) -> Customer:
        state_val = self.txt_cust_state.value.strip() if self.txt_cust_state.value else "Tamilnadu"
        return Customer(
            customer_name=self.txt_cust_name.value.strip(),
            customer_address=self.txt_cust_address.value.strip(),
            customer_gstin=self.txt_cust_gstin.value.strip(),
            customer_state=state_val,
            customer_state_code=self._get_state_code(state_val),
        )

    def get_invoice_number(self) -> str:
        return self.txt_inv_number.value.strip()

    def get_invoice_date(self) -> str:
        return self.txt_inv_date.value.strip()

    def get_po_number(self) -> str:
        return self.txt_po_number.value.strip()

    def get_po_date(self) -> str:
        return self.txt_po_date.value.strip()

    def get_invoice_type(self) -> str:
        return self.dd_inv_type.value or "Original"

    def get_terms_of_payment(self) -> str:
        return self.dd_terms.value or "100% Advance"

    def set_invoice_number(self, invoice_number: str):
        self.txt_inv_number.value = invoice_number
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def load_customer(
        self,
        customer: Customer,
        invoice_number: str,
        invoice_date: str,
        po_number: str = "",
        po_date: str = "",
        invoice_type: str = "Original",
        terms_of_payment: str = "100% Advance",
    ):
        self._suppress_search = True
        try:
            self.txt_inv_number.value = invoice_number
            self.txt_inv_date.value = invoice_date
            self.txt_po_number.value = po_number or ""
            self.txt_po_date.value = po_date or ""
            self.dd_inv_type.value = invoice_type or "Original"
            self.dd_terms.value = terms_of_payment or "100% Advance"
            self.txt_cust_name.value = customer.customer_name
            self.txt_cust_address.value = customer.customer_address
            self.txt_cust_gstin.value = customer.customer_gstin
            self.txt_cust_state.value = customer.customer_state or "Tamilnadu"
            self.hide_suggestions()
            self.txt_edit_notice.value = "✓ Customer loaded. Editable."
            self.txt_edit_notice.visible = True
            try:
                if self.page:
                    self.page.update()
            except RuntimeError:
                pass
        finally:
            self._suppress_search = False

    def reset(self, next_invoice_number: str = "SKN/2026-27/001"):
        self._suppress_search = True
        try:
            self.txt_inv_number.value = next_invoice_number
            self.txt_inv_date.value = datetime.now().strftime("%Y-%m-%d")
            self.txt_po_number.value = ""
            self.txt_po_date.value = ""
            self.dd_inv_type.value = "Original"
            self.dd_terms.value = "100% Advance"
            self.txt_cust_name.value = ""
            self.txt_cust_address.value = ""
            self.txt_cust_gstin.value = ""
            self.txt_cust_state.value = "Tamilnadu"
            self.txt_edit_notice.visible = False
            self.hide_suggestions()
            try:
                if self.page:
                    self.page.update()
            except RuntimeError:
                pass
        finally:
            self._suppress_search = False
