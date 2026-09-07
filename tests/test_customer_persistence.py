import pytest
from src.db.repository import InvoiceRepository
from src.domain.models import Customer, Invoice, InvoiceItem
from decimal import Decimal

def test_customer_saving_and_searching(tmp_path):
    db_file = str(tmp_path / "test_cust.db")
    repo = InvoiceRepository(db_path=db_file)

    c1 = Customer(
        customer_name="Grand Cyber Tech Systems India Ltd",
        customer_address="Plot 45, IT Park, Mangalagiri",
        customer_gstin="37AAACG1234F1Z9",
        customer_state="Andhra Pradesh",
        customer_state_code="37",
    )
    c2 = Customer(
        customer_name="Grand Solutions Pvt Ltd",
        customer_address="10 Anna Salai, Chennai",
        customer_gstin="33AABC1234E1Z1",
        customer_state="Tamilnadu",
        customer_state_code="33",
    )

    repo.save_customer(c1)
    repo.save_customer(c2)

    # Search by prefix "Grand"
    results = repo.search_customers("Grand")
    assert len(results) == 2
    names = [r.customer_name for r in results]
    assert "Grand Cyber Tech Systems India Ltd" in names
    assert "Grand Solutions Pvt Ltd" in names

    # Search by GSTIN
    results_gst = repo.search_customers("33AABC")
    assert len(results_gst) == 1
    assert results_gst[0].customer_name == "Grand Solutions Pvt Ltd"
    assert results_gst[0].customer_state == "Tamilnadu"
    assert results_gst[0].customer_state_code == "33"

def test_save_invoice_auto_persists_customer(tmp_path):
    db_file = str(tmp_path / "test_auto_cust.db")
    repo = InvoiceRepository(db_path=db_file)

    cust = Customer(
        customer_name="Auto Saved Enterprise",
        customer_address="Road 1, Coimbatore",
        customer_gstin="33XYZ9999P1Z2",
        customer_state="Tamilnadu",
        customer_state_code="33",
    )
    inv = Invoice(
        invoice_number="SKN/2026-27/CUST-1",
        invoice_date="2026-08-20",
        customer=cust,
        items=[InvoiceItem(description="Item A", rate=Decimal("100.00"), quantity=Decimal("1"))],
    )
    repo.save_invoice(inv)

    # Verify customer was saved in customers table
    found = repo.search_customers("Auto Saved")
    assert len(found) == 1
    assert found[0].customer_name == "Auto Saved Enterprise"
    assert found[0].customer_gstin == "33XYZ9999P1Z2"
    assert found[0].customer_state == "Tamilnadu"
