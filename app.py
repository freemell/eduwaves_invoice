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
from database import db

app = Flask(__name__)

# Debug: Print all routes when app starts
def print_routes():
    print("🔍 Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")

# Simple test route to verify app is working
@app.route('/ping')
def ping():
    return jsonify({"status": "ok", "message": "EDUwaves Invoice Generator is running!", "routes": [str(rule) for rule in app.url_map.iter_rules()]})

# Vercel compatibility
def handler(request):
    return app(request.environ, lambda *args: None)

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

@app.route('/api/test')
def test_api():
    """Test API endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/database/status')
def database_status():
    """Check database status"""
    try:
        import sqlite3
        conn = sqlite3.connect('invoices.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Count records
        invoice_count = 0
        school_count = 0
        if 'invoices' in tables:
            cursor.execute("SELECT COUNT(*) FROM invoices")
            invoice_count = cursor.fetchone()[0]
        
        if 'schools' in tables:
            cursor.execute("SELECT COUNT(*) FROM schools")
            school_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'database_exists': True,
            'tables': tables,
            'invoice_count': invoice_count,
            'school_count': school_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'database_exists': False
        })

@app.route('/api/schools/history/<school_name>')
def get_school_history(school_name):
    """Get invoice history for a specific school"""
    try:
        history = db.get_school_invoice_history(school_name)
        
        # Format the response
        formatted_history = []
        for invoice in history:
            formatted_history.append({
                'invoice_number': invoice['invoice_number'],
                'invoice_type': invoice['invoice_type'],
                'date': invoice['created_at'],
                'sales_manager': invoice['sales_manager'],
                'total_quantity': invoice['total_quantity'],
                'gross_total': invoice['gross_total'],
                'discount_percent': invoice['discount_percent'],
                'net_total': invoice['net_total'],
                'item_count': invoice['item_count'],
                'items': invoice['items']
            })
        
        return jsonify({
            'success': True,
            'school_name': school_name,
            'invoice_count': len(formatted_history),
            'invoices': formatted_history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/invoices/<invoice_number>')
def get_invoice_details(invoice_number):
    """Get full details of a specific invoice by invoice number"""
    print(f"🔍 Searching for invoice: {invoice_number}")
    try:
        invoice = db.get_invoice_by_number(invoice_number)
        print(f"📄 Invoice found: {invoice is not None}")
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Format items
        formatted_items = []
        for item in invoice.get('items', []):
            formatted_items.append({
                'book_code': item['book_code'],
                'title': item['book_title'],
                'grade': item.get('book_grade', ''),
                'subject': item.get('book_subject', ''),
                'price': float(item['rate']),
                'quantity': int(item['quantity']),
                'gross_amount': float(item['gross_amount'])
            })
        
        return jsonify({
            'success': True,
            'invoice': {
                'invoice_number': invoice['invoice_number'],
                'invoice_type': invoice['invoice_type'],
                'customer_name': invoice['customer_name'],
                'customer_phone': invoice.get('customer_phone', ''),
                'customer_address': invoice.get('customer_address', ''),
                'sales_manager': invoice['sales_manager'],
                'bank_name': invoice['bank_name'],
                'account_number': invoice['account_number'],
                'date': invoice['created_at'],
                'total_quantity': invoice['total_quantity'],
                'gross_total': invoice['gross_total'],
                'discount_percent': invoice['discount_percent'],
                'discount_amount': invoice['discount_amount'],
                'net_total': invoice['net_total'],
                'items': formatted_items
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/invoices/reprint/<invoice_number>', methods=['POST'])
def reprint_invoice(invoice_number):
    """Reprint an existing invoice"""
    try:
        invoice = db.get_invoice_by_number(invoice_number)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Format items for PDF generation
        formatted_items = []
        for item in invoice.get('items', []):
            formatted_items.append({
                'book_code': item['book_code'],
                'title': item['book_title'],
                'grade': item.get('book_grade', ''),
                'subject': item.get('book_subject', ''),
                'price': float(item['rate']),
                'quantity': int(item['quantity'])
            })
        
        # Prepare invoice data for PDF
        invoice_data = {
            'customer_name': invoice['customer_name'],
            'customer_phone': invoice.get('customer_phone', ''),
            'customer_address': invoice.get('customer_address', ''),
            'sales_manager': invoice['sales_manager'],
            'bank_name': invoice['bank_name'],
            'account_number': invoice['account_number'],
            'discount_percent': invoice['discount_percent'],
            'invoice_type': invoice['invoice_type'],
            'items': formatted_items
        }
        
        # Generate PDF
        pdf_buffer = create_invoice_pdf(invoice_data, invoice['invoice_number'])
        
        # Return as base64
        import base64
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'invoice_number': invoice['invoice_number'],
            'pdf_data': pdf_base64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports')
def reports_page():
    """Reports page"""
    return render_template('reports.html')

@app.route('/api/reports/summary', methods=['POST'])
def get_report_summary():
    """Get report summary for date range"""
    data = request.json
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start date and end date are required'}), 400
    
    try:
        summary = db.get_invoice_summary(start_date, end_date)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/invoices', methods=['POST'])
def get_report_invoices():
    """Get invoices for date range"""
    data = request.json
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start date and end date are required'}), 400
    
    try:
        invoices = db.get_invoices_by_date_range(start_date, end_date)
        return jsonify(invoices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/generate-pdf', methods=['POST'])
def generate_report_pdf():
    """Generate PDF report for date range"""
    data = request.json
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start date and end date are required'}), 400
    
    try:
        # Get data
        summary = db.get_invoice_summary(start_date, end_date)
        invoices = db.get_invoices_by_date_range(start_date, end_date)
        
        # Create PDF
        pdf_buffer = create_report_pdf(summary, invoices, start_date, end_date)
        
        # Return as base64
        import base64
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'pdf_data': pdf_base64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-invoice', methods=['POST'])
def generate_invoice():
    data = request.json
    
    # Generate invoice number
    invoice_number = f"HO/IN/{datetime.now().strftime('%y%m%d%H%M')}"
    
    # Calculate totals
    total_quantity = sum(item['quantity'] for item in data['items'])
    gross_total = sum(item['quantity'] * item['price'] for item in data['items'])
    discount_amount = gross_total * (data['discount_percent'] / 100)
    net_total = gross_total - discount_amount
    
    # Prepare invoice data for database
    invoice_data = {
        'invoice_number': invoice_number,
        'invoice_type': data['invoice_type'],
        'customer_name': data['customer_name'],
        'customer_phone': data.get('customer_phone', ''),
        'customer_address': data.get('customer_address', ''),
        'sales_manager': data['sales_manager'],
        'bank_name': data['bank_name'],
        'account_number': data['account_number'],
        'total_quantity': total_quantity,
        'gross_total': gross_total,
        'discount_percent': data['discount_percent'],
        'discount_amount': discount_amount,
        'net_total': net_total,
        'items': data['items']
    }
    
    try:
        # Save to database
        invoice_id = db.save_invoice(invoice_data)
        print(f"✅ Invoice saved to database with ID: {invoice_id}")
        
        # Automatically create a 20% discounted version
        try:
            discounted_invoice_id = db.create_discounted_invoice(invoice_id, 20.0)
            print(f"✅ Discounted invoice created with ID: {discounted_invoice_id}")
        except Exception as e:
            print(f"❌ Error creating discounted invoice: {e}")
            # Continue even if discounted version fails
            
    except Exception as e:
        print(f"❌ Error saving invoice to database: {e}")
        # Continue with PDF generation even if database save fails
    
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

@app.route('/api/generate-discounted-invoice', methods=['POST'])
def generate_discounted_invoice():
    """Generate a 20% discounted version of an existing invoice"""
    data = request.json
    original_invoice_number = data.get('invoice_number')
    
    if not original_invoice_number:
        return jsonify({'error': 'Original invoice number is required'}), 400
    
    try:
        # Get original invoice from database
        original_invoice = db.get_invoice_by_number(original_invoice_number)
        if not original_invoice:
            return jsonify({'error': 'Original invoice not found'}), 404
        
        # Create discounted version
        discounted_invoice_id = db.create_discounted_invoice(original_invoice['id'], 20.0)
        
        # Get the discounted invoice data
        discounted_invoice_data = db.get_invoice_by_id(discounted_invoice_id)
        
        if not discounted_invoice_data:
            return jsonify({'error': 'Failed to retrieve discounted invoice data'}), 500
        
        # Get items for the discounted invoice
        conn = sqlite3.connect('invoices.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = ?', (discounted_invoice_id,))
        item_columns = [description[0] for description in cursor.description]
        items = [dict(zip(item_columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        # Format items for PDF generation
        formatted_items = []
        for item in items:
            formatted_items.append({
                'book_code': item['book_code'],
                'title': item['book_title'],
                'grade': item.get('book_grade', ''),
                'subject': item.get('book_subject', ''),
                'price': float(item['rate']),
                'quantity': int(item['quantity'])
            })
        
        # Add items to invoice data
        discounted_invoice_data['items'] = formatted_items
        
        # Generate PDF for the discounted invoice
        pdf_data = generate_invoice_pdf(discounted_invoice_data)
        
        # Return as base64
        import base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'invoice_number': discounted_invoice_data['invoice_number'],
            'pdf_data': pdf_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/<filename>')
def serve_logo(filename):
    if filename == 'WhatsApp_Image_2025-08-01_at_12.46.28_e1c96073-removebg-preview.png':
        return send_file(filename)
    return "File not found", 404

@app.route('/images/<filename>')
def serve_images(filename):
    image_path = os.path.join('images', filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    return "Image not found", 404

# Catch-all route for debugging
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Route not found",
        "message": "The requested URL was not found on the server",
        "available_routes": [str(rule) for rule in app.url_map.iter_rules()],
        "requested_path": request.path
    }), 404

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
        story.append(Spacer(1, 5))
    
    # Company Slogan
    slogan_style = ParagraphStyle(
        'Slogan',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceAfter=10
    )
    story.append(Paragraph("...global positioning for the african child", slogan_style))
    
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
    items_data = [["S.No.", "TITLE", "RATE", "QTY.", "GROSS AMT.", "NET AMOUNT"]]
    
    total_gross = 0
    total_quantity = 0
    
    for i, item in enumerate(data.get('items', []), 1):
        gross_amount = item['quantity'] * item['price']
        total_gross += gross_amount
        total_quantity += item['quantity']
        items_data.append([
            str(i),
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
            "", "", "", "", f"N{total_gross:,.2f}", f"N{total_gross:,.2f}"
        ])
        # Add discount line
        items_data.append([
            "", f"LESS DISCOUNT {discount_percent}%", "", "", f"N{discount_amount:,.2f}", f"N{net_total:,.2f}"
        ])
    
    # Add final total row
    items_data.append([
        "", "Total:", "", str(total_quantity), f"N{total_gross:,.2f}", f"N{net_total:,.2f}"
    ])
    
    items_table = Table(items_data, colWidths=[0.5*inch, 3.8*inch, 0.8*inch, 0.5*inch, 1*inch, 1*inch])
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
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Title column left-aligned
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
    
    # Contact Information Footer - Beautiful Design
    contact_footer_style = ParagraphStyle(
        'ContactFooter',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=5
    )
    
    # Create a horizontal line separator
    story.append(Spacer(1, 10))
    line = Table([['']], colWidths=[7*inch])
    line.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (0, 0), 1, colors.grey),
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.grey),
    ]))
    story.append(line)
    story.append(Spacer(1, 10))
    
    # Contact information in a neat table layout
    contact_data = []
    contact_row = []
    
    # WhatsApp
    whatsapp_path = "images/whatsapp.png"
    if os.path.exists(whatsapp_path):
        whatsapp_icon = Image(whatsapp_path, width=0.2*inch, height=0.2*inch)
        contact_row.append([whatsapp_icon, Paragraph("09025977776", contact_footer_style)])
    else:
        contact_row.append([Paragraph("📱", contact_footer_style), Paragraph("09025977776", contact_footer_style)])
    
    # Phone
    contact_row.append([Paragraph("📞", contact_footer_style), Paragraph("+234 803 086 7910<br/>07066483007", contact_footer_style)])
    
    # Website
    web_path = "images/web.png"
    if os.path.exists(web_path):
        web_icon = Image(web_path, width=0.2*inch, height=0.2*inch)
        contact_row.append([web_icon, Paragraph("www.eduwavespublishers.com", contact_footer_style)])
    else:
        contact_row.append([Paragraph("🌐", contact_footer_style), Paragraph("www.eduwavespublishers.com", contact_footer_style)])
    
    # Email
    gmail_path = "images/gmail-logo.png"
    if os.path.exists(gmail_path):
        gmail_icon = Image(gmail_path, width=0.2*inch, height=0.2*inch)
        contact_row.append([gmail_icon, Paragraph("eduwavespl@gmail.com", contact_footer_style)])
    else:
        contact_row.append([Paragraph("✉️", contact_footer_style), Paragraph("eduwavespl@gmail.com", contact_footer_style)])
    
    contact_data.append(contact_row)
    
    # Create contact table
    contact_table = Table(contact_data, colWidths=[1.75*inch, 1.75*inch, 1.75*inch, 1.75*inch])
    contact_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    
    story.append(contact_table)
    story.append(Spacer(1, 15))
    
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

def create_report_pdf(summary, invoices, start_date, end_date):
    """Create PDF report for invoice summary"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName='Helvetica',
        spaceAfter=5
    )
    
    story = []
    
    # Title
    title = Paragraph("EDUwaves Publishers - Invoice Report", title_style)
    story.append(title)
    
    # Date range
    date_range = Paragraph(f"Report Period: {start_date} to {end_date}", normal_style)
    story.append(date_range)
    story.append(Spacer(1, 20))
    
    # Summary section
    story.append(Paragraph("Summary", heading_style))
    
    summary_data = [
        ["Total Invoices", str(summary.get('total_invoices', 0))],
        ["Total Quantity", str(summary.get('total_quantity', 0))],
        ["Gross Total (N)", f"N{summary.get('total_gross', 0):,.2f}"],
        ["Total Discount (N)", f"N{summary.get('total_discount', 0):,.2f}"],
        ["Net Total (N)", f"N{summary.get('total_net', 0):,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Breakdown by type
    if summary.get('by_type'):
        story.append(Paragraph("Breakdown by Invoice Type", heading_style))
        
        type_data = [["Invoice Type", "Count", "Total Amount (N)"]]
        for item in summary['by_type']:
            type_data.append([
                item['invoice_type'].title(),
                str(item['count']),
                f"N{item['total_amount']:,.2f}"
            ])
        
        type_table = Table(type_data, colWidths=[2*inch, 1*inch, 2*inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(type_table)
        story.append(Spacer(1, 20))
    
    # Top customers
    if summary.get('top_customers'):
        story.append(Paragraph("Top Customers", heading_style))
        
        customer_data = [["Customer Name", "Invoice Count", "Total Amount (N)"]]
        for item in summary['top_customers']:
            customer_data.append([
                item['customer_name'],
                str(item['invoice_count']),
                f"N{item['total_amount']:,.2f}"
            ])
        
        customer_table = Table(customer_data, colWidths=[3*inch, 1*inch, 2*inch])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(customer_table)
        story.append(Spacer(1, 20))
    
    # Detailed invoices
    if invoices:
        story.append(Paragraph("Detailed Invoices", heading_style))
        
        # Create detailed table
        invoice_data = [["Invoice #", "Date", "Customer", "Type", "Net Amount (N)"]]
        for invoice in invoices:
            invoice_data.append([
                invoice['invoice_number'],
                invoice['created_at'][:10],  # Just the date part
                invoice['customer_name'][:30],  # Truncate long names
                invoice['invoice_type'].title(),
                f"N{invoice['net_total']:,.2f}"
            ])
        
        invoice_table = Table(invoice_data, colWidths=[1.5*inch, 1*inch, 2*inch, 1*inch, 1.5*inch])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(invoice_table)
    
    # Footer
    story.append(Spacer(1, 20))
    footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    footer = Paragraph(footer_text, normal_style)
    story.append(footer)
    
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

# Railway deployment configuration - Only run Flask dev server locally
if __name__ == '__main__':
    # Only run Flask dev server for local development
    # In production, Railway will use gunicorn with wsgi.py
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting EDUwaves Invoice Generator (LOCAL DEV) on port {port}")
    print(f"📋 Available routes: /, /health, /api/books/search, /api/schools/search, /api/generate-invoice, /api/generate-discounted-invoice")
    
    # Print all registered routes
    print_routes()
    
    print(f"🌐 Local dev server starting on http://0.0.0.0:{port}")
    print("⚠️  WARNING: This is a development server. Use WSGI for production!")
    app.run(host='0.0.0.0', port=port, debug=True)
