# Sai Krishna Networks GST Invoice Generator — Architecture

## 1. Purpose

A small, offline-first desktop GST invoice generator for Sai Krishna Networks.

Primary platform: Windows  
Secondary platform: macOS  
Expected users: 1–2  
Network/cloud dependency: None required

The application must allow a user to enter invoice/customer/item information, calculate GST accurately, preview the invoice, print it, and save it as PDF.

The supplied sample supplier invoice is the visual reference for the invoice document structure. It contains company/supplier details, consignee and buyer information, invoice metadata, item details including HSN/SAC/quantity/rate/amount, CGST/SGST tax summary, amount in words, declaration, bank details and authorised signatory.

## 2. Technology Decision

### Recommended stack

- Language: Python 3.12+
- UI: Flet
- Database: SQLite
- Money/calculation: Python `Decimal`
- PDF: HTML/CSS invoice template rendered to PDF
- Packaging: Flet Build
- Tests: pytest
- Dependency management: `pyproject.toml`

### Architectural principle

The Flet UI must NOT contain GST/business calculations.

Business logic must be independent of the UI so that the UI could later be replaced by PySide6 or another framework without rewriting the GST engine.

## 3. High-level architecture

```text
                    Flet Desktop UI
                           |
                           v
                 Application Services
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     GST Engine        Invoice Model      SQLite
      Decimal             |              Repository
          |               |
          +-------+-------+
                  |
                  v
           Invoice Renderer
                  |
                  v
             HTML + CSS
                  |
                  v
             PDF Generator
                  |
             +----+----+
             |         |
             v         v
            PDF      Printer
```

## 4. Layer responsibilities

### UI layer

Responsible only for:
- Forms
- Tables
- Input validation feedback
- Navigation
- Preview
- Save/Print/PDF actions
- Displaying calculated values

It must not implement financial calculations.

### Domain layer

Contains:
- Invoice
- InvoiceItem
- Customer
- CompanySettings
- tax-related value objects where useful

Domain objects should use `Decimal` for monetary and percentage values.

### GST calculation layer

Responsible for:
- Taxable amount
- CGST
- SGST
- Total tax
- Tax-inclusive rate
- Tax-inclusive amount
- Explicit rounding rules

This layer must be deterministic and heavily unit-tested.

### Persistence layer

SQLite stores:
- Company settings
- Customers
- Optional products
- Invoices
- Invoice items

### Document layer

Responsible for:
- Converting invoice data into HTML
- A4 layout
- Dynamic row height
- Long description wrapping
- Page breaks
- Tax summary
- Amount in words
- Declaration
- Bank details
- Authorised signatory

### Packaging layer

Build standalone Windows and macOS applications.

## 5. Data flow

```text
User input
   |
   v
Validation
   |
   v
Domain Invoice
   |
   v
GST Calculator
   |
   v
Calculated Invoice
   |
   +----> UI preview
   |
   +----> HTML template
              |
              v
             PDF
              |
              v
           Print/save
```

## 6. Important architectural rules

1. Never use binary floating point for money calculations.
2. Never use Python `float` for monetary values or GST calculations.
3. Use `Decimal` with explicit conversion from strings.
4. Never construct `Decimal` from a binary float.
5. Define and test rounding rules explicitly.
6. Store invoice calculation results so a historical invoice remains reproducible.
7. The PDF must be generated from invoice data, not from a screenshot of the UI.
8. The invoice renderer must be independent from the Flet UI.
9. Long descriptions must wrap naturally and increase row height.
10. Fixed-width numeric columns must not be displaced by long descriptions.
11. A4 page layout must be deterministic and tested with short and long descriptions.
12. Printing and PDF generation should use the same invoice document representation wherever practical.
13. No cloud service is required for normal operation.
14. The application must work without an internet connection after installation.
15. Database backup/export should be considered before production release.
