import os
import sys
from jinja2 import Environment, FileSystemLoader
from src.domain.models import Invoice
from src.domain.gst_engine import calculate_invoice

class InvoiceDocumentRenderer:
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            candidates = []
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                candidates.append(os.path.join(sys._MEIPASS, "src", "rendering"))
                candidates.append(os.path.join(sys._MEIPASS, "rendering"))
                candidates.append(sys._MEIPASS)
            
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(os.path.join(exe_dir, "_internal", "src", "rendering"))
            candidates.append(os.path.join(exe_dir, "src", "rendering"))
            candidates.append(os.path.dirname(os.path.abspath(__file__)))
            candidates.append(os.path.join(os.getcwd(), "src", "rendering"))

            template_dir = os.path.dirname(os.path.abspath(__file__))
            for cand in candidates:
                if cand and os.path.exists(os.path.join(cand, "template.html")):
                    template_dir = cand
                    break

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
