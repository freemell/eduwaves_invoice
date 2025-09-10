from flask import Flask, render_template, request, jsonify, send_file
import json
import pandas as pd
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

app = Flask(__name__)

# Load data
def load_books():
    try:
        with open('books_database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_schools():
    try:
        df = pd.read_csv('unique_schools.csv')
        return df.to_dict('records')
    except FileNotFoundError:
        return []

# Global data - loaded on first request
books_data = None
schools_data = None

def get_books_data():
    global books_data
    if books_data is None:
        books_data = load_books()
    return books_data

def get_schools_data():
    global schools_data
    if schools_data is None:
        schools_data = load_schools()
    return schools_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/books/search')
def search_books():
    books_data = get_books_data()
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify(books_data[:20])
    
    results = []
    for book in books_data:
        if (query in book['title'].lower() or 
            query in book['subject'].lower() or 
            query in book['grade'].lower() or
            query in book['book_code'].lower()):
            results.append(book)
    
    return jsonify(results[:20])

@app.route('/api/schools/search')
def search_schools():
    schools_data = get_schools_data()
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    results = []
    for school in schools_data:
        if (query in school['Customer_Name'].lower() or 
            query in school['SM_Name'].lower()):
            results.append({
                'name': school['Customer_Name'],
                'sm_name': school['SM_Name'],
                'phone': school['Phone_Number']
            })
    
    return jsonify(results[:10])

@app.route('/api/generate-invoice', methods=['POST'])
def generate_invoice():
    data = request.json
    
    invoice_number = f"HO/IN/{datetime.now().strftime('%y%m%d%H%M')}"
    
    pdf_buffer = create_invoice_pdf(data, invoice_number)
    
    import base64
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    
    return jsonify({
        'success': True,
        'invoice_number': invoice_number,
        'pdf_data': pdf_base64
    })

@app.route('/<filename>')
def serve_logo(filename):
    if filename == 'WhatsApp_Image_2025-08-01_at_12.46.28_e1c96073-removebg-preview.png':
        return send_file(filename)
    return "File not found", 404

def create_invoice_pdf(data, invoice_number):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.3*inch, bottomMargin=0.3*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Logo
    try:
        logo = Image('WhatsApp_Image_2025-08-01_at_12.46.28_e1c96073-removebg-preview.png', width=1.5*inch, height=1.5*inch)
        logo.hAlign = 'LEFT'
        story.append(logo)
    except:
        pass
    
    # Header
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    header_text = f"<b>EDUWAVES PUBLISHERS LIMITED</b><br/>Global Positioning for the African Child<br/>INVOICE"
    story.append(Paragraph(header_text, header_style))
    story.append(Spacer(1, 20))
    
    # Invoice details
    invoice_data = [
        ['Invoice No:', invoice_number, 'Date:', datetime.now().strftime('%d/%m/%Y')],
        ['Customer:', data.get('customerName', ''), 'Sales Manager:', data.get('salesManager', '')],
        ['Phone:', data.get('phone', ''), 'Invoice Type:', data.get('invoiceType', '')]
    ]
    
    invoice_table = Table(invoice_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 20))
    
    # Books table
    books_data_table = [['S/N', 'Book Title', 'Grade', 'Subject', 'Qty', 'Unit Price', 'Total']]
    
    total_amount = 0
    for i, book in enumerate(data.get('books', []), 1):
        qty = int(book.get('quantity', 0))
        price = float(book.get('price', 0))
        total = qty * price
        total_amount += total
        
        books_data_table.append([
            str(i),
            book.get('title', ''),
            book.get('grade', ''),
            book.get('subject', ''),
            str(qty),
            f"N{price:,.2f}",
            f"N{total:,.2f}"
        ])
    
    books_table = Table(books_data_table, colWidths=[0.5*inch, 2.5*inch, 0.8*inch, 1.2*inch, 0.5*inch, 1*inch, 1*inch])
    books_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(books_table)
    story.append(Spacer(1, 20))
    
    # Totals
    discount_percent = float(data.get('discount', 0))
    discount_amount = (total_amount * discount_percent) / 100
    final_total = total_amount - discount_amount
    
    totals_data = [
        ['', '', '', '', 'Subtotal:', f"N{total_amount:,.2f}"],
        ['', '', '', '', f'Less {discount_percent}%:', f"N{discount_amount:,.2f}"],
        ['', '', '', '', 'TOTAL:', f"N{final_total:,.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[0.5*inch, 2.5*inch, 0.8*inch, 1.2*inch, 1.5*inch, 1*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (4, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (4, 0), (-1, -1), 10),
        ('FONTNAME', (4, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (4, -1), (-1, -1), 12),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 30))
    
    # Bank details
    bank_name = data.get('bank_name', 'ZENITH BANK')
    account_number = data.get('account_number', '1229600064')
    
    bank_style = ParagraphStyle(
        'BankDetails',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    bank_text = f"<b>BANK DETAILS:</b><br/>BANK NAME: {bank_name}<br/>ACCOUNT NAME: EDUWAVES PUBLISHERS LTD<br/>ACCOUNT NUMBER: {account_number}"
    story.append(Paragraph(bank_text, bank_style))
    story.append(Spacer(1, 20))
    
    # Terms and conditions
    terms_style = ParagraphStyle(
        'Terms',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=20,
        alignment=TA_LEFT,
        leftIndent=0,
        rightIndent=0
    )
    
    terms_text = "I/We have received the above books in good condition and promise to pay the bill within a month, failing which I/We will be liable to pay an interest of 20% per annum."
    story.append(Paragraph(terms_text, terms_style))
    story.append(Spacer(1, 30))
    
    # Signature
    signature_data = [
        ['', '', 'For: EDUWAVES PUBLISHERS LTD'],
        ['', '', ''],
        ['', '', ''],
        ['', '', 'Authorized Signature']
    ]
    
    signature_table = Table(signature_data, colWidths=[2*inch, 2*inch, 2*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica'),
        ('FONTSIZE', (2, 0), (2, -1), 10),
    ]))
    
    story.append(signature_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# This is required for Vercel
if __name__ == '__main__':
    app.run(debug=True)
