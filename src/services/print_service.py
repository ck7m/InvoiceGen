import os
import platform
import subprocess
import logging

logger = logging.getLogger(__name__)

class PrintService:
    @staticmethod
    def print_pdf(pdf_path: str) -> tuple[bool, str]:
        """
        Opens the generated PDF in the operating system's native viewer
        (macOS Preview, Windows PDF Viewer / Acrobat / Edge, Linux Document Viewer)
        to allow the user to review the print preview, adjust printer settings, and print.
        
        Returns (success: bool, message: str)
        """
        if not os.path.exists(pdf_path):
            return False, f"File not found: {pdf_path}"

        system = platform.system().lower()
        abs_path = os.path.abspath(pdf_path)

        try:
            if "windows" in system:
                # Open PDF in default Windows application (Edge / Acrobat) for print preview
                try:
                    os.startfile(abs_path)
                    return True, "Opened invoice print preview in default PDF viewer."
                except Exception:
                    subprocess.run(["cmd", "/c", "start", "", abs_path], shell=True, check=True)
                    return True, "Opened invoice print preview."
            elif "darwin" in system:
                # macOS: open in Preview.app for print preview
                subprocess.run(["open", abs_path], check=True)
                return True, "Opened invoice print preview in Preview."
            else:
                # Linux / Unix
                subprocess.run(["xdg-open", abs_path], check=True)
                return True, "Opened invoice print preview in document viewer."
        except Exception as e:
            logger.error(f"Print preview error: {e}")
            return False, f"Failed to open print preview: {e}"

