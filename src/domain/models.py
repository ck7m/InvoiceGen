from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

@dataclass
class CompanySettings:
    company_name: str = "Sai Krishna Networks"
    address: str = "Door No. 12-3-4, Main Road, Guntur, Andhra Pradesh"
    gstin: str = "37AAAAA0000A1Z5"
    pan: str = "AAAAA0000A"
    state: str = "Andhra Pradesh"
    state_code: str = "37"
    phone: str = "+91 98765 43210"
    email: str = "info@saikrishnanetworks.com"
    website: str = "www.saikrishnanetworks.com"
    bank_name: str = "State Bank of India"

    account_number: str = "123456789012"
    branch: str = "Main Branch, Guntur"
    ifsc: str = "SBIN0001234"
    declaration: str = "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct."
    authorised_signatory: str = "For Sai Krishna Networks"

@dataclass
class Customer:
    customer_name: str = ""
    customer_address: str = ""
    customer_gstin: str = ""
    customer_pan: str = ""
    customer_state: str = ""
    customer_state_code: str = ""
    phone: str = ""
    email: str = ""

@dataclass
class InvoiceItem:
    serial_number: int = 1
    description: str = ""
    batch_number: str = ""
    hsn_sac: str = ""
    quantity: Decimal = field(default_factory=lambda: Decimal("1.00"))
    rate: Decimal = field(default_factory=lambda: Decimal("0.00"))
    cgst_percent: Decimal = field(default_factory=lambda: Decimal("9.00"))
    sgst_percent: Decimal = field(default_factory=lambda: Decimal("9.00"))
    
    # Calculated fields populated by GST calculation engine
    taxable_amount: Decimal = field(default_factory=lambda: Decimal("0.00"))
    cgst_amount: Decimal = field(default_factory=lambda: Decimal("0.00"))
    sgst_amount: Decimal = field(default_factory=lambda: Decimal("0.00"))
    total_tax: Decimal = field(default_factory=lambda: Decimal("0.00"))
    rate_with_tax: Decimal = field(default_factory=lambda: Decimal("0.00"))
    amount_with_tax: Decimal = field(default_factory=lambda: Decimal("0.00"))

@dataclass
class Invoice:
    invoice_number: str = ""
    invoice_date: str = ""
    company: CompanySettings = field(default_factory=CompanySettings)
    customer: Customer = field(default_factory=Customer)
    items: List[InvoiceItem] = field(default_factory=list)
    
    # Summary calculations
    subtotal: Decimal = field(default_factory=lambda: Decimal("0.00"))
    total_cgst: Decimal = field(default_factory=lambda: Decimal("0.00"))
    total_sgst: Decimal = field(default_factory=lambda: Decimal("0.00"))
    total_tax: Decimal = field(default_factory=lambda: Decimal("0.00"))
    grand_total: Decimal = field(default_factory=lambda: Decimal("0.00"))
    amount_in_words: str = ""
    tax_amount_in_words: str = ""
