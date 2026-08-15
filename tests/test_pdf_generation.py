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

