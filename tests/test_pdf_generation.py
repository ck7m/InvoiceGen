import os
import pytest
from decimal import Decimal
from src.domain.models import Invoice, InvoiceItem, Customer, CompanySettings
from src.pdf.generator import PDFGenerator

@pytest.fixture
def pdf_gen():
    return PDFGenerator()

def test_generate_pdf_prototype_test_data(pdf_gen, tmp_path):
    """
    Test prototype test suite:
    Item 1: Dell Latitude Laptop (Qty 2, Rate 82627.12, CGST 9%, SGST 9%)
    Item 2: Deliberately long multi-line description
    Item 3: Very short description
    """
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

    customer = Customer(
        customer_name="Grand Cyber Tech Systems India Ltd",
        customer_address="Plot 45, IT Park, Mangalagiri, Guntur District, AP - 522503",
        customer_gstin="37AAACG1234F1Z9",
        customer_pan="AAACG1234F",
        customer_state="Andhra Pradesh",
        customer_state_code="37",
    )

    invoice = Invoice(
        invoice_number="SKN/2026-27/001",
        invoice_date="2026-08-15",
        customer=customer,
        items=[item1, item2, item3],
    )

    output_pdf = str(tmp_path / "prototype_invoice.pdf")
    generated_path = pdf_gen.generate_pdf(invoice, output_pdf)

    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 1000

def test_generate_pdf_multi_page(pdf_gen, tmp_path):
    """Test multi-page invoice layout with 25 items."""
    items = []
    for i in range(1, 26):
        items.append(
            InvoiceItem(
                description=f"Item #{i}: High performance network cable component model SKN-CAT6A-{i:03d} with extra long description for testing multi-page flow and table header repetition.",
                batch_number=f"BATCH-{i:02d}",
                hsn_sac="85444299",
                quantity=Decimal(f"{i}.00"),
                rate=Decimal(f"{1000 * i}.00"),
                cgst_percent=Decimal("9.00"),
                sgst_percent=Decimal("9.00"),
            )
        )

    customer = Customer(
        customer_name="Bulk Enterprise Client",
        customer_address="Industrial Area, Vijayawada, AP",
        customer_gstin="37AAABB0000A1Z1",
        customer_state="Andhra Pradesh",
    )

    invoice = Invoice(
        invoice_number="SKN/2026-27/MULTI-01",
        invoice_date="2026-08-15",
        customer=customer,
        items=items,
    )

    output_pdf = str(tmp_path / "multipage_invoice.pdf")
    generated_path = pdf_gen.generate_pdf(invoice, output_pdf)

    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 2000

def test_generate_pdf_single_item(pdf_gen, tmp_path):
    """Test clean layout and footer positioning with a single item."""
    item = InvoiceItem(
        description="Single Cisco Core Switch 9300 48-Port PoE+",
        batch_number="CIS-9300",
        hsn_sac="85176290",
        quantity=Decimal("1.00"),
        rate=Decimal("250000.00"),
        cgst_percent=Decimal("9.00"),
        sgst_percent=Decimal("9.00"),
    )
    customer = Customer(
        customer_name="Hospitality Net Corp",
        customer_address="Resort Road, Guntur, AP",
        customer_gstin="37AAACH9999Z1Z5",
    )
    invoice = Invoice(
        invoice_number="SKN/2026-27/005",
        invoice_date="2026-08-16",
        customer=customer,
        items=[item],
    )
    output_pdf = str(tmp_path / "single_item.pdf")
    generated_path = pdf_gen.generate_pdf(invoice, output_pdf)
    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 1000

def test_generate_pdf_10_items_with_long_descriptions(pdf_gen, tmp_path):
    """Test 10 items layout where each item has multi-line specifications."""
    items = []
    for i in range(1, 11):
        items.append(
            InvoiceItem(
                description=(
                    f"Service #{i}: Enterprise Wi-Fi 6 Access Point Deployment\n"
                    f"- High density ceiling AP model AP-W6-{i:02d}\n"
                    f"- Channel bonding, RF power calibration, and controller licensing for 5 years."
                ),
                batch_number=f"WIFI-{i:02d}",
                hsn_sac="85176290",
                quantity=Decimal("2.00"),
                rate=Decimal("35000.00"),
                cgst_percent=Decimal("9.00"),
                sgst_percent=Decimal("9.00"),
            )
        )
    invoice = Invoice(
        invoice_number="SKN/2026-27/010",
        invoice_date="2026-08-16",
        customer=Customer(customer_name="Tech Park Campus", customer_address="Plot 10, Guntur"),
        items=items,
    )
    output_pdf = str(tmp_path / "ten_items_long.pdf")
    generated_path = pdf_gen.generate_pdf(invoice, output_pdf)
    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 1500

