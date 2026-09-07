import os
import sqlite3
from decimal import Decimal
from typing import List, Optional
from src.domain.models import CompanySettings, Customer, InvoiceItem, Invoice
from src.domain.gst_engine import calculate_invoice
from src.db.schema import (
    CREATE_COMPANY_TABLE,
    CREATE_INVOICES_TABLE,
    CREATE_INVOICE_ITEMS_TABLE,
    CREATE_CUSTOMERS_TABLE,
)

class InvoiceRepository:
    def __init__(self, db_path: str = None):
        if db_path is None:
            from src.services.config import ConfigService
            db_path = ConfigService().get_db_path()
        self.db_path = db_path
        
        # Ensure directory for DB exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_COMPANY_TABLE)
            cursor.execute(CREATE_INVOICES_TABLE)
            cursor.execute(CREATE_INVOICE_ITEMS_TABLE)
            cursor.execute(CREATE_CUSTOMERS_TABLE)
            
            # Check if website column exists in company_settings (for existing DB migrations)
            cursor.execute("PRAGMA table_info(company_settings);")
            columns = [row["name"] for row in cursor.fetchall()]
            if "website" not in columns and len(columns) > 0:
                try:
                    cursor.execute("ALTER TABLE company_settings ADD COLUMN website TEXT;")
                except Exception:
                    pass

            # Check if new invoice columns exist (for existing DB migrations)
            cursor.execute("PRAGMA table_info(invoices);")
            inv_cols = [row["name"] for row in cursor.fetchall()]
            if "po_number" not in inv_cols and len(inv_cols) > 0:
                try:
                    cursor.execute("ALTER TABLE invoices ADD COLUMN po_number TEXT DEFAULT '';")
                    cursor.execute("ALTER TABLE invoices ADD COLUMN po_date TEXT DEFAULT '';")
                    cursor.execute("ALTER TABLE invoices ADD COLUMN invoice_type TEXT DEFAULT 'Original';")
                    cursor.execute("ALTER TABLE invoices ADD COLUMN terms_of_payment TEXT DEFAULT '100% Advance';")
                except Exception:
                    pass
                    
            conn.commit()

    def get_company_settings(self) -> CompanySettings:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM company_settings ORDER BY id LIMIT 1;")
            row = cursor.fetchone()
            if row:
                row_keys = row.keys()
                return CompanySettings(
                    company_name=row["company_name"],
                    address=row["address"],
                    gstin=row["gstin"],
                    pan=row["pan"],
                    state=row["state"],
                    state_code=row["state_code"],
                    phone=row["phone"],
                    email=row["email"],
                    website=row["website"] if "website" in row_keys and row["website"] else "www.saikrishnanetworks.com",
                    bank_name=row["bank_name"],
                    account_number=row["account_number"],
                    branch=row["branch"],
                    ifsc=row["ifsc"],
                    declaration=row["declaration"],
                    authorised_signatory=row["authorised_signatory"],
                )
            else:
                default_settings = CompanySettings()
                self.save_company_settings(default_settings)
                return default_settings

    def save_company_settings(self, settings: CompanySettings):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM company_settings;")
            cursor.execute(
                """
                INSERT INTO company_settings (
                    company_name, address, gstin, pan, state, state_code,
                    phone, email, website, bank_name, account_number, branch, ifsc,
                    declaration, authorised_signatory
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    settings.company_name,
                    settings.address,
                    settings.gstin,
                    settings.pan,
                    settings.state,
                    settings.state_code,
                    settings.phone,
                    settings.email,
                    settings.website,
                    settings.bank_name,
                    settings.account_number,
                    settings.branch,
                    settings.ifsc,
                    settings.declaration,
                    settings.authorised_signatory,
                ),
            )
            conn.commit()

    def save_invoice(self, invoice: Invoice) -> int:
        calculate_invoice(invoice)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?;", (invoice.invoice_number,))
            existing = cursor.fetchone()

            if existing:
                invoice_id = existing["id"]
                cursor.execute(
                    """
                    UPDATE invoices SET
                        invoice_date = ?, po_number = ?, po_date = ?, invoice_type = ?, terms_of_payment = ?,
                        customer_name = ?, customer_address = ?,
                        customer_gstin = ?, customer_pan = ?, customer_state = ?,
                        customer_state_code = ?, subtotal = ?, total_cgst = ?,
                        total_sgst = ?, total_tax = ?, grand_total = ?,
                        amount_in_words = ?, tax_amount_in_words = ?
                    WHERE id = ?;
                    """,
                    (
                        invoice.invoice_date,
                        invoice.po_number or "",
                        invoice.po_date or "",
                        invoice.invoice_type or "Original",
                        invoice.terms_of_payment or "100% Advance",
                        invoice.customer.customer_name,
                        invoice.customer.customer_address,
                        invoice.customer.customer_gstin,
                        invoice.customer.customer_pan,
                        invoice.customer.customer_state,
                        invoice.customer.customer_state_code,
                        str(invoice.subtotal),
                        str(invoice.total_cgst),
                        str(invoice.total_sgst),
                        str(invoice.total_tax),
                        str(invoice.grand_total),
                        invoice.amount_in_words,
                        invoice.tax_amount_in_words,
                        invoice_id,
                    ),
                )
                cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?;", (invoice_id,))
            else:
                cursor.execute(
                    """
                    INSERT INTO invoices (
                        invoice_number, invoice_date, po_number, po_date, invoice_type, terms_of_payment,
                        customer_name, customer_address,
                        customer_gstin, customer_pan, customer_state, customer_state_code,
                        subtotal, total_cgst, total_sgst, total_tax, grand_total,
                        amount_in_words, tax_amount_in_words
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        invoice.invoice_number,
                        invoice.invoice_date,
                        invoice.po_number or "",
                        invoice.po_date or "",
                        invoice.invoice_type or "Original",
                        invoice.terms_of_payment or "100% Advance",
                        invoice.customer.customer_name,
                        invoice.customer.customer_address,
                        invoice.customer.customer_gstin,
                        invoice.customer.customer_pan,
                        invoice.customer.customer_state,
                        invoice.customer.customer_state_code,
                        str(invoice.subtotal),
                        str(invoice.total_cgst),
                        str(invoice.total_sgst),
                        str(invoice.total_tax),
                        str(invoice.grand_total),
                        invoice.amount_in_words,
                        invoice.tax_amount_in_words,
                    ),
                )
                invoice_id = cursor.lastrowid

            for item in invoice.items:
                cursor.execute(
                    """
                    INSERT INTO invoice_items (
                        invoice_id, serial_number, description, batch_number, hsn_sac,
                        quantity, rate, cgst_percent, sgst_percent, taxable_amount,
                        cgst_amount, sgst_amount, total_tax, rate_with_tax, amount_with_tax
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        invoice_id,
                        item.serial_number,
                        item.description,
                        item.batch_number,
                        item.hsn_sac,
                        str(item.quantity),
                        str(item.rate),
                        str(item.cgst_percent),
                        str(item.sgst_percent),
                        str(item.taxable_amount),
                        str(item.cgst_amount),
                        str(item.sgst_amount),
                        str(item.total_tax),
                        str(item.rate_with_tax),
                        str(item.amount_with_tax),
                    ),
                )
            conn.commit()

        # Save customer details to customers table
        if invoice.customer and (invoice.customer.customer_name or invoice.customer.customer_gstin):
            try:
                self.save_customer(invoice.customer)
            except Exception:
                pass

        return invoice_id

    def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?;", (invoice_number,))
            row = cursor.fetchone()
            if not row:
                return None

            row_keys = row.keys()
            po_number = row["po_number"] if "po_number" in row_keys and row["po_number"] else ""
            po_date = row["po_date"] if "po_date" in row_keys and row["po_date"] else ""
            invoice_type = row["invoice_type"] if "invoice_type" in row_keys and row["invoice_type"] else "Original"
            terms_of_payment = row["terms_of_payment"] if "terms_of_payment" in row_keys and row["terms_of_payment"] else "100% Advance"

            company = self.get_company_settings()
            customer = Customer(
                customer_name=row["customer_name"],
                customer_address=row["customer_address"],
                customer_gstin=row["customer_gstin"] or "",
                customer_pan=row["customer_pan"] or "",
                customer_state=row["customer_state"] or "",
                customer_state_code=row["customer_state_code"] or "",
            )

            cursor.execute(
                "SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY serial_number;",
                (row["id"],),
            )
            item_rows = cursor.fetchall()
            items = []
            for ir in item_rows:
                items.append(
                    InvoiceItem(
                        serial_number=ir["serial_number"],
                        description=ir["description"],
                        batch_number=ir["batch_number"] or "",
                        hsn_sac=ir["hsn_sac"] or "",
                        quantity=Decimal(ir["quantity"]),
                        rate=Decimal(ir["rate"]),
                        cgst_percent=Decimal(ir["cgst_percent"]),
                        sgst_percent=Decimal(ir["sgst_percent"]),
                        taxable_amount=Decimal(ir["taxable_amount"]),
                        cgst_amount=Decimal(ir["cgst_amount"]),
                        sgst_amount=Decimal(ir["sgst_amount"]),
                        total_tax=Decimal(ir["total_tax"]),
                        rate_with_tax=Decimal(ir["rate_with_tax"]),
                        amount_with_tax=Decimal(ir["amount_with_tax"]),
                    )
                )

            invoice = Invoice(
                invoice_number=row["invoice_number"],
                invoice_date=row["invoice_date"],
                po_number=po_number,
                po_date=po_date,
                invoice_type=invoice_type,
                terms_of_payment=terms_of_payment,
                company=company,
                customer=customer,
                items=items,
                subtotal=Decimal(row["subtotal"]),
                total_cgst=Decimal(row["total_cgst"]),
                total_sgst=Decimal(row["total_sgst"]),
                total_tax=Decimal(row["total_tax"]),
                grand_total=Decimal(row["grand_total"]),
                amount_in_words=row["amount_in_words"],
                tax_amount_in_words=row["tax_amount_in_words"],
            )
            return invoice

    def list_invoices(self, search_query: str = "") -> List[dict]:
        """
        Returns summary dictionary for all stored invoices, matching optional search query
        (filters by invoice_number, customer_name, or invoice_date).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if search_query and search_query.strip():
                pattern = f"%{search_query.strip()}%"
                cursor.execute(
                    """
                    SELECT id, invoice_number, invoice_date, customer_name,
                           customer_gstin, subtotal, total_tax, grand_total, created_at
                    FROM invoices
                    WHERE invoice_number LIKE ? OR customer_name LIKE ? OR invoice_date LIKE ?
                    ORDER BY id DESC;
                    """,
                    (pattern, pattern, pattern),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, invoice_number, invoice_date, customer_name,
                           customer_gstin, subtotal, total_tax, grand_total, created_at
                    FROM invoices
                    ORDER BY id DESC;
                    """
                )
            rows = cursor.fetchall()
            result = []
            for r in rows:
                # Count items for each invoice
                cursor.execute("SELECT COUNT(*) as item_count FROM invoice_items WHERE invoice_id = ?;", (r["id"],))
                cnt_row = cursor.fetchone()
                item_count = cnt_row["item_count"] if cnt_row else 0

                result.append({
                    "id": r["id"],
                    "invoice_number": r["invoice_number"],
                    "invoice_date": r["invoice_date"],
                    "customer_name": r["customer_name"],
                    "customer_gstin": r["customer_gstin"] or "",
                    "subtotal": r["subtotal"],
                    "total_tax": r["total_tax"],
                    "grand_total": r["grand_total"],
                    "item_count": item_count,
                    "created_at": r["created_at"],
                })
            return result

    def get_all_invoice_numbers(self) -> List[str]:
        """
        Returns all registered invoice numbers from the database.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT invoice_number FROM invoices ORDER BY id ASC;")
            return [row["invoice_number"] for row in cursor.fetchall()]

    def delete_invoice(self, invoice_number: str) -> bool:
        """
        Deletes the invoice and associated items with the specified invoice number.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?;", (invoice_number,))
            row = cursor.fetchone()
            if not row:
                return False
            invoice_id = row["id"]
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?;", (invoice_id,))
            cursor.execute("DELETE FROM invoices WHERE id = ?;", (invoice_id,))
            conn.commit()
            return True

    def save_customer(self, customer: Customer) -> int:
        """
        Saves or updates customer info in the customers table.
        """
        if not customer.customer_name and not customer.customer_gstin:
            return 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            existing = None
            if customer.customer_gstin and customer.customer_gstin.strip():
                cursor.execute(
                    "SELECT id FROM customers WHERE customer_gstin = ? LIMIT 1;",
                    (customer.customer_gstin.strip(),),
                )
                existing = cursor.fetchone()
            if not existing and customer.customer_name and customer.customer_name.strip():
                cursor.execute(
                    "SELECT id FROM customers WHERE LOWER(customer_name) = LOWER(?) LIMIT 1;",
                    (customer.customer_name.strip(),),
                )
                existing = cursor.fetchone()

            if existing:
                cust_id = existing["id"]
                cursor.execute(
                    """
                    UPDATE customers
                    SET customer_name = ?, customer_address = ?, customer_gstin = ?,
                        customer_pan = ?, customer_state = ?, customer_state_code = ?,
                        phone = ?, email = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?;
                    """,
                    (
                        customer.customer_name.strip(),
                        customer.customer_address.strip(),
                        customer.customer_gstin.strip() if customer.customer_gstin else "",
                        customer.customer_pan.strip() if customer.customer_pan else "",
                        customer.customer_state.strip() if customer.customer_state else "",
                        customer.customer_state_code.strip() if customer.customer_state_code else "",
                        customer.phone.strip() if customer.phone else "",
                        customer.email.strip() if customer.email else "",
                        cust_id,
                    ),
                )
                conn.commit()
                return cust_id
            else:
                cursor.execute(
                    """
                    INSERT INTO customers (
                        customer_name, customer_address, customer_gstin,
                        customer_pan, customer_state, customer_state_code,
                        phone, email
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        customer.customer_name.strip(),
                        customer.customer_address.strip(),
                        customer.customer_gstin.strip() if customer.customer_gstin else "",
                        customer.customer_pan.strip() if customer.customer_pan else "",
                        customer.customer_state.strip() if customer.customer_state else "",
                        customer.customer_state_code.strip() if customer.customer_state_code else "",
                        customer.phone.strip() if customer.phone else "",
                        customer.email.strip() if customer.email else "",
                    ),
                )
                conn.commit()
                return cursor.lastrowid

    def search_customers(self, query: str) -> List[Customer]:
        """
        Search saved customers by name or GSTIN (matches substring).
        """
        q = query.strip()
        if not q or len(q) < 1:
            return []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            pattern = f"%{q}%"
            cursor.execute(
                """
                SELECT * FROM customers
                WHERE customer_name LIKE ? OR customer_gstin LIKE ?
                ORDER BY updated_at DESC LIMIT 10;
                """,
                (pattern, pattern),
            )
            rows = cursor.fetchall()

            # If no results in customers table, fallback to distinct customers in invoices table
            if not rows:
                cursor.execute(
                    """
                    SELECT DISTINCT customer_name, customer_address, customer_gstin,
                           customer_pan, customer_state, customer_state_code, '' as phone, '' as email
                    FROM invoices
                    WHERE customer_name LIKE ? OR customer_gstin LIKE ?
                    ORDER BY id DESC LIMIT 10;
                    """,
                    (pattern, pattern),
                )
                rows = cursor.fetchall()

            customers = []
            seen = set()
            for r in rows:
                key = (r["customer_name"] or "", r["customer_gstin"] or "")
                if key in seen:
                    continue
                seen.add(key)
                customers.append(
                    Customer(
                        customer_name=r["customer_name"] or "",
                        customer_address=r["customer_address"] or "",
                        customer_gstin=r["customer_gstin"] or "",
                        customer_pan=r["customer_pan"] if "customer_pan" in r.keys() and r["customer_pan"] else "",
                        customer_state=r["customer_state"] if "customer_state" in r.keys() and r["customer_state"] else "",
                        customer_state_code=r["customer_state_code"] if "customer_state_code" in r.keys() and r["customer_state_code"] else "",
                        phone=r["phone"] if "phone" in r.keys() and r["phone"] else "",
                        email=r["email"] if "email" in r.keys() and r["email"] else "",
                    )
                )
            return customers

    def get_all_customers(self) -> List[Customer]:
        """
        Returns all saved customers ordered by name.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers ORDER BY customer_name ASC;")
            rows = cursor.fetchall()
            return [
                Customer(
                    customer_name=r["customer_name"] or "",
                    customer_address=r["customer_address"] or "",
                    customer_gstin=r["customer_gstin"] or "",
                    customer_pan=r["customer_pan"] or "",
                    customer_state=r["customer_state"] or "",
                    customer_state_code=r["customer_state_code"] or "",
                    phone=r["phone"] or "",
                    email=r["email"] or "",
                )
                for r in rows
            ]

