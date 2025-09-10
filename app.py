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

# Vercel compatibility
def handler(request):
    return app(request.environ, lambda *args: None)

# Railway deployment configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting EDUwaves Invoice Generator on port {port}")
    print(f"📋 Available routes: /, /health, /api/books/search, /api/schools/search, /api/generate-invoice")
    
    # Check if template file exists
    template_path = os.path.join('templates', 'index.html')
    if os.path.exists(template_path):
        print(f"✅ Template file found: {template_path}")
    else:
        print(f"❌ Template file not found: {template_path}")
    
    # List current directory contents
    print("📁 Current directory contents:")
    try:
        for item in os.listdir('.'):
            print(f"  - {item}")
    except Exception as e:
        print(f"❌ Error listing directory: {e}")
    
    # Check if data files exist
    data_files = ['books_database.json', 'unique_schools.csv']
    for file in data_files:
        if os.path.exists(file):
            print(f"✅ Data file found: {file}")
        else:
            print(f"❌ Data file missing: {file}")
    
    print(f"🌐 Server starting on http://0.0.0.0:{port}")
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        # Try alternative port
        alt_port = 8080
        print(f"🔄 Trying alternative port: {alt_port}")
        app.run(host='0.0.0.0', port=alt_port, debug=False)

# Load data
def load_books():
    try:
        with open('books_database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback for Vercel deployment
        return []

def load_schools():
    try:
        df = pd.read_csv('unique_schools.csv')
        return df.to_dict('records')
    except FileNotFoundError:
        # Fallback for Vercel deployment
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
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback if template fails to load
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EDUwaves Invoice Generator</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h2 class="mb-0">📚 EDUwaves Invoice Generator</h2>
                                <p class="mb-0">Global Positioning for the African Child</p>
                            </div>
                            <div class="card-body">
                                <div class="alert alert-info">
                                    <h4>🎉 Application is Running!</h4>
                                    <p>Your EDUwaves Invoice Generator is successfully deployed on Railway!</p>
                                    <p><strong>Template Error:</strong> {str(e)}</p>
                                </div>
                                
                                <h5>Available Features:</h5>
                                <ul>
                                    <li>✅ <strong>93 Books</strong> - Complete catalog search</li>
                                    <li>✅ <strong>2,032 Schools</strong> - Database with autocomplete</li>
                                    <li>✅ <strong>PDF Generation</strong> - Professional invoices</li>
                                    <li>✅ <strong>Bank Selection</strong> - Zenith/Globus options</li>
                                    <li>✅ <strong>Invoice Types</strong> - Floating/Credit/Special Market</li>
                                </ul>
                                
                                <h5>Test Endpoints:</h5>
                                <div class="d-grid gap-2">
                                    <a href="/health" class="btn btn-outline-primary">Health Check</a>
                                    <a href="/test" class="btn btn-outline-secondary">Simple Test</a>
                                    <a href="/api/books/search?q=math" class="btn btn-outline-success">Test Book Search</a>
                                    <a href="/api/schools/search?q=federal" class="btn btn-outline-info">Test School Search</a>
                                </div>
                                
                                <div class="mt-4">
                                    <h6>Next Steps:</h6>
                                    <p>The application is working, but there's a template loading issue. The main interface should be accessible once the template issue is resolved.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "EDUwaves Invoice Generator is running!"})

@app.route('/test')
def test():
    return "<h1>EDUwaves Invoice Generator</h1><p>App is working! <a href='/'>Go to main page</a></p>"

@app.route('/api/books/search')
def search_books():
    books_data = get_books_data()
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify(books_data[:20])  # Return first 20 books
    
    # Fuzzy search
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
    
    # Generate invoice number
    invoice_number = f"HO/IN/{datetime.now().strftime('%y%m%d%H%M')}"
    
    # Create PDF
    pdf_buffer = create_invoice_pdf(data, invoice_number)
    
    # For Vercel, return the PDF directly as base64
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
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles to match the original design
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    
    company_style = ParagraphStyle(
        'CompanyInfo',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Story (content)
    story = []
    
    # Logo and Company Header
    logo_path = "WhatsApp_Image_2025-08-01_at_12.46.28_e1c96073-removebg-preview.png"
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*inch, height=0.8*inch)
        story.append(logo)
        story.append(Spacer(1, 10))
    
    # Invoice Title
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 15))
    
    # Company Information Table
    company_data = [
        ["EDUWAVES PUBLISHERS LTD", "", f"Date: {datetime.now().strftime('%d-%b-%Y')}"],
        ["14 Onitsha Crescent, Area 11", "", f"Invoice No.: {invoice_number}"],
        ["Garki, Abuja-FCT, Nigeria", "", f"Order No.: HO/OR/{datetime.now().strftime('%y%m%d')}"]
    ]
    
    company_table = Table(company_data, colWidths=[3.5*inch, 0.5*inch, 2.5*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(company_table)
    story.append(Spacer(1, 15))
    
    # Sales Manager (top right)
    sm_name = data.get('sales_manager', 'DANIEL MMEYENE')
    sm_para = Paragraph(f"<para align='right'><b>{sm_name}</b></para>", normal_style)
    story.append(sm_para)
    story.append(Spacer(1, 10))
    
    # Customer Information
    customer_name = data.get('customer_name', '')
    customer_address = data.get('customer_address', '')
    customer_phone = data.get('customer_phone', '')
    
    customer_data = [
        ["To:", f"{customer_name}"],
        ["", f"{customer_address}"],
        ["", f"{customer_phone}"]
    ]
    
    customer_table = Table(customer_data, colWidths=[0.8*inch, 5.5*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(customer_table)
    story.append(Spacer(1, 20))
    
    # Items Table
    items_data = [["S.No.", "BOOK CODE", "TITLE", "RATE", "QTY.", "GROSS AMT.", "NET AMOUNT"]]
    
    total_gross = 0
    total_quantity = 0
    
    for i, item in enumerate(data.get('items', []), 1):
        gross_amount = item['quantity'] * item['price']
        total_gross += gross_amount
        total_quantity += item['quantity']
        items_data.append([
            str(i),
            item['book_code'],
            item['title'],
            f"N{item['price']:,.2f}",
            str(item['quantity']),
            f"N{gross_amount:,.2f}",
            f"N{gross_amount:,.2f}"
        ])
    
    # Add discount row if applicable
    discount_percent = data.get('discount_percent', 0)
    discount_amount = total_gross * (discount_percent / 100)
    net_total = total_gross - discount_amount
    
    if discount_percent > 0:
        # Add total before discount
        items_data.append([
            "", "", "", "", "", f"N{total_gross:,.2f}", f"N{total_gross:,.2f}"
        ])
        # Add discount line
        items_data.append([
            "", "", f"LESS DISCOUNT {discount_percent}%", "", "", f"N{discount_amount:,.2f}", f"N{net_total:,.2f}"
        ])
    
    # Add final total row
    items_data.append([
        "", "", "Total:", "", str(total_quantity), f"N{total_gross:,.2f}", f"N{net_total:,.2f}"
    ])
    
    items_table = Table(items_data, colWidths=[0.5*inch, 1*inch, 2.8*inch, 0.8*inch, 0.5*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Data rows
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Title column left-aligned
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        
        # Total row styling
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 20))
    
    # Net Amount Payable
    net_amount_text = f"NET Amount Payable (Naira): N{net_total:,.2f}"
    net_para = Paragraph(f"<para><b>{net_amount_text}</b></para>", normal_style)
    story.append(net_para)
    story.append(Spacer(1, 10))
    
    # Amount in words
    amount_words = number_to_words(int(net_total))
    words_para = Paragraph(f"Naira: {amount_words}", normal_style)
    story.append(words_para)
    story.append(Spacer(1, 20))
    
    # Bank Details
    bank_text = "Please make your payment into any of the designated account details below."
    bank_para = Paragraph(bank_text, normal_style)
    story.append(bank_para)
    story.append(Spacer(1, 10))
    
    # Get bank details from form data
    bank_name = data.get('bank_name', 'ZENITH BANK')
    account_number = data.get('account_number', '1229600064')
    
    bank_data = [
        ["ACCOUNT NAME:", "EDUWAVES PUBLISHERS LTD"],
        ["BANK NAME:", bank_name],
        ["ACCOUNT NUMBER:", account_number]
    ]
    
    bank_table = Table(bank_data, colWidths=[1.5*inch, 3*inch])
    bank_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(bank_table)
    story.append(Spacer(1, 20))
    
    # Terms and Conditions
    terms_text = "I/We have received the above books in good condition and promise to pay the bill within a month, failing which I/We will be liable to pay an interest of 20% per annum."
    terms_style = ParagraphStyle(
        'TermsStyle',
        parent=normal_style,
        fontSize=10,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName='Helvetica',
        spaceAfter=10,
        leftIndent=0,
        rightIndent=0
    )
    terms_para = Paragraph(terms_text, terms_style)
    story.append(terms_para)
    story.append(Spacer(1, 10))
    
    # Customer Signature
    signature_text = "Customer's Signature."
    signature_para = Paragraph(signature_text, normal_style)
    story.append(signature_para)
    story.append(Spacer(1, 10))
    
    # Note
    note_text = "Note: The delivery should be taken after checking the Books, we shall not be responsible for any shortage."
    note_para = Paragraph(note_text, normal_style)
    story.append(note_para)
    story.append(Spacer(1, 20))
    
    # Footer
    footer_data = [
        ["Prepared By", "", "Checked By", "", f"Page No.: Page 1 of 1"]
    ]
    
    footer_table = Table(footer_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch, 1.5*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(footer_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def number_to_words(num):
    """Convert number to words (simplified version)"""
    ones = ["", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]
    tens = ["", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]
    teens = ["TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN"]
    
    if num == 0:
        return "ZERO"
    
    def convert_hundreds(n):
        result = ""
        if n >= 100:
            result += ones[n // 100] + " HUNDRED "
            n %= 100
        if n >= 20:
            result += tens[n // 10] + " "
            n %= 10
        elif n >= 10:
            result += teens[n - 10] + " "
            return result
        if n > 0:
            result += ones[n] + " "
        return result
    
    result = ""
    if num >= 1000000:
        result += convert_hundreds(num // 1000000) + "MILLION "
        num %= 1000000
    if num >= 1000:
        result += convert_hundreds(num // 1000) + "THOUSAND "
        num %= 1000
    if num > 0:
        result += convert_hundreds(num)
    
    return result.strip() + " NAIRA ONLY"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
