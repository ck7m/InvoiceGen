import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict

DEFAULT_BASE_DIR = Path.home() / "Documents" / "SKN_Invoice_Generator"

@dataclass
class AppConfig:
    db_directory: str = str(DEFAULT_BASE_DIR / "data")
    pdf_export_directory: str = str(DEFAULT_BASE_DIR / "invoices")
    is_configured: bool = False
    
    @property
    def db_path(self) -> str:
        return os.path.join(self.db_directory, "skn_invoices.db")

class ConfigService:
    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = str(Path.home() / ".skn_invoice_config.json")
        self.config_file = config_file
        self.config = self.load_config()
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure storage directories exist."""
        try:
            os.makedirs(self.config.db_directory, exist_ok=True)
            os.makedirs(self.config.pdf_export_directory, exist_ok=True)
        except Exception:
            pass

    def load_config(self) -> AppConfig:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return AppConfig(
                        db_directory=data.get("db_directory", str(DEFAULT_BASE_DIR / "data")),
                        pdf_export_directory=data.get("pdf_export_directory", str(DEFAULT_BASE_DIR / "invoices")),
                        is_configured=data.get("is_configured", True),
                    )
            except Exception:
                pass
        return AppConfig(is_configured=False)

    def save_config(self, config: AppConfig):
        config.is_configured = True
        self.config = config
        self._ensure_directories()
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(asdict(self.config), f, indent=2)

    def get_db_path(self) -> str:
        return self.config.db_path

    def get_pdf_export_dir(self) -> str:
        return self.config.pdf_export_directory

    def is_first_run(self) -> bool:
        return not self.config.is_configured
