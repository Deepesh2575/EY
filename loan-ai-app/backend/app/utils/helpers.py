from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO
from typing import Dict, Any

def generate_sanction_letter(loan_details: Dict[str, Any]) -> bytes:
    """
    Generate a professional PDF sanction letter
    
    Args:
        loan_details: Dictionary containing loan information
    
    Returns:
        PDF file as bytes
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Colors
    primary_color = colors.HexColor('#2563eb')
    dark_gray = colors.HexColor('#1e293b')
    
    # Header Section
    c.setFillColor(primary_color)
    c.rect(0, height - 100, width, 100, fill=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1*inch, height - 50, "LOAN SANCTION LETTER")
    
    # Date
    c.setFont("Helvetica", 12)
    c.setFillColor(dark_gray)
    c.drawString(1*inch, height - 1.3*inch, f"Date: {datetime.now().strftime('%B %d, %Y')}")
    
    # Reference Number
    ref_number = f"REF/{datetime.now().strftime('%Y%m%d')}/{(loan_details.get('name') or 'CUSTOMER')[:5].upper()}"
    c.drawString(1*inch, height - 1.5*inch, f"Reference: {ref_number}")
    
    # Content Section
    y_position = height - 2.5*inch
    c.setFont("Helvetica", 12)
    c.setFillColor(dark_gray)
    
    # Greeting
    name = loan_details.get('name', 'Valued Customer')
    c.drawString(1*inch, y_position, f"Dear {name},")
    y_position -= 0.4*inch
    
    # Main content
    content_lines = [
        "",
        "We are pleased to inform you that your loan application has been APPROVED.",
        "",
        "LOAN DETAILS:",
        "",
        f"Loan Amount: ₹{loan_details.get('loan_amount', 0):,.2f}",
        f"Interest Rate: {loan_details.get('interest_rate', 12.5)}% per annum",
        f"Tenure: {loan_details.get('tenure', 36)} months",
        f"Monthly EMI: ₹{loan_details.get('monthly_emi', 0):,.2f}",
        "",
        "TERMS AND CONDITIONS:",
        "",
        "1. This sanction is valid for 30 days from the date of this letter.",
        "2. Final disbursement is subject to verification of all documents.",
        "3. Interest rates are subject to change as per market conditions.",
        "4. Please ensure timely EMI payments to maintain your credit score.",
        "",
        "NEXT STEPS:",
        "",
        "Our team will contact you within 2-3 business days to complete the",
        "disbursement process. Please keep the following documents ready:",
        "",
        "- Original identity proof",
        "- Address proof",
        "- Bank account details",
        "",
        "Thank you for choosing our services. We look forward to serving you.",
        "",
        "",
        "Sincerely,",
        "",
        "Loan Department",
        "AI Loan Sales Platform"
    ]
    
    for line in content_lines:
        if y_position < 1*inch:  # Start new page if needed
            c.showPage()
            y_position = height - 1*inch
        
        c.drawString(1*inch, y_position, line)
        y_position -= 0.3*inch
    
    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(1*inch, 0.5*inch, "This is a system-generated document. For queries, contact support.")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
