import os
import pytest
from src.services.config import ConfigService, AppConfig

def test_config_service_first_run(tmp_path):
    config_file = str(tmp_path / "test_config.json")
    service = ConfigService(config_file=config_file)
    
    assert service.is_first_run() is True

    custom_db_dir = str(tmp_path / "custom_data")
    custom_pdf_dir = str(tmp_path / "custom_pdf")
    
    service.save_config(AppConfig(
        db_directory=custom_db_dir,
        pdf_export_directory=custom_pdf_dir,
        is_configured=True,
    ))

    assert service.is_first_run() is False
    assert service.get_db_path() == os.path.join(custom_db_dir, "skn_invoices.db")
    assert service.get_pdf_export_dir() == custom_pdf_dir
    assert os.path.exists(custom_db_dir)
    assert os.path.exists(custom_pdf_dir)

def test_config_service_reload(tmp_path):
    config_file = str(tmp_path / "test_config.json")
    service1 = ConfigService(config_file=config_file)
    service1.save_config(AppConfig(
        db_directory=str(tmp_path / "d1"),
        pdf_export_directory=str(tmp_path / "p1"),
        is_configured=True,
    ))

    service2 = ConfigService(config_file=config_file)
    assert service2.is_first_run() is False
    assert service2.config.db_directory == str(tmp_path / "d1")
