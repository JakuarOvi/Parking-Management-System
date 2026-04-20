"""Utility functions for the parking application."""
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime


def generate_receipt_pdf(booking, payment):
    """Generate a PDF receipt for a booking/payment."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#185FA5'),
        alignment=1
    )
    elements.append(Paragraph("ParkManager - Receipt", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Receipt details
    details = [
        ['Booking ID:', f"#{booking.id}"],
        ['Date & Time:', str(booking.created_at)],
        ['Vehicle Type:', booking.vehicle_type],
        ['Entry Time:', str(booking.entry_time) if booking.entry_time else 'N/A'],
        ['Exit Time:', str(booking.exit_time) if booking.exit_time else 'N/A'],
        ['Status:', booking.status],
        ['', ''],
        ['Amount:', f"{payment.amount} BDT"],
        ['Payment Method:', payment.payment_method],
        ['Payment Status:', payment.status],
    ]
    
    table = Table(details, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    footer = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