def test_pdf_rendered_html_uses_rs_symbol():
    from src.rendering.document import InvoiceDocumentRenderer
    from src.domain.models import Invoice, Customer, InvoiceItem
    renderer = InvoiceDocumentRenderer()
    invoice = Invoice(
        invoice_number="SKN/2026-27/TEST-RS",
        customer=Customer(customer_name="Test Customer"),
        items=[InvoiceItem(description="Item 1", rate=Decimal("500.00"), quantity=Decimal("1"))],
    )
    from src.domain.gst_engine import calculate_invoice
    calculate_invoice(invoice)
    html = renderer.render_html(invoice)
    assert "₹" not in html, "Rupee symbol '₹' must not be in exported PDF HTML"
    assert "Rate (Rs)" in html
    assert "Amount (Rs)" in html
    assert "(Rs)" in html
    # Total rows must not have "Rs " prefix
    assert "Rs " not in html, "'Rs' prefix must be removed from the totals row"

def test_pdf_layout_customizations():
    from src.rendering.document import InvoiceDocumentRenderer
    from src.domain.models import Invoice, Customer, InvoiceItem
    renderer = InvoiceDocumentRenderer()
    invoice = Invoice(
        invoice_number="SKN/2026-27/TEST-LAYOUT",
        po_number="PO-9988",
        po_date="2026-08-10",
        invoice_type="Original",
        terms_of_payment="30 days Credit",
        customer=Customer(customer_name="Alpha Corp", customer_state="Tamilnadu"),
        items=[InvoiceItem(description="Item 1", batch_number="SN-1001", rate=Decimal("1000.00"), quantity=Decimal("1"))],
    )
    html = renderer.render_html(invoice)

    # 1. Declaration must be removed
    assert "Declaration:" not in html, "Declaration must be removed from exported PDF"

    # 2. Customer Seal & Signature must be present
    assert "Customer Seal &amp; Signature:" in html or "Customer Seal & Signature:" in html

    # 3. Place of Supply must be removed from TAX INVOICE section
    assert "Place of Supply:" not in html

    # 4. PO Number, PO Date, Invoice Type, Terms of Payment must be present
    assert "PO-9988" in html
    assert "2026-08-10" in html
    assert "Invoice Type:" in html
    assert "Original" in html
    assert "Terms of Payment:" in html
    assert "30 days Credit" in html

    # 5. Authorised Signatory must be present; "For Sai Krishna Networks" removed from seal/sign section
    assert "Authorised Signatory" in html
    assert "For Sai Krishna Networks" not in html

    # 6. Computer Generated Invoice must be removed
    assert "Computer Generated Invoice" not in html

    # 7. Terms & Conditions must be present above customer seal and signature in dedicated row
    assert "Terms &amp; Conditions:" in html or "Terms & Conditions:" in html
    assert "Goods once sold cannot taken back/Exchange" in html
    assert "Subject to Tamil Nadu Jurisdiction" in html

    # 8. Bank details moved to Amount in words row
    assert "Bank Details for NEFT / RTGS:" in html
    assert "Bank Name:" in html
    assert "Amount in Words:" in html

    # 9. Serial No used instead of Batch
    assert "Serial No: SN-1001" in html

    # 10. Web moved to new line in company header
    assert "Web:" in html
    assert "<div style=\"line-height: 1.15;\"><strong>Web:</strong>" in html

    # 11. Closing section wrapping prevents break after totals
    assert 'class="closing-section"' in html

def test_pdf_three_copies_export(tmp_path):
    from copy import deepcopy
    from src.domain.models import Invoice, Customer, InvoiceItem
    from src.pdf.generator import PDFGenerator
    pdf_gen = PDFGenerator()
    base_inv = Invoice(
        invoice_number="SKN/2026-27/COPIES-TEST",
        po_number="PO-123",
        po_date="2026-08-15",
        terms_of_payment="100% Advance",
        customer=Customer(customer_name="Test Enterprise"),
        items=[InvoiceItem(description="Component", rate=Decimal("5000.00"), quantity=Decimal("1"))],
    )
    copies = []
    for c_type in ["Original", "Duplicate", "Transport"]:
        copy_inv = deepcopy(base_inv)
        copy_inv.invoice_type = c_type
        copies.append(copy_inv)

    out_file = str(tmp_path / "three_copies.pdf")
    generated = pdf_gen.generate_pdf(base_inv, out_file, copies=copies)
    assert os.path.exists(generated)
    assert os.path.getsize(generated) > 2000

    html = pdf_gen.renderer.render_html(base_inv, copies=copies)
    assert "Original" in html
    assert "Duplicate" in html
    assert "Transport" in html
    assert html.count('class="invoice-box page-break"') == 2
    assert html.count('class="invoice-box ') == 3

