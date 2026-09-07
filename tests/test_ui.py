import pytest
from decimal import Decimal
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

def test_item_table_prototype_button_hidden_in_frozen_build(monkeypatch):
    import sys
    on_change_mock = MagicMock()

    # In local testing (not frozen)
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.delenv("INVOICEGEN_ENV", raising=False)
    local_table = ItemTableComponent(on_change_mock)
    assert local_table.btn_load_proto.visible is True
    assert local_table.btn_load_proto in local_table.content.controls[2].controls

    # In built exe / macOS app bundle (frozen)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    frozen_table = ItemTableComponent(on_change_mock)
    assert frozen_table.btn_load_proto.visible is False
    assert frozen_table.btn_load_proto not in frozen_table.content.controls[2].controls

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

def test_action_panel_wrapping_and_status():
    from src.ui.components.preview_panel import ActionPanelComponent
    panel = ActionPanelComponent(
        on_save_draft=MagicMock(),
        on_export_pdf=MagicMock(),
        on_export_3_copies=MagicMock(),
    )
    long_msg = "Draft saved to SQLite DB successfully! (ID: 1) at /Users/mohan/Documents/SKN_Invoice_Generator/data/skn_invoices.db"
    panel.set_status(long_msg)
    assert panel.txt_status.value == long_msg
    assert panel.txt_status.expand is True
    assert panel.txt_status.no_wrap is False

def test_customer_form_default_state_and_terms():
    on_change = MagicMock()
    form = CustomerFormComponent(on_change)

    # Verify default state is Tamilnadu
    assert form.txt_cust_state.value == "Tamilnadu"
    assert form.get_customer().customer_state == "Tamilnadu"
    assert form.get_customer().customer_state_code == "33"

    # Verify default terms of payment is 100% Advance
    assert form.get_terms_of_payment() == "100% Advance"
    assert form.get_invoice_type() == "Original"

    # Test reset maintains Tamilnadu
    form.reset("SKN/2026-27/005")
    assert form.txt_cust_state.value == "Tamilnadu"
    assert form.get_customer().customer_state_code == "33"
    assert form.get_terms_of_payment() == "100% Advance"

def test_customer_form_autocomplete_single_and_multiple_matches():
    from src.domain.models import Customer
    on_change = MagicMock()

    c1 = Customer(
        customer_name="Alpha Tech Ltd",
        customer_address="100 Mount Road, Chennai",
        customer_gstin="33AAAAA1111A1Z1",
        customer_state="Tamilnadu",
        customer_state_code="33",
    )
    c2 = Customer(
        customer_name="Alpha Networks Inc",
        customer_address="200 Anna Salai, Chennai",
        customer_gstin="33BBBBB2222B1Z2",
        customer_state="Tamilnadu",
        customer_state_code="33",
    )

    def mock_search(query: str):
        if query == "Alpha":
            return [c1, c2]
        elif query == "Alpha Tech":
            return [c1]
        return []

    form = CustomerFormComponent(on_change, on_search_customer=mock_search)

    # 1. Multiple matches: user selection UI displayed
    event_multiple = MagicMock()
    event_multiple.control.value = "Alpha"
    form._handle_customer_input_change(event_multiple)

    assert form.suggestions_card.visible is True
    assert len(form.suggestions_column.controls) == 2

    # Click the second customer to select
    form.apply_customer(c2)
    assert form.suggestions_card.visible is False
    assert form.txt_cust_name.value == "Alpha Networks Inc"
    assert form.txt_cust_gstin.value == "33BBBBB2222B1Z2"
    assert form.txt_cust_address.value == "200 Anna Salai, Chennai"

    # 2. Single match: displayed in suggestions card for user to load
    event_single = MagicMock()
    event_single.control.value = "Alpha Tech"
    form._handle_customer_input_change(event_single)

    assert form.suggestions_card.visible is True
    assert len(form.suggestions_column.controls) == 1

    # Clicking the match populates details and hides suggestions
    form.apply_customer(c1)
    assert form.suggestions_card.visible is False
    assert form.txt_cust_name.value == "Alpha Tech Ltd"
    assert form.txt_cust_gstin.value == "33AAAAA1111A1Z1"
    assert form.txt_cust_address.value == "100 Mount Road, Chennai"

    # 3. User is free to edit customer fields without autocomplete overwriting them
    form.txt_cust_name.value = "Alpha Tech India Pvt Ltd"
    form.txt_cust_gstin.value = "33AAAAA9999Z1Z9"
    cust = form.get_customer()
    assert cust.customer_name == "Alpha Tech India Pvt Ltd"
    assert cust.customer_gstin == "33AAAAA9999Z1Z9"

def test_item_table_rate_placeholder_zeros_removal():
    from src.ui.components.item_table import ItemTableComponent
    on_change = MagicMock()
    table = ItemTableComponent(on_change)
    row = table.rows[0]

    # Empty/zero rate clears on focus
    row.txt_rate.value = "0.00"
    row._handle_rate_focus(MagicMock())
    assert row.txt_rate.value == ""

    # If placeholder zero exists when user types, leading zero is stripped
    row.txt_rate.value = "0.0050"
    row._handle_rate_change(MagicMock())
    assert row.txt_rate.value == "50"

def test_item_table_qty_placeholder_zeros_removal():
    from src.ui.components.item_table import ItemTableComponent
    on_change = MagicMock()
    table = ItemTableComponent(on_change)
    row = table.rows[0]

    # Focus clears default placeholder "1.00"
    row.txt_qty.value = "1.00"
    row._handle_qty_focus(MagicMock())
    assert row.txt_qty.value == ""

    # If user types while placeholder present, it is cleanly replaced
    row.txt_qty.value = "1.005"
    row._handle_qty_change(MagicMock())
    assert row.txt_qty.value == "5"

    # Blur on empty restores default 1.00
    row.txt_qty.value = ""
    row._handle_qty_blur(MagicMock())
    assert row.txt_qty.value == "1.00"

def test_item_table_reset_clears_all_items_from_existing_invoice():
    from src.ui.components.item_table import ItemTableComponent
    on_change = MagicMock()
    table = ItemTableComponent(on_change)

    # Load 3 existing items
    table.load_prototype_data()
    assert len(table.rows) == 3

    # Reset clears all items and resets to exactly 1 blank row
    table.reset()
    assert len(table.rows) == 1
    assert len(table.rows_column.controls) == 1
    blank_item = table.get_items()[0]
    assert blank_item.description == ""
    assert blank_item.batch_number == ""
    assert blank_item.hsn_sac == ""
    assert blank_item.rate == Decimal("0.00")

def test_item_table_serial_no_header_and_controls():
    from src.ui.components.item_table import ItemTableComponent
    table = ItemTableComponent(MagicMock())
    # Header check
    header_texts = [c.content.value for c in table.content.controls[0].content.controls if hasattr(c.content, "value")]
    assert "Serial No" in header_texts
    assert "Batch" not in header_texts

    # Row control hint text check
    row = table.rows[0]
    assert row.txt_batch.hint_text == "Serial No"

