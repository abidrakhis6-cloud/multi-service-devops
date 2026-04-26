"""
Invoice Generator for MultiServe
Generates PDF invoices for orders
"""
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.base import ContentFile
from datetime import datetime
import os


def generate_invoice_number():
    """Generate unique invoice number: FACT-YYYYMMDD-XXXX"""
    today = datetime.now()
    prefix = f"FACT-{today.strftime('%Y%m%d')}"
    
    # Get last invoice number for today
    from .models import Invoice
    last_invoice = Invoice.objects.filter(
        invoice_number__startswith=prefix
    ).order_by('-invoice_number').first()
    
    if last_invoice:
        last_num = int(last_invoice.invoice_number.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}-{new_num:04d}"


def create_invoice(order, payment):
    """Create invoice for an order"""
    from .models import Invoice
    
    # Calculate amounts
    amount_ttc = float(order.total_price)
    vat_rate = 20.0  # 20% TVA
    amount_ht = amount_ttc / (1 + vat_rate / 100)
    vat_amount = amount_ttc - amount_ht
    
    # Generate invoice number
    invoice_number = generate_invoice_number()
    
    # Create invoice
    invoice = Invoice.objects.create(
        order=order,
        invoice_number=invoice_number,
        amount_ttc=amount_ttc,
        amount_ht=round(amount_ht, 2),
        vat_amount=round(vat_amount, 2),
        vat_rate=vat_rate,
        store_name=order.store.name if order.store else "MultiServe",
        store_address="12 Rue de Rivoli, 75004 Paris",  # Default store address
        store_siret="12345678900012",  # Example SIRET
        customer_name=f"{order.user.first_name} {order.user.last_name}".strip() or order.user.username,
        customer_email=order.user.email,
        customer_address=order.delivery_address,
        payment_method=payment.get_method_display(),
        payment_date=payment.created_at
    )
    
    # Generate PDF (simplified - in production use WeasyPrint or xhtml2pdf)
    pdf_filename = f"facture_{invoice_number}.pdf"
    
    # For now, we'll store the HTML template as PDF URL
    # In production, convert HTML to PDF
    invoice.pdf_url = f"/media/invoices/{pdf_filename}"
    invoice.save()
    
    return invoice


def generate_invoice_html(invoice):
    """Generate HTML for invoice"""
    context = {
        'invoice': invoice,
        'order': invoice.order,
        'items': invoice.order.cart.items.all(),
        'logo_url': f"{settings.STATIC_URL}images/logo.png"
    }
    
    return render_to_string('invoice_template.html', context)
