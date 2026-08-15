import os
import pytest
from decimal import Decimal
from src.domain.models import Invoice, InvoiceItem, Customer, CompanySettings
from src.db.repository import InvoiceRepository

@pytest.fixture
def test_repo(tmp_path):
    db_file = tmp_path / "test_skn.db"
    return InvoiceRepository(db_path=str(db_file))

def test_save_and_retrieve_invoice(test_repo):
    customer = Customer(
        customer_name="Tech Solutions Pvt Ltd",
        customer_address="123 Tech Park, Vijayawada, AP",
        customer_gstin="37BBBCC1111D1Z2",
        customer_pan="BBBCC1111D",
        customer_state="Andhra Pradesh",
        customer_state_code="37",
    )
    item = InvoiceItem(
        description="Dell Latitude Laptop 5420",
        batch_number="B001",
        hsn_sac="84713010",
        quantity=Decimal("2.00"),
        rate=Decimal("82627.12"),
        cgst_percent=Decimal("9.00"),
        sgst_percent=Decimal("9.00"),
    )
    invoice = Invoice(
        invoice_number="SKN/2026-27/001",
        invoice_date="2026-08-15",
        customer=customer,
        items=[item],
    )

    test_repo.save_invoice(invoice)

    retrieved = test_repo.get_invoice_by_number("SKN/2026-27/001")
    assert retrieved is not None
    assert retrieved.invoice_number == "SKN/2026-27/001"
    assert retrieved.customer.customer_name == "Tech Solutions Pvt Ltd"
    assert len(retrieved.items) == 1
    assert retrieved.items[0].taxable_amount == Decimal("165254.24")
    assert retrieved.grand_total == Decimal("195000.00")
    assert isinstance(retrieved.grand_total, Decimal)
