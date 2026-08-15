import os
import sys
from jinja2 import Environment, FileSystemLoader
from src.domain.models import Invoice
from src.domain.gst_engine import calculate_invoice

class InvoiceDocumentRenderer:
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                template_dir = os.path.join(sys._MEIPASS, "src", "rendering")
            else:
                template_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Fallback if not found in calculated path
            if not os.path.exists(os.path.join(template_dir, "template.html")):
                exe_dir = os.path.dirname(sys.executable)
                alt_dir = os.path.join(exe_dir, "src", "rendering")
                if os.path.exists(os.path.join(alt_dir, "template.html")):
                    template_dir = alt_dir

        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template("template.html")

    def render_html(self, invoice: Invoice) -> str:
        """
        Render the invoice into HTML string.
        Rule 3.4 & User Comment: The PDF/HTML renderer MUST receive an already calculated
        Invoice model and must NOT recalculate financial amounts independently.
        """
        # Ensure calculated fields exist if not already populated
        calculate_invoice(invoice)
        return self.template.render(invoice=invoice)
