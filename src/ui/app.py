import os
import flet as ft
from src.domain.models import Invoice
from src.domain.gst_engine import calculate_invoice
from src.db.repository import InvoiceRepository
from src.pdf.generator import PDFGenerator
from src.services.config import ConfigService, AppConfig
from src.services.numbering import InvoiceNumberService
from src.services.print_service import PrintService

from src.ui.components.company_header import CompanyHeaderComponent
from src.ui.components.customer_form import CustomerFormComponent
from src.ui.components.item_table import ItemTableComponent
from src.ui.components.totals_view import TotalsViewComponent
from src.ui.components.preview_panel import ActionPanelComponent
from src.ui.components.history_view import HistoryViewComponent
from src.ui.components.settings_view import SettingsViewComponent

def main(page: ft.Page):
    page.title = "Sai Krishna Networks - GST Invoice Generator"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.Padding.all(16)

    config_service = ConfigService()
    repo = InvoiceRepository(db_path=config_service.get_db_path())
    pdf_gen = PDFGenerator()

    # Load active company settings from SQLite
    company_settings = repo.get_company_settings()

    # Invoice Generator Tab Components
    company_comp = CompanyHeaderComponent(company_settings)
    totals_comp = TotalsViewComponent()

    customer_comp = None
    item_table_comp = None
    history_view = None

    def get_next_invoice_number() -> str:
        existing_numbers = repo.get_all_invoice_numbers()
        return InvoiceNumberService.generate_next_number(existing_numbers)

    def build_current_invoice() -> Invoice:
        if customer_comp is None or item_table_comp is None:
            return Invoice(company=company_settings)
        customer = customer_comp.get_customer()
        items = item_table_comp.get_items()
        invoice = Invoice(
            invoice_number=customer_comp.get_invoice_number(),
            invoice_date=customer_comp.get_invoice_date(),
            company=company_settings,
            customer=customer,
            items=items,
        )
        calculate_invoice(invoice)
        return invoice

    def on_form_change():
        invoice = build_current_invoice()
        totals_comp.update_totals(invoice)

    customer_comp = CustomerFormComponent(on_form_change)
    item_table_comp = ItemTableComponent(on_form_change)

    # Initialize with next sequential number (while remaining editable by user)
    customer_comp.set_invoice_number(get_next_invoice_number())

    def handle_new_invoice():
        next_num = get_next_invoice_number()
        customer_comp.reset(next_num)
        item_table_comp.reset()
        on_form_change()
        action_comp.set_status(f"Started fresh invoice #{next_num}")

    def handle_save_draft():
        try:
            invoice = build_current_invoice()
            invoice_id = repo.save_invoice(invoice)
            action_comp.set_status(f"Draft saved to SQLite DB successfully! (ID: {invoice_id}) at {repo.db_path}")
            if history_view:
                history_view.refresh_list()
        except Exception as e:
            action_comp.set_status(f"Error saving draft: {e}", is_error=True)

    def handle_export_pdf():
        try:
            invoice = build_current_invoice()
            clean_num = invoice.invoice_number.replace("/", "_").replace("\\", "_")
            if not clean_num:
                clean_num = "draft_invoice"
            pdf_dir = config_service.get_pdf_export_dir()
            os.makedirs(pdf_dir, exist_ok=True)
            output_pdf = os.path.join(pdf_dir, f"Invoice_{clean_num}.pdf")
            
            pdf_gen.generate_pdf(invoice, output_pdf)
            action_comp.set_status(f"PDF generated successfully at: {output_pdf}")
        except Exception as e:
            action_comp.set_status(f"Error generating PDF: {e}", is_error=True)

    def handle_print_invoice():
        try:
            invoice = build_current_invoice()
            clean_num = invoice.invoice_number.replace("/", "_").replace("\\", "_")
            if not clean_num:
                clean_num = "draft_invoice"
            pdf_dir = config_service.get_pdf_export_dir()
            os.makedirs(pdf_dir, exist_ok=True)
            output_pdf = os.path.join(pdf_dir, f"Invoice_{clean_num}.pdf")

            pdf_gen.generate_pdf(invoice, output_pdf)
            success, msg = PrintService.print_pdf(output_pdf)
            action_comp.set_status(msg, is_error=not success)
        except Exception as e:
            action_comp.set_status(f"Error printing invoice: {e}", is_error=True)

    action_comp = ActionPanelComponent(
        on_save_draft=handle_save_draft,
        on_export_pdf=handle_export_pdf,
        on_print=handle_print_invoice,
        on_new_invoice=handle_new_invoice,
    )

    # Main Invoice Generator View Container
    invoice_view = ft.Column(
        controls=[
            company_comp,
            customer_comp,
            item_table_comp,
            totals_comp,
            action_comp,
        ],
        spacing=12,
    )

    # Handler when opening an invoice from History
    def open_invoice_from_history(invoice_number: str):
        inv = repo.get_invoice_by_number(invoice_number)
        if not inv:
            return
        customer_comp.load_customer(inv.customer, inv.invoice_number, inv.invoice_date)
        item_table_comp.load_items(inv.items)
        on_form_change()

        # Switch view to tab 0 (Create Invoice)
        nav_tabs.selected_index = 0
        content_area.content = invoice_view
        action_comp.set_status(f"Loaded invoice #{inv.invoice_number} into editor.")
        page.update()

    # Invoice History View Component
    history_view = HistoryViewComponent(
        repository=repo,
        pdf_generator=pdf_gen,
        config_service=config_service,
        on_open_invoice=open_invoice_from_history,
    )

    # Callback when settings are saved
    def on_settings_saved(new_company_settings, new_config):
        nonlocal company_settings, repo
        company_settings = new_company_settings
        repo = InvoiceRepository(db_path=new_config.db_path)
        repo.save_company_settings(company_settings)
        company_comp.update_company(company_settings)
        if history_view:
            history_view.repo = repo
            history_view.refresh_list()
        on_form_change()

    # Settings View Component
    settings_view = SettingsViewComponent(
        company_settings=company_settings,
        config_service=config_service,
        on_save_callback=on_settings_saved,
    )

    # Views Container
    content_area = ft.Container(content=invoice_view, expand=True)

    def on_tab_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            content_area.content = invoice_view
        elif selected_index == 1:
            history_view.refresh_list()
            content_area.content = history_view
        else:
            content_area.content = settings_view
        page.update()

    # Top Navigation Bar (3 Tabs)
    nav_tabs = ft.Tabs(
        length=3,
        selected_index=0,
        animation_duration=200,
        on_change=on_tab_change,
        content=ft.TabBar(
            tabs=[
                ft.Tab(label="Create Invoice", icon=ft.Icons.RECEIPT_LONG),
                ft.Tab(label="Invoice History", icon=ft.Icons.HISTORY),
                ft.Tab(label="Company & Storage Settings", icon=ft.Icons.SETTINGS),
            ]
        ),
    )

    # Welcome Dialog for First-Time Setup
    if config_service.is_first_run():
        dlg_db_dir = ft.TextField(label="SQLite Database Folder", value=config_service.config.db_directory, dense=True)
        dlg_pdf_dir = ft.TextField(label="PDF Invoices Export Folder", value=config_service.config.pdf_export_directory, dense=True)

        def confirm_first_run(e):
            new_cfg = AppConfig(
                db_directory=dlg_db_dir.value.strip(),
                pdf_export_directory=dlg_pdf_dir.value.strip(),
                is_configured=True,
            )
            config_service.save_config(new_cfg)
            repo.db_path = new_cfg.db_path
            repo._init_db()
            repo.save_company_settings(company_settings)
            welcome_dialog.open = False
            page.update()

        welcome_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Welcome to SKN Invoice Generator", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Please confirm the storage locations for your data and invoices outside the application:", size=12),
                    dlg_db_dir,
                    dlg_pdf_dir,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.Button("Confirm & Continue", on_click=confirm_first_run),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = welcome_dialog
        welcome_dialog.open = True

    page.add(
        nav_tabs,
        ft.Divider(height=1, color=ft.Colors.GREY_300),
        content_area,
    )

    # Initial calculation trigger
    on_form_change()

if __name__ == "__main__":
    ft.app(target=main)

