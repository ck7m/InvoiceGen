import os
import logging
from src.domain.models import Invoice
from src.rendering.document import InvoiceDocumentRenderer

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        self.renderer = InvoiceDocumentRenderer()

    def generate_pdf(self, invoice: Invoice, output_path: str) -> str:
        """
        Generate A4 PDF from Invoice model.
        Uses WeasyPrint as primary engine, falls back to xhtml2pdf if WeasyPrint fails.
        """
        html_content = self.renderer.render_html(invoice)
        
        # Try WeasyPrint first
        try:
            from weasyprint import HTML
            logger.info("Generating PDF using WeasyPrint engine...")
            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"PDF successfully generated with WeasyPrint at: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"WeasyPrint PDF generation failed/unavailable ({e}). Falling back to xhtml2pdf engine...")
            
        # Fallback to xhtml2pdf
        try:
            from xhtml2pdf import pisa
            with open(output_path, "wb") as output_file:
                pisa_status = pisa.CreatePDF(html_content, dest=output_file)
                if pisa_status.err:
                    raise RuntimeError(f"xhtml2pdf error status: {pisa_status.err}")
            logger.info(f"PDF successfully generated with xhtml2pdf at: {output_path}")
            return output_path
        except Exception as err:
            logger.error(f"xhtml2pdf generation failed: {err}")
            raise RuntimeError(f"Failed to generate PDF using all available engines: {err}")
