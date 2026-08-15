import flet as ft
from decimal import Decimal, InvalidOperation
from typing import List, Callable
from src.domain.models import InvoiceItem
from src.domain.gst_engine import calculate_item

class ItemRowControl(ft.Container):
    def __init__(self, index: int, item: InvoiceItem, on_change: Callable, on_delete: Callable):
        self.index = index
        self.on_change_callback = on_change
        self.on_delete_callback = on_delete

        self.txt_desc = ft.TextField(
            value=item.description,
            multiline=True,
            min_lines=1,
            max_lines=4,
            dense=True,
            expand=True,
            hint_text="Item description...",
            on_change=self._handle_change,
        )
        self.txt_batch = ft.TextField(
            value=item.batch_number,
            dense=True,
            width=70,
            hint_text="Batch",
            on_change=self._handle_change,
        )
        self.txt_hsn = ft.TextField(
            value=item.hsn_sac,
            dense=True,
            width=85,
            hint_text="HSN/SAC",
            on_change=self._handle_change,
        )
        self.txt_qty = ft.TextField(
            value=str(item.quantity),
            dense=True,
            width=65,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._handle_change,
        )
        self.txt_rate = ft.TextField(
            value=str(item.rate),
            dense=True,
            width=90,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._handle_change,
        )
        self.txt_cgst = ft.TextField(
            value=str(item.cgst_percent),
            dense=True,
            width=60,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._handle_change,
        )
        self.txt_sgst = ft.TextField(
            value=str(item.sgst_percent),
            dense=True,
            width=60,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._handle_change,
        )

        # Calculated display fields
        self.lbl_taxable = ft.Text(value="₹0.00", weight=ft.FontWeight.BOLD, size=11)
        self.lbl_cgst_amt = ft.Text(value="₹0.00", size=11)
        self.lbl_sgst_amt = ft.Text(value="₹0.00", size=11)
        self.lbl_amount = ft.Text(value="₹0.00", weight=ft.FontWeight.BOLD, size=11, color=ft.Colors.BLUE_900)

        self.btn_delete = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINED,
            icon_color=ft.Colors.RED_400,
            tooltip="Remove row",
            width=40,
            on_click=lambda _: self.on_delete_callback(self),
        )

        self.update_calculations()

        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Container(ft.Text(f"{self.index}", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD), width=25),
                    self.txt_desc,
                    self.txt_batch,
                    self.txt_hsn,
                    self.txt_qty,
                    self.txt_rate,
                    self.txt_cgst,
                    self.txt_sgst,
                    ft.Container(self.lbl_taxable, width=85, alignment=ft.Alignment.CENTER_RIGHT),
                    ft.Container(self.lbl_cgst_amt, width=75, alignment=ft.Alignment.CENTER_RIGHT),
                    ft.Container(self.lbl_sgst_amt, width=75, alignment=ft.Alignment.CENTER_RIGHT),
                    ft.Container(self.lbl_amount, width=95, alignment=ft.Alignment.CENTER_RIGHT),
                    self.btn_delete,
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=4, horizontal=6),
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
        )

    def parse_decimal(self, text: str, default: str = "0.00") -> Decimal:
        try:
            val = text.strip()
            if not val:
                return Decimal(default)
            return Decimal(val)
        except InvalidOperation:
            return Decimal(default)

    def update_calculations(self):
        qty = self.parse_decimal(self.txt_qty.value, "0.00")
        rate = self.parse_decimal(self.txt_rate.value, "0.00")
        cgst_pct = self.parse_decimal(self.txt_cgst.value, "9.00")
        sgst_pct = self.parse_decimal(self.txt_sgst.value, "9.00")

        taxable, cgst_amt, sgst_amt, total_tax, rate_with_tax, amount_with_tax = calculate_item(
            qty, rate, cgst_pct, sgst_pct
        )

        self.lbl_taxable.value = f"₹{taxable:.2f}"
        self.lbl_cgst_amt.value = f"₹{cgst_amt:.2f}"
        self.lbl_sgst_amt.value = f"₹{sgst_amt:.2f}"
        self.lbl_amount.value = f"₹{amount_with_tax:.2f}"

    def _handle_change(self, e):
        self.update_calculations()
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass
        self.on_change_callback()

    def get_invoice_item(self) -> InvoiceItem:
        qty = self.parse_decimal(self.txt_qty.value, "0.00")
        rate = self.parse_decimal(self.txt_rate.value, "0.00")
        cgst_pct = self.parse_decimal(self.txt_cgst.value, "9.00")
        sgst_pct = self.parse_decimal(self.txt_sgst.value, "9.00")

        return InvoiceItem(
            serial_number=self.index,
            description=self.txt_desc.value.strip(),
            batch_number=self.txt_batch.value.strip(),
            hsn_sac=self.txt_hsn.value.strip(),
            quantity=qty,
            rate=rate,
            cgst_percent=cgst_pct,
            sgst_percent=sgst_pct,
        )


