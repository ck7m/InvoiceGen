# Sai Krishna Networks GST Invoice Generator — Detailed Product & Engineering Specification

## 1. Document purpose

This document is the implementation specification for AI coding agents building the Sai Krishna Networks GST Invoice Generator.

The application is a small, offline-first Windows desktop application with macOS support.

The first implementation task is explicitly a **project setup + invoice prototype**. Subsequent tasks should build the remaining functionality on top of the prototype.

Agents must follow this specification rather than introducing unnecessary architecture or cloud services.

---

# 2. Primary objectives

The application shall:

1. Run as a desktop application.
2. Primarily support Windows.
3. Also support macOS.
4. Work offline.
5. Store data locally in SQLite.
6. Allow creation of GST invoices.
7. Calculate GST accurately.
8. Display taxable rate, tax-inclusive rate, tax amount and total amount.
9. Generate an A4 PDF invoice.
10. Print the invoice.
11. Handle descriptions ranging from very short to several lines without breaking the invoice layout.
12. Follow the structure and visual style of the supplied sample invoice where practical.
13. Remain simple enough for 1–2 users.
14. Avoid unnecessary server/cloud infrastructure.

---

# 3. Technology requirements

## 3.1 Required technology

Use:

- Python 3.12+
- Flet
- SQLite
- Python `Decimal`
- pytest
- HTML/CSS for invoice document layout
- A suitable HTML-to-PDF renderer
- Flet Build for packaging

## 3.2 Do not introduce

Unless a concrete requirement appears later, do NOT introduce:

- Web server
- REST API
- Microservices
- Docker
- Cloud database
- AWS/Azure infrastructure
- PostgreSQL
- Redis
- Kafka
- Authentication server
- Remote backend

This is a local desktop application.

---

# 4. Critical financial accuracy rules

## 4.1 Never use float

The following is prohibited:

```python
rate = 1000.10
tax = rate * 0.09
```

Do not use Python `float` for monetary calculations.

Use:

```python
from decimal import Decimal

rate = Decimal("1000.10")
tax_rate = Decimal("0.09")
```

Never do:

```python
Decimal(0.1)
```

Use:

```python
Decimal("0.1")
```

instead.

## 4.2 Monetary precision

Internally use `Decimal`.

Invoice monetary display precision is 2 decimal places unless a future business rule explicitly requires otherwise.

## 4.3 Explicit rounding

The implementation must define a single rounding policy and use it consistently.

Recommended default:

```text
ROUND_HALF_UP
```

The GST engine must explicitly quantize calculated monetary amounts to 2 decimal places at the defined calculation boundary.

Do not allow different UI/PDF/database layers to independently round the same value.

## 4.4 Calculation ownership

Only the GST/domain calculation layer calculates:

- taxable amount
- CGST amount
- SGST amount
- total tax
- tax-inclusive rate
- tax-inclusive amount
- invoice total

The UI only displays the result.

---

# 5. GST calculation model

For an invoice item:

```text
Quantity
Rate per quantity
CGST %
SGST %
```

Calculate:

```text
Taxable Amount = Quantity × Rate
CGST Amount = Taxable Amount × CGST %
SGST Amount = Taxable Amount × SGST %

Total Tax = CGST Amount + SGST Amount

Amount With Tax = Taxable Amount + Total Tax

Rate With Tax = Rate + (Rate × CGST %) + (Rate × SGST %)
```

All monetary results must follow the application's explicit rounding policy.

## Example

Input:

```text
Quantity = 2
Rate = ₹1,000.00
CGST = 9%
SGST = 9%
```

Expected:

```text
Taxable Amount = ₹2,000.00
CGST = ₹180.00
SGST = ₹180.00
Total Tax = ₹360.00
Amount With Tax = ₹2,360.00

Rate With Tax = ₹1,180.00
```

## 5.1 Default GST

Default CGST:

```text
9%
```

Default SGST:

```text
9%
```

The UI must allow the tax rate to be changed.

The default does not mean the application should hard-code 9% into calculations.

## 5.2 Future tax rates

The architecture must support:

- 0%
- 5%
- 12%
- 18%
- 28%
- custom rates

without changing the GST calculation engine.

For intra-state invoices, the user may enter separate CGST and SGST percentages.

Do not assume every future invoice will always use 9% + 9%.

---

# 6. Invoice item fields

Each invoice item must support:

- Serial number
- Description
- Batch number
- HSN/SAC
- Quantity
- Rate per quantity
- CGST %
- SGST %

Calculated/display-only fields:

- Taxable amount
- CGST amount
- SGST amount
- Total tax
- Rate including tax
- Amount including tax

The UI should clearly distinguish user-entered fields from calculated fields.

