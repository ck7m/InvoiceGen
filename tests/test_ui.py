import pytest
from unittest.mock import MagicMock
import flet as ft
from src.ui.app import main
from src.domain.models import CompanySettings
from src.services.config import ConfigService
from src.ui.components.item_table import ItemTableComponent
from src.ui.components.customer_form import CustomerFormComponent
from src.ui.components.totals_view import TotalsViewComponent
from src.ui.components.settings_view import SettingsViewComponent

def test_ui_initialization():
    mock_page = MagicMock(spec=ft.Page)
    mock_page.add = MagicMock()
    
    # Should execute without any AttributeError or RuntimeError
    main(mock_page)
    assert mock_page.add.called

def test_item_table_prototype_data_loading():
    on_change_mock = MagicMock()
    table = ItemTableComponent(on_change_mock)
    
    assert len(table.rows) == 1
    
    table.load_prototype_data()
    assert len(table.rows) == 3
    
    items = table.get_items()
    assert len(items) == 3
    assert "Dell" in items[0].description
    assert items[0].quantity == pytest.approx(2.0)

def test_settings_view_component(tmp_path):
    config_file = str(tmp_path / "test_cfg.json")
    cfg_service = ConfigService(config_file=config_file)
    company = CompanySettings()
    on_save = MagicMock()

    settings_view = SettingsViewComponent(company, cfg_service, on_save)
    assert settings_view.txt_name.value == "Sai Krishna Networks"
    assert settings_view.txt_gstin.value == "37AAAAA0000A1Z5"

    settings_view.txt_name.value = "Updated SKN Ltd"
    settings_view._save_settings()

    assert on_save.called
    saved_company, saved_cfg = on_save.call_args[0]
    assert saved_company.company_name == "Updated SKN Ltd"

def test_history_view_component(tmp_path):
    from src.db.repository import InvoiceRepository
    from src.pdf.generator import PDFGenerator
    from src.ui.components.history_view import HistoryViewComponent
    from src.domain.models import Invoice, Customer, InvoiceItem
    from decimal import Decimal

    db_file = str(tmp_path / "hist_ui_test.db")
    repo = InvoiceRepository(db_path=db_file)
    pdf_gen = PDFGenerator()
    cfg_service = ConfigService(config_file=str(tmp_path / "cfg.json"))

    # Save a sample invoice
    inv = Invoice(
        invoice_number="SKN/2026-27/001",
        invoice_date="2026-08-16",
        customer=Customer(customer_name="Tech Solutions Ltd"),
        items=[InvoiceItem(description="Item 1", rate=Decimal("100.00"), quantity=Decimal("1"))],
    )
    repo.save_invoice(inv)

    on_open_mock = MagicMock()
    hist_view = HistoryViewComponent(repo, pdf_gen, cfg_service, on_open_mock)
    
    assert len(hist_view.list_container.controls) == 1
    
    # Search filter
    hist_view.txt_search.value = "Tech"
    hist_view.refresh_list()
    assert len(hist_view.list_container.controls) == 1

    hist_view.txt_search.value = "NonExistent"
    hist_view.refresh_list()
    assert len(hist_view.list_container.controls) == 1  # Empty state container

def test_customer_form_load_and_reset():
    from src.domain.models import Customer
    on_change = MagicMock()
    form = CustomerFormComponent(on_change)

    # Load existing customer
    cust = Customer(
        customer_name="Custom Buyer",
        customer_address="123 Road, City",
        customer_gstin="37TEST12345",
        customer_state="Andhra Pradesh",
    )
    form.load_customer(cust, "SKN/2026-27/099", "2026-08-20")

    assert form.get_invoice_number() == "SKN/2026-27/099"
    assert form.get_invoice_date() == "2026-08-20"
    assert form.get_customer().customer_name == "Custom Buyer"

    # Reset
    form.reset("SKN/2026-27/100")
    assert form.get_invoice_number() == "SKN/2026-27/100"
    assert form.get_customer().customer_name == ""

