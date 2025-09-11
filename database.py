import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class InvoiceDatabase:
    def __init__(self, db_path: str = "invoices.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                invoice_type TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                customer_address TEXT,
                sales_manager TEXT NOT NULL,
                bank_name TEXT NOT NULL,
                account_number TEXT NOT NULL,
                total_quantity INTEGER NOT NULL,
                gross_total REAL NOT NULL,
                discount_percent REAL NOT NULL,
                discount_amount REAL NOT NULL,
                net_total REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create invoice_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                book_code TEXT NOT NULL,
                book_title TEXT NOT NULL,
                book_grade TEXT,
                book_subject TEXT,
                rate REAL NOT NULL,
                quantity INTEGER NOT NULL,
                gross_amount REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_type ON invoices(invoice_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_invoice ON invoice_items(invoice_id)')
        
        conn.commit()
        conn.close()
    
    def save_invoice(self, invoice_data: Dict) -> int:
        """Save invoice and its items to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert invoice
            cursor.execute('''
                INSERT INTO invoices (
                    invoice_number, invoice_type, customer_name, customer_phone,
                    customer_address, sales_manager, bank_name, account_number,
                    total_quantity, gross_total, discount_percent, discount_amount, net_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_data['invoice_number'],
                invoice_data['invoice_type'],
                invoice_data['customer_name'],
                invoice_data.get('customer_phone', ''),
                invoice_data.get('customer_address', ''),
                invoice_data['sales_manager'],
                invoice_data['bank_name'],
                invoice_data['account_number'],
                invoice_data['total_quantity'],
                invoice_data['gross_total'],
                invoice_data['discount_percent'],
                invoice_data['discount_amount'],
                invoice_data['net_total']
            ))
            
            invoice_id = cursor.lastrowid
            
            # Insert invoice items
            for item in invoice_data['items']:
                cursor.execute('''
                    INSERT INTO invoice_items (
                        invoice_id, book_code, book_title, book_grade, book_subject,
                        rate, quantity, gross_amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    invoice_id,
                    item['book_code'],
                    item['title'],
                    item.get('grade', ''),
                    item.get('subject', ''),
                    item['price'],
                    item['quantity'],
                    item['price'] * item['quantity']
                ))
            
            conn.commit()
            return invoice_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_invoices_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get invoices within date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM invoices 
            WHERE DATE(created_at) BETWEEN ? AND ?
            ORDER BY created_at DESC
        ''', (start_date, end_date))
        
        columns = [description[0] for description in cursor.description]
        invoices = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Get items for each invoice
        for invoice in invoices:
            cursor.execute('''
                SELECT * FROM invoice_items WHERE invoice_id = ?
                ORDER BY id
            ''', (invoice['id'],))
            
            item_columns = [description[0] for description in cursor.description]
            invoice['items'] = [dict(zip(item_columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return invoices
    
    def get_invoice_summary(self, start_date: str, end_date: str) -> Dict:
        """Get summary statistics for date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic counts and totals
        cursor.execute('''
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total_quantity) as total_quantity,
                SUM(gross_total) as total_gross,
                SUM(discount_amount) as total_discount,
                SUM(net_total) as total_net
            FROM invoices 
            WHERE DATE(created_at) BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        summary = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
        
        # Get breakdown by invoice type
        cursor.execute('''
            SELECT 
                invoice_type,
                COUNT(*) as count,
                SUM(net_total) as total_amount
            FROM invoices 
            WHERE DATE(created_at) BETWEEN ? AND ?
            GROUP BY invoice_type
        ''', (start_date, end_date))
        
        summary['by_type'] = [
            dict(zip(['invoice_type', 'count', 'total_amount'], row))
            for row in cursor.fetchall()
        ]
        
        # Get top customers
        cursor.execute('''
            SELECT 
                customer_name,
                COUNT(*) as invoice_count,
                SUM(net_total) as total_amount
            FROM invoices 
            WHERE DATE(created_at) BETWEEN ? AND ?
            GROUP BY customer_name
            ORDER BY total_amount DESC
            LIMIT 10
        ''', (start_date, end_date))
        
        summary['top_customers'] = [
            dict(zip(['customer_name', 'invoice_count', 'total_amount'], row))
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return summary
    
    def get_all_invoices(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all invoices with pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM invoices 
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [description[0] for description in cursor.description]
        invoices = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return invoices
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict]:
        """Get specific invoice by invoice number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            invoice = dict(zip(columns, row))
            
            # Get items
            cursor.execute('''
                SELECT * FROM invoice_items WHERE invoice_id = ?
                ORDER BY id
            ''', (invoice['id'],))
            
            item_columns = [description[0] for description in cursor.description]
            invoice['items'] = [dict(zip(item_columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return invoice
        
        conn.close()
        return None

# Initialize database instance
db = InvoiceDatabase()