---

# 7. Long description requirement

This is a critical requirement.

Descriptions may be:

```text
Short description
```

or:

```text
Very long multi-line description containing model information,
specifications, warranty details and other text.
```

The application must never:

- clip the description
- overlap adjacent columns
- overlap the next row
- force the entire invoice horizontally wider
- shrink the font to an unreadable size just because a description is long

The description cell must wrap.

The row height must grow automatically.

Example:

```text
+----+------------------------------------+-------+
| 1  | Dell Latitude Laptop              | 8471  |
|    | Intel Core i7, 16GB RAM, 512GB    |       |
|    | SSD, Windows 11 Pro, warranty     |       |
+----+------------------------------------+-------+
```

Numeric columns retain their defined widths.

---

# 8. Invoice document requirements

The uploaded supplier invoice is the primary visual/reference document.

The sample contains:

- Supplier/company information
- GSTIN
- State and state code
- Contact information
- Consignee / Ship To
- Buyer / Bill To
- Invoice number
- Invoice date
- Delivery/reference/order information
- Payment/delivery fields
- Item table
- HSN/SAC
- Quantity
- Rate
- Rate including tax
- Amount
- CGST
- SGST
- Tax totals
- Amount in words
- Tax amount in words
- Declaration
- Company PAN
- Bank details
- Authorised signatory
- Computer-generated invoice statement

The application should reproduce the useful structure of this document while keeping the implementation maintainable.

The uploaded reference shows the item and tax structures in its item/tax sections and the declaration/bank/signatory sections near the bottom.

---

# 9. Invoice layout

Target page size:

```text
A4
```

The invoice should be designed as a document template, not as a screenshot or canvas drawing.

Recommended architecture:

```text
Invoice model
    |
    v
HTML template
    |
    v
CSS print layout
    |
    v
PDF
```

The same document representation should be used for print and PDF as much as practical.

---

# 10. PDF layout rules

## 10.1 Fixed columns

The following columns should have controlled widths:

- Sl No
- HSN/SAC
- Batch
- Quantity
- Rate
- GST
- Amount

The description column gets the remaining width.

## 10.2 Dynamic rows

Item rows must dynamically increase in height when description wraps.

## 10.3 Page breaks

If items do not fit on one page:

- Continue the item table on the next page.
- Repeat the table header.
- Do not split a single item row across pages if practical.
- Keep the tax summary after the final item.
- Keep declaration/bank/signatory sections together when possible.
- If they cannot fit, move them to the next page rather than overlapping content.

## 10.4 Font

Use a professional readable font.

Do not reduce font size below an agreed minimum merely to force everything onto one page.

---

# 11. Company configuration

The company information must be configurable.

Settings should include:

- Company name
- Address
- GSTIN
- PAN
- State
- State code
- Phone
- Email
- Website, if applicable
- Bank name
- Account number
- Branch
- IFSC
- Declaration text
- Authorised signatory label

Do not hard-code these values into the PDF template.

---

# 12. Customer information

Customer lookup is optional for the first prototype.

The architecture should support it later.

Potential customer fields:

- Customer name
- Address
- GSTIN
- PAN
- State
- State code
- Phone
- Email

For the initial prototype, customer information may simply be entered into the invoice form.

---

# 13. Product information

Product master/lookup is optional.

Do not block the prototype on product master functionality.

The invoice must allow free-form item entry.

A future product master may contain:

- Product name
- Description
- HSN/SAC
- Default rate
- Default GST
- Unit

---

# 14. Invoice numbering

Invoice numbering must be deterministic and persisted.

Recommended initial format:

```text
SKN/2026-27/001
SKN/2026-27/002
SKN/2026-27/003
```

The numbering strategy must be isolated behind an invoice-number service so that the format can be changed later.

Do not generate invoice numbers only in the UI.

---

# 15. Database

Use SQLite. SQLlite should be outside of the exec or dmg files. First time ask the user where to save the DB data and use it.

Minimum tables:

## company_settings

```text
id
company_name
address
gstin
pan
state
state_code
phone
email
website
bank_name
account_number
branch
ifsc
declaration
authorised_signatory
```

## invoices

```text
id
invoice_number
invoice_date
customer_name
customer_address
customer_gstin
customer_pan
customer_state
customer_state_code
subtotal
total_cgst
total_sgst
total_tax
grand_total
amount_in_words
tax_amount_in_words
created_at
updated_at
```

## invoice_items

```text
id
invoice_id
serial_number
description
batch_number
hsn_sac
quantity
rate
cgst_percent
sgst_percent
taxable_amount
cgst_amount
sgst_amount
total_tax
rate_with_tax
amount_with_tax
```

