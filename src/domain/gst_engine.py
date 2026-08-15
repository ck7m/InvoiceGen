from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple
from src.domain.models import InvoiceItem, Invoice

TWO_PLACES = Decimal("0.01")

def quantize_money(amount: Decimal) -> Decimal:
    """Quantize financial amount to 2 decimal places using ROUND_HALF_UP."""
    if not isinstance(amount, Decimal):
        raise TypeError(f"Expected Decimal, got {type(amount).__name__}")
    return amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def calculate_item(
    quantity: Decimal,
    rate: Decimal,
    cgst_percent: Decimal,
    sgst_percent: Decimal
) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    """
    Calculate GST fields for an invoice item.
    Returns: (taxable_amount, cgst_amount, sgst_amount, total_tax, rate_with_tax, amount_with_tax)
    All inputs and outputs MUST be Decimal.
    """
    if not isinstance(quantity, Decimal) or not isinstance(rate, Decimal) or \
       not isinstance(cgst_percent, Decimal) or not isinstance(sgst_percent, Decimal):
        raise TypeError("All parameters to calculate_item must be Decimal instances")

    taxable_amount = quantize_money(quantity * rate)
    
    cgst_rate_frac = cgst_percent / Decimal("100")
    sgst_rate_frac = sgst_percent / Decimal("100")
    
    cgst_amount = quantize_money(taxable_amount * cgst_rate_frac)
    sgst_amount = quantize_money(taxable_amount * sgst_rate_frac)
    
    total_tax = cgst_amount + sgst_amount
    amount_with_tax = taxable_amount + total_tax
    
    unit_tax = quantize_money(rate * (cgst_rate_frac + sgst_rate_frac))
    rate_with_tax = rate + unit_tax

    return taxable_amount, cgst_amount, sgst_amount, total_tax, rate_with_tax, amount_with_tax

def calculate_invoice(invoice: Invoice) -> Invoice:
    """
    Calculate all item amounts and invoice summary totals in place.
    Ensures mathematical invariants:
    - grand_total == subtotal + total_tax
    - total_tax == total_cgst + total_sgst
    """
    subtotal = Decimal("0.00")
    total_cgst = Decimal("0.00")
    total_sgst = Decimal("0.00")

    for idx, item in enumerate(invoice.items, start=1):
        item.serial_number = idx
        (
            item.taxable_amount,
            item.cgst_amount,
            item.sgst_amount,
            item.total_tax,
            item.rate_with_tax,
            item.amount_with_tax
        ) = calculate_item(
            item.quantity,
            item.rate,
            item.cgst_percent,
            item.sgst_percent
        )
        
        subtotal += item.taxable_amount
        total_cgst += item.cgst_amount
        total_sgst += item.sgst_amount

    invoice.subtotal = subtotal
    invoice.total_cgst = total_cgst
    invoice.total_sgst = total_sgst
    invoice.total_tax = total_cgst + total_sgst
    invoice.grand_total = invoice.subtotal + invoice.total_tax

    invoice.amount_in_words = number_to_words_indian(invoice.grand_total)
    invoice.tax_amount_in_words = number_to_words_indian(invoice.total_tax)

    return invoice

def number_to_words_indian(amount: Decimal) -> str:
    """Convert Decimal amount to Indian Currency format words."""
    amount = quantize_money(amount)
    rupees = int(amount)
    paise = int((amount - Decimal(rupees)) * 100)

    rupee_words = _num_to_words_int(rupees) if rupees > 0 else "Zero"
    words = f"INR {rupee_words} Rupees"
    
    if paise > 0:
        paise_words = _num_to_words_int(paise)
        words += f" and {paise_words} Paise"
        
    return words + " Only"

def _num_to_words_int(n: int) -> str:
    if n == 0:
        return "Zero"

    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
             "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
             "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def convert_below_thousand(num: int) -> str:
        res = []
        if num >= 100:
            res.append(f"{units[num // 100]} Hundred")
            num %= 100
        if num >= 20:
            res.append(tens[num // 10])
            if num % 10 > 0:
                res.append(units[num % 10])
        elif num > 0:
            res.append(units[num])
        return " ".join(res)

    parts = []
    # Crores (10^7)
    if n >= 10000000:
        crores = n // 10000000
        parts.append(f"{_num_to_words_int(crores)} Crore")
        n %= 10000000

    # Lakhs (10^5)
    if n >= 100000:
        lakhs = n // 100000
        parts.append(f"{convert_below_thousand(lakhs)} Lakh")
        n %= 100000

    # Thousands (10^3)
    if n >= 1000:
        thousands = n // 1000
        parts.append(f"{convert_below_thousand(thousands)} Thousand")
        n %= 1000

    if n > 0:
        parts.append(convert_below_thousand(n))

    return " ".join(parts)
