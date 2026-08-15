import os
import pytest
from unittest.mock import patch, MagicMock
from src.services.print_service import PrintService

def test_print_service_non_existent_file():
    success, msg = PrintService.print_pdf("/non/existent/path/invoice.pdf")
    assert not success
    assert "File not found" in msg

def test_print_service_windows(tmp_path):
    dummy_pdf = tmp_path / "test_win.pdf"
    dummy_pdf.write_text("%PDF-1.4 dummy content")

    with patch("platform.system", return_value="Windows"), \
         patch("os.startfile", create=True) as mock_startfile:
        success, msg = PrintService.print_pdf(str(dummy_pdf))
        assert success
        assert "print preview" in msg
        mock_startfile.assert_called_once_with(os.path.abspath(str(dummy_pdf)))

def test_print_service_macos(tmp_path):
    dummy_pdf = tmp_path / "test_mac.pdf"
    dummy_pdf.write_text("%PDF-1.4 dummy content")

    mock_res = MagicMock()
    mock_res.returncode = 0

    with patch("platform.system", return_value="Darwin"), \
         patch("subprocess.run", return_value=mock_res) as mock_sub:
        success, msg = PrintService.print_pdf(str(dummy_pdf))
        assert success
        assert "print preview" in msg
        mock_sub.assert_called_once_with(["open", os.path.abspath(str(dummy_pdf))], check=True)