The stored calculated values are intentional: a historical invoice should remain reproducible even if calculation implementation changes later.

---

# 16. Invoice immutability/history

Once an invoice is issued, editing should be handled carefully.

At minimum:

- Draft invoices may be edited.
- Issued/final invoices should not silently change.
- If editing issued invoices is eventually allowed, provide an explicit edit/revision operation.
- PDF generated for an issued invoice should remain reproducible from stored invoice data.

The exact finalization workflow can be implemented after the prototype.

---

# 17. UI requirements

## 17.1 Dashboard

Provide:

- New Invoice
- Recent invoices
- Search
- Settings

Do not over-design the dashboard.

## 17.2 Invoice screen

Sections:

### Invoice information

- Invoice number
- Invoice date
- Place/state of supply
- Optional delivery/payment fields

### Customer

- Name
- Address
- GSTIN
- PAN
- State
- State code

### Items

Dynamic table.

Buttons:

- Add item
- Remove item
- Duplicate item

### Totals

Display:

- Taxable value
- CGST
- SGST
- Total tax
- Grand total

### Actions

- Save Draft
- Preview
- Generate PDF
- Print

---

# 18. Prototype requirement — FIRST TASK

This is the first task for the AI coding agent.

Do NOT begin by implementing the complete product.

## Task 1 — Project setup and working prototype

Create the project with:

- Python
- Flet
- SQLite
- Decimal
- pytest
- PDF renderer
- basic packaging configuration

Create the basic folder structure.

Implement a single prototype screen containing:

1. Company header
2. Customer details
3. Invoice number/date
4. Dynamic invoice item table
5. Description
6. Batch number
7. HSN/SAC
8. Quantity
9. Rate
10. CGST %
11. SGST %
12. Calculated taxable amount
13. Calculated CGST
14. Calculated SGST
15. Calculated total
16. Long-description wrapping
17. Invoice preview
18. PDF generation

### Prototype test data

Use at least:

```text
Item 1:
Description: short description
Batch: B001
HSN/SAC: 84713010
Quantity: 2
Rate: 82627.12
CGST: 9%
SGST: 9%

Item 2:
Use a deliberately long multi-line description.

Item 3:
Use a very short description.
```

The purpose is to test:

- table behavior
- calculations
- wrapping
- PDF layout
- page behavior

Do not build customer master, product master, advanced reporting, backup, or other secondary functionality in Task 1.

---

# 19. Prototype acceptance criteria

The prototype is accepted only if all are true:

### Calculation

- No monetary calculation uses float.
- Decimal is used.
- GST calculations pass automated tests.
- Rounding is deterministic.
- Display values are correct to 2 decimal places.

### UI

- Application opens as a desktop application.
- Item rows can be added/removed.
- Calculated values update when input changes.
- Long descriptions wrap.
- Columns do not overlap.

### PDF

- PDF is A4.
- Invoice is readable.
- Long descriptions wrap.
- No text overlaps.
- Table headers are correct.
- Totals are visible.
- Tax summary is visible.
- PDF can be opened independently of the application.

### Windows

- Prototype can be packaged and launched without Python installed.

### Architecture

- GST logic is independent of Flet.
- PDF generation is independent of Flet.
- SQLite access is isolated.
- Unit tests exist for calculation logic.

---

# 20. Subsequent implementation tasks

After Task 1 is accepted, implement in this order.

## Task 2 — Company Settings

Implement:

- company profile
- GSTIN
- PAN
- address
- bank details
- declaration
- authorised signatory

Persist to SQLite.

## Task 3 — Customer Management

Implement:

- add customer
- edit customer
- search customer
- select customer for invoice

## Task 4 — Invoice Persistence

Implement:

- save draft
- open draft
- update draft
- invoice numbering
- invoice history

## Task 5 — Full Invoice Template

Implement the complete invoice based on the supplied reference.

Include:

- company section
- buyer/ship-to sections
- invoice metadata
- item table
- tax summary
- amount in words
- declaration
- bank details
- authorised signatory

## Task 6 — Robust PDF Pagination

Test:

- 1 item
- 3 items
- 10 items
- 20+ items
- long descriptions
- combinations of long and short descriptions
- page boundary cases

## Task 7 — Printing

Implement Windows printing.

Verify that printed output matches PDF.

## Task 8 — Invoice History

Implement:

- invoice list
- search
- open
- preview
- PDF
- print

## Task 9 — Product Master (Optional)

Implement only if useful.

## Task 10 — Backup/Restore

Implement local database backup.

A simple backup mechanism should allow the user to copy/export the SQLite database safely.

## Task 11 — Packaging

Produce:

- Windows installer
- macOS application

Test on real target machines.

---

# 21. Testing strategy

## 21.1 Unit tests