class ItemTableComponent(ft.Container):
    def __init__(self, on_change_callback: Callable):
        self.on_change_callback = on_change_callback
        self.rows: List[ItemRowControl] = []
        self.rows_column = ft.Column(spacing=0)

        # Header titles strictly aligned with column widths
        headers = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(ft.Text("#", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD), width=25),
                    ft.Container(ft.Text("Description of Goods", weight=ft.FontWeight.BOLD), expand=True),
                    ft.Container(ft.Text("Batch", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD), width=70),
                    ft.Container(ft.Text("HSN/SAC", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD), width=85),
                    ft.Container(ft.Text("Qty", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD), width=65),
                    ft.Container(ft.Text("Rate (₹)", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD), width=90),
                    ft.Container(ft.Text("CGST%", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD), width=60),
                    ft.Container(ft.Text("SGST%", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD), width=60),
                    ft.Container(ft.Text("Taxable", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD), width=85),
                    ft.Container(ft.Text("CGST (₹)", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD), width=75),
                    ft.Container(ft.Text("SGST (₹)", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD), width=75),
                    ft.Container(ft.Text("Amount (₹)", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD), width=95),
                    ft.Container(ft.Text(""), width=40),  # Action space
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLUE_100,
            padding=ft.Padding.symmetric(vertical=8, horizontal=6),
            border_radius=4,
        )

        btn_add = ft.Button(
            "Add Item Row",
            icon=ft.Icons.ADD,
            on_click=lambda _: self.add_row(),
        )

        btn_load_proto = ft.OutlinedButton(
            "Load Prototype Test Suite Data",
            icon=ft.Icons.SCIENCE,
            on_click=lambda _: self.load_prototype_data(),
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    headers,
                    self.rows_column,
                    ft.Row([btn_add, btn_load_proto], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ],
                spacing=10,
            ),
            padding=ft.Padding.all(10),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
        )

        # Initial default row
        self.add_row()

    def add_row(self, item: InvoiceItem = None):
        if item is None:
            item = InvoiceItem()
        index = len(self.rows) + 1
        row = ItemRowControl(index, item, self.on_change_callback, self.remove_row)
        self.rows.append(row)
        self.rows_column.controls.append(row)
        self._reindex_rows()
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass
        self.on_change_callback()

    def remove_row(self, row: ItemRowControl):
        if len(self.rows) <= 1:
            return  # Keep at least 1 row
        self.rows.remove(row)
        self.rows_column.controls.remove(row)
        self._reindex_rows()
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass
        self.on_change_callback()

    def load_prototype_data(self):
        """Populate mandatory prototype test items (Dell Laptop, Long multi-line desc, Short desc)."""
        self.rows.clear()
        self.rows_column.controls.clear()

        item1 = InvoiceItem(
            description="Dell Latitude Laptop 5420 - 14 inch FHD, Intel Core i7, 16GB RAM, 512GB SSD, Windows 11 Pro",
            batch_number="B001",
            hsn_sac="84713010",
            quantity=Decimal("2.00"),
            rate=Decimal("82627.12"),
            cgst_percent=Decimal("9.00"),
            sgst_percent=Decimal("9.00"),
        )
        item2 = InvoiceItem(
            description=(
                "Network Infrastructure Setup & Managed IT Services:\n"
                "- Category 6A UTP Cable installation and patch panel termination across 4 floors\n"
                "- Managed Gigabit Ethernet Switches (48-port PoE+) configuration with VLAN segmentation\n"
                "- Dual WAN Gateway router setup with load balancing and failover rules\n"
                "- Rack mounting, cable management, labeling, certification testing, and 3-year warranty SLA."
            ),
            batch_number="SRV-2026",
            hsn_sac="998313",
            quantity=Decimal("1.00"),
            rate=Decimal("150000.00"),
            cgst_percent=Decimal("9.00"),
            sgst_percent=Decimal("9.00"),
        )
        item3 = InvoiceItem(
            description="Cat6 Patch Cord 1m",
            batch_number="ACC-01",
            hsn_sac="85444299",
            quantity=Decimal("10.00"),
            rate=Decimal("250.00"),
            cgst_percent=Decimal("9.00"),
            sgst_percent=Decimal("9.00"),
        )

        for item in [item1, item2, item3]:
            self.add_row(item)

    def _reindex_rows(self):
        for idx, row in enumerate(self.rows, start=1):
            row.index = idx
            row.content.controls[0].content.value = str(idx)

    def load_items(self, items: List[InvoiceItem]):
        """Populate items from an existing invoice."""
        self.rows.clear()
        self.rows_column.controls.clear()
        if not items:
            self.add_row()
        else:
            for item in items:
                self.add_row(item)

    def reset(self):
        """Reset item table to 1 blank row."""
        self.rows.clear()
        self.rows_column.controls.clear()
        self.add_row()

    def get_items(self) -> List[InvoiceItem]:
        return [row.get_invoice_item() for row in self.rows]

