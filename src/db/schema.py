CREATE_COMPANY_TABLE = """
CREATE TABLE IF NOT EXISTS company_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    address TEXT NOT NULL,
    gstin TEXT NOT NULL,
    pan TEXT NOT NULL,
    state TEXT NOT NULL,
    state_code TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    website TEXT,
    bank_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    branch TEXT NOT NULL,
    ifsc TEXT NOT NULL,
    declaration TEXT NOT NULL,
    authorised_signatory TEXT NOT NULL
);
"""

CREATE_INVOICES_TABLE = """
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    invoice_date TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_address TEXT NOT NULL,
    customer_gstin TEXT,
    customer_pan TEXT,
    customer_state TEXT,
    customer_state_code TEXT,
    subtotal TEXT NOT NULL,
    total_cgst TEXT NOT NULL,
    total_sgst TEXT NOT NULL,
    total_tax TEXT NOT NULL,
    grand_total TEXT NOT NULL,
    amount_in_words TEXT NOT NULL,
    tax_amount_in_words TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_INVOICE_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    serial_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    batch_number TEXT,
    hsn_sac TEXT,
    quantity TEXT NOT NULL,
    rate TEXT NOT NULL,
    cgst_percent TEXT NOT NULL,
    sgst_percent TEXT NOT NULL,
    taxable_amount TEXT NOT NULL,
    cgst_amount TEXT NOT NULL,
    sgst_amount TEXT NOT NULL,
    total_tax TEXT NOT NULL,
    rate_with_tax TEXT NOT NULL,
    amount_with_tax TEXT NOT NULL,
    FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);
"""