The GST engine must have extensive unit tests.

Test:

- zero GST
- 5%
- 12%
- 18%
- 28%
- custom rates
- decimal rates
- quantity 1
- fractional quantity if allowed
- large amounts
- small amounts
- rounding boundaries
- multiple invoice items

## 21.2 Property/invariant tests

Verify:

```text
grand_total = taxable_total + total_tax
total_tax = total_cgst + total_sgst
```

within the defined rounding model.

## 21.3 UI tests

Verify:

- add item
- delete item
- update quantity
- update rate
- update GST
- long description
- empty description validation
- invalid numeric input

## 21.4 PDF tests

At minimum manually inspect generated PDFs for:

- one item
- multiple items
- long description
- many rows
- page break
- totals
- declaration/signatory

---

# 22. Validation rules

The application must validate:

- Invoice date is valid.
- Invoice number is present before finalization.
- Description is present for every item.
- HSN/SAC is present where required by the configured invoice rules.
- Quantity is numeric and greater than zero unless explicitly permitted otherwise.
- Rate is not negative.
- Tax percentages are not negative.
- Customer name is present.
- Company GSTIN is valid in format if GSTIN validation is enabled.
- Numeric fields reject malformed input.

Do not over-restrict fields unless there is a clear business requirement.

---

# 23. Error handling

Errors should be understandable to a business user.

Bad:

```text
ValueError: invalid literal for Decimal()
```

Good:

```text
Please enter a valid rate.
```

Unexpected technical errors should be logged locally while presenting a simple message to the user.

---

# 24. Logging

Use Python's standard logging.

Logs should be local.

Do not log:

- unnecessary customer PII
- full invoice contents unless required for debugging
- passwords or secrets

---

# 25. Offline requirement

Normal invoice creation must work without internet.

The application must not depend on:

- internet-based GST calculation
- cloud APIs
- remote databases
- online authentication
- online PDF services

All normal functionality must be local.

---

# 26. Security

This is a small local business application.

Minimum requirements:

- Store database locally.
- Do not expose a network port unless a future requirement explicitly needs one.
- Do not transmit invoice/customer data externally.
- Do not include telemetry unless explicitly approved.
- Protect backups appropriately.

---

# 27. Performance

The application should comfortably handle:

- 1–2 concurrent users
- hundreds/thousands of historical invoices
- invoices with dozens of line items

Do not optimize prematurely.

SQLite is sufficient for the expected scale.

---

# 28. Code quality rules for AI agents

AI coding agents must:

1. Prefer simple code over abstractions that do not solve a current problem.
2. Keep UI, business logic, persistence and PDF rendering separate.
3. Add tests with every change to financial calculation logic.
4. Never silently change GST calculation behavior.
5. Never introduce float into financial calculations.
6. Never duplicate calculation logic in UI and PDF layers.
7. Avoid hard-coded company information.
8. Avoid hard-coded tax rates except as configurable defaults.
9. Keep database migrations/versioning manageable.
10. Document non-obvious rounding decisions.
11. Do not add cloud infrastructure.
12. Do not add unnecessary dependencies.

---

# 29. AI-agent workflow

For every implementation task:

1. Read this specification.
2. Inspect the existing code.
3. Identify the smallest required change.
4. Implement it.
5. Add/update tests.
6. Run the tests.
7. Run the application when UI changes are made.
8. Validate generated PDF when document changes are made.
9. Report:
   - files changed
   - functionality implemented
   - tests run
   - known limitations

Agents must not proceed to later tasks until the current task's acceptance criteria are satisfied.

---

# 30. Definition of Done

The application is complete when a user can:

1. Open Sai Krishna Networks Invoice Generator from a desktop icon.
2. Create an invoice.
3. Enter customer details.
4. Add any number of invoice items.
5. Enter description, batch, HSN/SAC, quantity and rate.
6. Enter/change CGST and SGST.
7. See accurate calculated values immediately.
8. Save the invoice.
9. Preview the invoice.
10. Generate an A4 PDF.
11. Print the invoice.
12. Reopen historical invoices.
13. Generate the same invoice PDF again.
14. Operate without internet.
15. Run the application on Windows.
16. Optionally run the same application on supported macOS.

The invoice must remain visually correct when descriptions are short, long, or when the invoice spans multiple pages.

---

# 31. Explicit non-goals for initial release

Do not implement unless requested later:

- E-invoicing/IRN submission
- GST portal integration
- E-way bill integration
- Online payment gateway
- Cloud synchronization
- Multi-tenant architecture
- Role-based access control
- Mobile application
- Inventory management
- Accounting system
- Purchase management
- Full ERP functionality

These may be future integrations, but they are outside the initial scope.
