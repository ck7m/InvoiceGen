import datetime
import re
from typing import List, Optional

def get_current_financial_year(dt: Optional[datetime.date] = None) -> str:
    """
    Returns the Indian Financial Year string in 'YYYY-YY' format.
    Financial Year runs from April 1 to March 31.
    Example: August 2026 -> '2026-27'
             February 2027 -> '2026-27'
    """
    if dt is None:
        dt = datetime.date.today()
    
    year = dt.year
    if dt.month >= 4:
        start_year = year
        end_year = (year + 1) % 100
    else:
        start_year = year - 1
        end_year = year % 100
        
    return f"{start_year}-{end_year:02d}"

class InvoiceNumberService:
    @staticmethod
    def generate_next_number(existing_numbers: List[str], prefix: str = "SKN", dt: Optional[datetime.date] = None) -> str:
        """
        Generates the next sequential invoice number.
        Format: {prefix}/{financial_year}/{3-digit sequence}
        Example: SKN/2026-27/001
        
        The user can always manually edit this value in the invoice editor.
        """
        fy = get_current_financial_year(dt)
        pattern = re.compile(rf"^{re.escape(prefix)}/{re.escape(fy)}/(\d+)$", re.IGNORECASE)
        
        max_seq = 0
        for num in existing_numbers:
            if not num:
                continue
            match = pattern.match(num.strip())
            if match:
                try:
                    seq = int(match.group(1))
                    if seq > max_seq:
                        max_seq = seq
                except ValueError:
                    pass
                    
        next_seq = max_seq + 1
        return f"{prefix}/{fy}/{next_seq:03d}"
