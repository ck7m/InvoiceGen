# Sai Krishna Networks GST Invoice Generator

A lightweight, offline-first desktop application for creating, managing, and printing GST-compliant tax invoices with accurate financial calculations, SQLite persistence, and A4 PDF export.

---

## 🌟 Key Features

- **Offline-First & Fast**: Operates completely offline without cloud dependencies or external APIs.
- **Accurate Financial Calculations**: Uses Python `Decimal` with strict `ROUND_HALF_UP` quantization to ensure zero floating-point rounding errors.
- **Persistent Data Outside App Bundle**: All SQLite data (`company_settings`, `invoices`, `invoice_items`) is stored safely outside the application in `~/Documents/SKN_Invoice_Generator/data/` (user-configurable).
- **Auto-Incrementing Invoice Numbering**: Deterministic Indian Financial Year numbering (`SKN/2026-27/001`) with full manual edit support.
- **A4 PDF Generation & Pagination**: Generates print-ready A4 PDFs with repeating table headers across pages and wrapped descriptions.
- **Cross-Platform Printing**: Direct printing support on Windows (native print verb), macOS (`lp`/preview), and Linux (`lpr`).
- **Invoice History & Search**: Real-time searchable history list with capabilities to re-open historical invoices in the editor, export PDFs, print, and delete.

---

## 🚀 Local Setup Instructions

### Prerequisites
- Python 3.12 or newer
- Either `uv` (recommended) or standard `pip` + `venv`

---

### Option 1: Quick Setup with `uv` (Recommended)

1. **Clone or navigate to the repository:**
   ```bash
   cd InvoiceGen
   ```

2. **Sync dependencies and virtual environment:**
   ```bash
   uv sync
   ```

3. **Run the desktop application:**
   ```bash
   uv run python src/main.py
   ```

4. **Run the test suite:**
   ```bash
   uv run pytest -v
   ```

---

### Option 2: Setup with Standard Python `venv` & `pip`

1. **Create and activate a virtual environment:**
   ```bash
   # On macOS / Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows (PowerShell):
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies from `requirements.txt`:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python src/main.py
   ```

4. **Run automated tests:**
   ```bash
   pytest -v
   ```

---

## 📦 Installers & Standalone Packages: Windows vs macOS

PyInstaller builds platform-native packages in the `dist/` directory.

| Platform | Built Package / Executable Path | How to Run / Install |
| :--- | :--- | :--- |
| **macOS** | `dist/SKN_Invoice_Generator.app` | Drag `SKN_Invoice_Generator.app` to your `/Applications` folder (or double-click to run). |
| **macOS (CLI/Folder)** | `dist/SKN_Invoice_Generator/SKN_Invoice_Generator` | Run directly from Terminal. |
| **Windows** | `dist\SKN_Invoice_Generator\SKN_Invoice_Generator.exe` | Double-click `SKN_Invoice_Generator.exe` or create a shortcut on Desktop. |
| **Windows (Installer)**| Inno Setup script can wrap `dist\SKN_Invoice_Generator\` into a `Setup_SKN_InvoiceGen.exe` installer wizard. | Run the setup `.exe` installer. |

> [!NOTE]
> PyInstaller produces binaries for the operating system on which the build command is executed.
> - To build the **macOS `.app`**, run `python scripts/build_executable.py` on macOS.
> - To build the **Windows `.exe`**, run `python scripts/build_executable.py` on Windows.

---

## 🔨 How to Build Standalone Executables

To package the standalone desktop app for your current operating system:

```bash
# Using uv:
uv run python scripts/build_executable.py

# Using activated virtual environment:
python scripts/build_executable.py
```

The output bundle and binaries will be generated inside the `dist/` folder.

---

## 📁 Storage & Configuration

When you first launch the application, it creates its configuration file at `~/.skn_invoice_config.json`.

Default storage locations:
- **SQLite Database:** `~/Documents/SKN_Invoice_Generator/data/skn_invoices.db`
- **PDF Invoices:** `~/Documents/SKN_Invoice_Generator/invoices/`

You can change these directories anytime in the **Company & Storage Settings** tab inside the app.

---

## 🧪 Test Suite

The project includes 34 automated unit and integration tests covering:
- GST calculation engine (0%, 5%, 12%, 18%, 28%, rounding boundaries)
- Company settings persistence in SQLite
- Invoice persistence, auto-numbering, searching, and cascade deletion
- A4 PDF generation and multi-page pagination with long descriptions
- Cross-platform printing service
- UI components and tab lifecycle

Run the full test suite with:
```bash
pytest -v
```
