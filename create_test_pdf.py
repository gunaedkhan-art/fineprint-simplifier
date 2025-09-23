#!/usr/bin/env python3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_test_pdf():
    # Create a PDF with the test contract content
    filename = "test_contract.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Set font
    c.setFont("Helvetica", 12)
    
    # Add content
    content = """SERVICE AGREEMENT

This agreement contains the following terms:

1. EARLY TERMINATION FEE: Customer agrees to pay an early termination fee of $200 if service is cancelled before the end of the contract term.

2. AUTOMATIC RENEWAL: This contract will automatically renew for additional 12-month periods unless cancelled in writing 30 days before expiration.

3. BINDING ARBITRATION: Any disputes arising from this agreement shall be resolved through binding arbitration. Customer waives their right to sue in court.

4. LATE PAYMENT PENALTIES: A late payment fee of $25 will be charged for payments received more than 10 days after the due date.

5. NON-REFUNDABLE: All payments made under this agreement are non-refundable.

6. LIMITED LIABILITY: Company's liability is limited to the amount paid by customer in the 12 months preceding the claim.

7. GRACE PERIOD: Customer has a grace period of 14 days to cancel without penalty from the date of signing.

8. MONEY-BACK GUARANTEE: If customer is not satisfied within the first 30 days, they may request a full refund.

9. DATA PROTECTION: Customer data will be kept secure and confidential in accordance with GDPR requirements.

10. NO WIN NO FEE: Legal representation is provided on a no win no fee basis for eligible cases."""
    
    # Split content into lines and draw them
    lines = content.split('\n')
    y_position = height - 50
    
    for line in lines:
        if y_position < 50:  # Start new page if needed
            c.showPage()
            y_position = height - 50
            c.setFont("Helvetica", 12)
        
        c.drawString(50, y_position, line)
        y_position -= 20
    
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_test_pdf()
