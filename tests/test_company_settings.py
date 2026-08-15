import os
from decimal import Decimal
import pytest
from unittest.mock import MagicMock
from src.domain.models import CompanySettings, Invoice, InvoiceItem, Customer
from src.db.repository import InvoiceRepository
from src.services.config import ConfigService, AppConfig
from src.rendering.document import InvoiceDocumentRenderer
from src.ui.components.settings_view import SettingsViewComponent

def test_default_company_settings(tmp_path):
    db_file = str(tmp_path / "settings_default_test.db")
    repo = InvoiceRepository(db_path=db_file)

    settings = repo.get_company_settings()
    assert settings.company_name == "Sai Krishna Networks"
    assert settings.gstin == "37AAAAA0000A1Z5"
    assert settings.pan == "AAAAA0000A"
    assert settings.state == "Andhra Pradesh"
    assert settings.state_code == "37"
    assert settings.phone == "+91 98765 43210"
    assert settings.email == "info@saikrishnanetworks.com"
    assert settings.website == "www.saikrishnanetworks.com"
    assert settings.bank_name == "State Bank of India"
    assert settings.account_number == "123456789012"
    assert settings.branch == "Main Branch, Guntur"
    assert settings.ifsc == "SBIN0001234"
    assert "actual price" in settings.declaration
    assert settings.authorised_signatory == "For Sai Krishna Networks"

def test_company_settings_persistence(tmp_path):
    db_file = str(tmp_path / "settings_test.db")
    repo = InvoiceRepository(db_path=db_file)

    # Modify settings
    custom_settings = CompanySettings(
        company_name="Sai Krishna Networks Enterprises Pvt Ltd",
        address="Plot 45, Tech Zone, Guntur, AP - 522001",
        gstin="37AAACS1234F1Z9",
        pan="AAACS1234F",
        state="Andhra Pradesh",
        state_code="37",
        phone="+91 99999 88888",
        email="billing@sknenterprises.com",
        website="https://sknenterprises.com",
        bank_name="HDFC Bank",
        account_number="98765432109876",
        branch="Ring Road Branch, Guntur",
        ifsc="HDFC0001234",
        declaration="Custom certified declaration of genuine supply under GST rules.",
        authorised_signatory="Managing Director / Authorised Signatory",
    )

    repo.save_company_settings(custom_settings)

    # Reload from SQLite DB
    loaded = repo.get_company_settings()
    assert loaded.company_name == "Sai Krishna Networks Enterprises Pvt Ltd"
    assert loaded.address == "Plot 45, Tech Zone, Guntur, AP - 522001"
    assert loaded.gstin == "37AAACS1234F1Z9"
    assert loaded.pan == "AAACS1234F"
    assert loaded.phone == "+91 99999 88888"
    assert loaded.email == "billing@sknenterprises.com"
    assert loaded.website == "https://sknenterprises.com"
    assert loaded.bank_name == "HDFC Bank"
    assert loaded.account_number == "98765432109876"
    assert loaded.branch == "Ring Road Branch, Guntur"
    assert loaded.ifsc == "HDFC0001234"
    assert loaded.declaration == "Custom certified declaration of genuine supply under GST rules."
    assert loaded.authorised_signatory == "Managing Director / Authorised Signatory"

def test_company_settings_rendered_in_html_invoice(tmp_path):
    db_file = str(tmp_path / "settings_render_test.db")
    repo = InvoiceRepository(db_path=db_file)

    custom_settings = CompanySettings(
        company_name="SKN Cloud Solutions",
        address="Suite 101, IT Park, Vijayawada",
        gstin="37BBBBB1111B1Z2",
        pan="BBBBB1111B",
        state="Andhra Pradesh",
        state_code="37",
        phone="+91 88888 77777",
        email="accounts@skncloud.io",
        website="www.skncloud.io",
        bank_name="ICICI Bank",
        account_number="555566667777",
        branch="MG Road Branch",
        ifsc="ICIC0000555",
        declaration="All accounts subject to Guntur jurisdiction.",
        authorised_signatory="Authorised Representative - SKN",
    )
    repo.save_company_settings(custom_settings)

    # Create Invoice using the loaded company settings
    company = repo.get_company_settings()
    invoice = Invoice(
        invoice_number="SKN/2026-27/101",
        invoice_date="16/08/2026",
        company=company,
        customer=Customer(customer_name="Alpha Corp", customer_address="Plot 5, Hyderabad"),
        items=[
            InvoiceItem(
                serial_number=1,
                description="Network Switch",
                hsn_sac="85176290",
                quantity=Decimal("1"),
                rate=Decimal("5000.00"),
                cgst_percent=Decimal("9.00"),
                sgst_percent=Decimal("9.00"),
            )
        ],
    )

    renderer = InvoiceDocumentRenderer()
    html = renderer.render_html(invoice)

    # Verify company profile rendered dynamically
    assert "SKN Cloud Solutions" in html
    assert "Suite 101, IT Park, Vijayawada" in html
    assert "37BBBBB1111B1Z2" in html
    assert "BBBBB1111B" in html
    assert "+91 88888 77777" in html
    assert "accounts@skncloud.io" in html
    assert "www.skncloud.io" in html

    # Verify bank details rendered dynamically
    assert "ICICI Bank" in html
    assert "555566667777" in html
    assert "MG Road Branch" in html
    assert "ICIC0000555" in html

    # Verify declaration & signatory rendered dynamically
    assert "All accounts subject to Guntur jurisdiction." in html
    assert "Authorised Representative - SKN" in html

def test_settings_view_validation(tmp_path):
    config_file = str(tmp_path / "test_cfg.json")
    cfg_service = ConfigService(config_file=config_file)
    company = CompanySettings()
    on_save = MagicMock()

    view = SettingsViewComponent(company, cfg_service, on_save)

    # Empty company name should fail validation
    view.txt_name.value = ""
    view._save_settings()
    assert not on_save.called
    assert "Company Name" in view.txt_status.value

    # Empty address should fail validation
    view.txt_name.value = "Valid Name"
    view.txt_address.value = ""
    view._save_settings()
    assert not on_save.called
    assert "Company Address" in view.txt_status.value

    # Empty GSTIN should fail validation
    view.txt_address.value = "Valid Address"
    view.txt_gstin.value = ""
    view._save_settings()
    assert not on_save.called
    assert "GSTIN" in view.txt_status.value

    # Valid values should succeed
    view.txt_gstin.value = "37ABCDE1234F1Z5"
    view._save_settings()
    assert on_save.called
    assert "successfully" in view.txt_status.value

def test_settings_view_reset_defaults(tmp_path):
    config_file = str(tmp_path / "test_cfg.json")
    cfg_service = ConfigService(config_file=config_file)
    company = CompanySettings(company_name="Temporary Name")
    on_save = MagicMock()

    view = SettingsViewComponent(company, cfg_service, on_save)
    view._reset_defaults()

    assert view.txt_name.value == "Sai Krishna Networks"
    assert view.txt_gstin.value == "37AAAAA0000A1Z5"
    assert "defaults" in view.txt_status.value
