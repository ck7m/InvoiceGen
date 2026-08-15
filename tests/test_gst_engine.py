import pytest
from decimal import Decimal
from src.domain.models import InvoiceItem, Invoice
from src.domain.gst_engine import (
    calculate_item,
    calculate_invoice,
    quantize_money,
    number_to_words_indian,
)

def test_type_safety():
    """Verify that floats raise TypeError and Decimal is strictly enforced."""
    with pytest.raises(TypeError):
        calculate_item(2.0, Decimal("100.00"), Decimal("9.00"), Decimal("9.00"))  # type: ignore

    with pytest.raises(TypeError):
        calculate_item(Decimal("2.00"), 100.00, Decimal("9.00"), Decimal("9.00"))  # type: ignore

    with pytest.raises(TypeError):
        quantize_money(10.5)  # type: ignore

def test_gst_9_percent_item1_spec():
    """Test Item 1 from spec: Dell Latitude Laptop Qty 2 @ 82627.12 with 9% CGST + 9% SGST."""
    qty = Decimal("2")
    rate = Decimal("82627.12")
    cgst_pct = Decimal("9.00")
    sgst_pct = Decimal("9.00")

    taxable, cgst, sgst, total_tax, rate_with_tax, amount_with_tax = calculate_item(
        qty, rate, cgst_pct, sgst_pct
    )

    assert taxable == Decimal("165254.24")
    assert cgst == Decimal("14872.88")  # 165254.24 * 0.09 = 14872.8816 -> 14872.88
    assert sgst == Decimal("14872.88")
    assert total_tax == Decimal("29745.76")
    assert amount_with_tax == Decimal("195000.00")
    assert rate_with_tax == Decimal("97500.00")

def test_0_percent_gst():
    taxable, cgst, sgst, total_tax, rate_with_tax, amount_with_tax = calculate_item(
        Decimal("5"), Decimal("100.00"), Decimal("0.00"), Decimal("0.00")
    )
    assert taxable == Decimal("500.00")
    assert cgst == Decimal("0.00")
    assert sgst == Decimal("0.00")
    assert total_tax == Decimal("0.00")
    assert amount_with_tax == Decimal("500.00")
    assert rate_with_tax == Decimal("100.00")

def test_5_percent_gst():
    # 2.5% CGST + 2.5% SGST
    taxable, cgst, sgst, total_tax, rate_with_tax, amount_with_tax = calculate_item(
        Decimal("10"), Decimal("50.00"), Decimal("2.50"), Decimal("2.50")
    )
    assert taxable == Decimal("500.00")
    assert cgst == Decimal("12.50")
    assert sgst == Decimal("12.50")
    assert total_tax == Decimal("25.00")
    assert amount_with_tax == Decimal("525.00")

def test_12_percent_gst():
    # 6% CGST + 6% SGST
    taxable, cgst, sgst, total_tax, rate_with_tax, amount_with_tax = calculate_item(
        Decimal("1"), Decimal("1000.00"), Decimal("6.00"), Decimal("6.00")
    )
    assert taxable == Decimal("1000.00")
    assert cgst == Decimal("60.00")
    assert sgst == Decimal("60.00")
    assert total_tax == Decimal("120.00")

def test_18_percent_gst():
    # 9% CGST + 9% SGST
    taxable, cgst, sgst, total_tax, rate_with_tax, amount_with_tax = calculate_item(
        Decimal("1"), Decimal("1000.00"), Decimal("9.00"), Decimal("9.00")
    )
    assert taxable == Decimal("1000.00")
    assert cgst == Decimal("90.00")
    assert sgst == Decimal("90.00")
    assert total_tax == Decimal("180.00")

def test_28_percent_gst():
    # 14% CGST + 14% SGST
    taxable, cgst, sgst, total_tax, rate_with_tax, amount_with_tax = calculate_item(
        Decimal("1"), Decimal("1000.00"), Decimal("14.00"), Decimal("14.00")
    )
    assert taxable == Decimal("1000.00")
    assert cgst == Decimal("140.00")
    assert sgst == Decimal("140.00")
    assert total_tax == Decimal("280.00")

def test_rounding_boundaries():
    # 1.005 -> 1.01 (ROUND_HALF_UP)
    # Rate: 11.15 * 0.09 = 1.0035 -> 1.00
    taxable, cgst, sgst, total_tax, rate_with_tax, amount_with_tax = calculate_item(
        Decimal("1"), Decimal("11.15"), Decimal("9.00"), Decimal("9.00")
    )
    assert taxable == Decimal("11.15")
    assert cgst == Decimal("1.00")
    assert sgst == Decimal("1.00")

    # Rate: 11.28 * 0.09 = 1.0152 -> 1.02
    taxable2, cgst2, sgst2, total_tax2, _, _ = calculate_item(
        Decimal("1"), Decimal("11.28"), Decimal("9.00"), Decimal("9.00")
    )
    assert cgst2 == Decimal("1.02")

def test_large_amounts():
    taxable, cgst, sgst, total_tax, rate_with_tax, amount_with_tax = calculate_item(
        Decimal("100"), Decimal("5000000.00"), Decimal("9.00"), Decimal("9.00")
    )
    assert taxable == Decimal("500000000.00")
    assert cgst == Decimal("45000000.00")
    assert sgst == Decimal("45000000.00")
    assert total_tax == Decimal("90000000.00")
    assert amount_with_tax == Decimal("590000000.00")

def test_invoice_invariants():
    item1 = InvoiceItem(
        description="Laptop",
        quantity=Decimal("2"),
        rate=Decimal("82627.12"),
        cgst_percent=Decimal("9.00"),
        sgst_percent=Decimal("9.00"),
    )
    item2 = InvoiceItem(
        description="Mouse",
        quantity=Decimal("5"),
        rate=Decimal("500.00"),
        cgst_percent=Decimal("9.00"),
        sgst_percent=Decimal("9.00"),
    )
    
    invoice = Invoice(items=[item1, item2])
    calculate_invoice(invoice)

    # Invariants verification
    assert invoice.total_tax == invoice.total_cgst + invoice.total_sgst
    assert invoice.grand_total == invoice.subtotal + invoice.total_tax
    assert isinstance(invoice.grand_total, Decimal)

def test_number_to_words():
    words = number_to_words_indian(Decimal("195000.00"))
    assert "INR One Lakh Ninety Five Thousand Rupees Only" in words
