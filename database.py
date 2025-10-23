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
        
        # Create schools table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_name TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                address TEXT,
                sales_manager TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_invoice_date TIMESTAMP
            )
        ''')
        
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
                is_discounted_version BOOLEAN DEFAULT FALSE,
                original_invoice_id INTEGER,
                school_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (original_invoice_id) REFERENCES invoices (id) ON DELETE SET NULL,
                FOREIGN KEY (school_id) REFERENCES schools (id) ON DELETE SET NULL
            )
        ''')
        
        # Check if new columns exist in invoices table, if not add them
        cursor.execute("PRAGMA table_info(invoices)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'school_id' not in columns:
            print("Adding school_id column to invoices table...")
            cursor.execute('ALTER TABLE invoices ADD COLUMN school_id INTEGER')
        
        if 'is_discounted_version' not in columns:
            print("Adding is_discounted_version column to invoices table...")
            cursor.execute('ALTER TABLE invoices ADD COLUMN is_discounted_version BOOLEAN DEFAULT FALSE')
        
        if 'original_invoice_id' not in columns:
            print("Adding original_invoice_id column to invoices table...")
            cursor.execute('ALTER TABLE invoices ADD COLUMN original_invoice_id INTEGER')
        
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schools_name ON schools(school_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_type ON invoices(invoice_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_school ON invoices(school_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_invoice ON invoice_items(invoice_id)')
        
        conn.commit()
        conn.close()
    
    def add_or_update_school(self, school_name: str, phone_number: str = '', address: str = '', sales_manager: str = '') -> int:
        """Add a new school or update existing school information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if school exists
            cursor.execute('SELECT id FROM schools WHERE school_name = ?', (school_name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing school
                cursor.execute('''
                    UPDATE schools 
                    SET phone_number = COALESCE(NULLIF(?, ''), phone_number),
                        address = COALESCE(NULLIF(?, ''), address),
                        sales_manager = COALESCE(NULLIF(?, ''), sales_manager),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE school_name = ?
                ''', (phone_number, address, sales_manager, school_name))
                school_id = existing[0]
            else:
                # Insert new school
                cursor.execute('''
                    INSERT INTO schools (school_name, phone_number, address, sales_manager)
                    VALUES (?, ?, ?, ?)
                ''', (school_name, phone_number, address, sales_manager))
                school_id = cursor.lastrowid
            
            conn.commit()
            return school_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_school_by_name(self, school_name: str) -> Optional[Dict]:
        """Get school information by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM schools WHERE school_name = ?', (school_name,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            school = dict(zip(columns, row))
            conn.close()
            return school
        
        conn.close()
        return None
    
    def get_school_invoice_history(self, school_name: str, limit: int = 50) -> List[Dict]:
        """Get invoice history for a specific school"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT i.*, 
                   COUNT(ii.id) as item_count
            FROM invoices i
            LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
            WHERE i.customer_name = ?
            GROUP BY i.id
            ORDER BY i.created_at DESC
            LIMIT ?
        ''', (school_name, limit))
        
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
    
    def import_schools_from_csv(self, csv_path: str) -> int:
        """Import schools from CSV file"""
        import csv
        import os
        
        print(f"Looking for CSV file: {csv_path}")
        print(f"File exists: {os.path.exists(csv_path)}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                print(f"CSV columns: {reader.fieldnames}")
                
                for i, row in enumerate(reader):
                    try:
                        # Handle different column names
                        school_name = (row.get('Customer_Name') or row.get('customer_name') or row.get('SMName', '')).strip()
                        phone_number = (row.get('Phone_Number') or row.get('phone_number', '')).strip()
                        address = (row.get('Address') or row.get('address', '')).strip()
                        sales_manager = (row.get('SM_Name') or row.get('sales_manager', '')).strip()
                        
                        if school_name:
                            # Check if exists
                            cursor.execute('SELECT id FROM schools WHERE school_name = ?', (school_name,))
                            if not cursor.fetchone():
                                cursor.execute('''
                                    INSERT INTO schools (school_name, phone_number, address, sales_manager)
                                    VALUES (?, ?, ?, ?)
                                ''', (school_name, phone_number, address, sales_manager))
                                imported_count += 1
                                
                                if imported_count <= 5:  # Log first 5 imports
                                    print(f"Imported: {school_name} - {sales_manager}")
                    except Exception as e:
                        print(f"Error importing school {school_name}: {e}")
                        continue
                        
                    if i >= 10:  # Limit for testing
                        print(f"Processed {i+1} rows, imported {imported_count}")
                        break
            
            conn.commit()
            print(f"Total imported: {imported_count} schools")
            return imported_count
            
        except Exception as e:
            conn.rollback()
            print(f"Import failed: {e}")
            raise e
        finally:
            conn.close()
    
    def save_invoice(self, invoice_data: Dict) -> int:
        """Save invoice and its items to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # First, handle school information (unless it's Floating Stock or Special Market)
            school_id = None
            customer_name = invoice_data['customer_name']
            invoice_type = invoice_data['invoice_type']
            
            # Only save as school if it's not Floating Stock or manually entered Special Market
            if customer_name and customer_name.lower() != 'floating stock':
                # Check if school exists
                cursor.execute('SELECT id FROM schools WHERE school_name = ?', (customer_name,))
                existing_school = cursor.fetchone()
                
                if existing_school:
                    school_id = existing_school[0]
                    # Update school information if provided
                    cursor.execute('''
                        UPDATE schools 
                        SET phone_number = COALESCE(NULLIF(?, ''), phone_number),
                            address = COALESCE(NULLIF(?, ''), address),
                            sales_manager = COALESCE(NULLIF(?, ''), sales_manager),
                            updated_at = CURRENT_TIMESTAMP,
                            last_invoice_date = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (
                        invoice_data.get('customer_phone', ''),
                        invoice_data.get('customer_address', ''),
                        invoice_data['sales_manager'],
                        school_id
                    ))
                else:
                    # Insert new school
                    cursor.execute('''
                        INSERT INTO schools (school_name, phone_number, address, sales_manager, last_invoice_date)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (
                        customer_name,
                        invoice_data.get('customer_phone', ''),
                        invoice_data.get('customer_address', ''),
                        invoice_data['sales_manager']
                    ))
                    school_id = cursor.lastrowid
                    print(f"✅ New school added to database: {customer_name} (ID: {school_id})")
            
            # Insert invoice
            cursor.execute('''
                INSERT INTO invoices (
                    invoice_number, invoice_type, customer_name, customer_phone,
                    customer_address, sales_manager, bank_name, account_number,
                    total_quantity, gross_total, discount_percent, discount_amount, net_total,
                    is_discounted_version, original_invoice_id, school_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                invoice_data['net_total'],
                invoice_data.get('is_discounted_version', False),
                invoice_data.get('original_invoice_id', None),
                school_id
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
    
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Dict]:
        """Get specific invoice by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            invoice = dict(zip(columns, row))
            conn.close()
            return invoice
        
        conn.close()
        return None
    
    def create_discounted_invoice(self, original_invoice_id: int, discount_percent: float = 20.0) -> int:
        """Create a discounted version of an existing invoice"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if a discounted version already exists
            cursor.execute('''
                SELECT id FROM invoices 
                WHERE original_invoice_id = ? AND is_discounted = 1
            ''', (original_invoice_id,))
            existing_discounted = cursor.fetchone()
            
            if existing_discounted:
                print(f"Discounted invoice already exists with ID: {existing_discounted[0]}")
                return existing_discounted[0]
            
            # Get original invoice
            cursor.execute('SELECT * FROM invoices WHERE id = ?', (original_invoice_id,))
            original_row = cursor.fetchone()
            
            if not original_row:
                raise ValueError(f"Invoice with ID {original_invoice_id} not found")
            
            columns = [description[0] for description in cursor.description]
            original_invoice = dict(zip(columns, original_row))
            
            # Get original invoice items
            cursor.execute('''
                SELECT * FROM invoice_items WHERE invoice_id = ?
                ORDER BY id
            ''', (original_invoice_id,))
            
            item_columns = [description[0] for description in cursor.description]
            original_items = [dict(zip(item_columns, row)) for row in cursor.fetchall()]
            
            # Calculate new totals - same gross total, fixed 20% discount
            gross_total = original_invoice['gross_total']
            discount_amount = gross_total * (discount_percent / 100)
            net_total = gross_total - discount_amount
            
            # Generate new invoice number with a unique suffix
            from datetime import datetime
            import time
            timestamp = int(time.time() * 1000)  # Use milliseconds for uniqueness
            new_invoice_number = f"HO/IN/{datetime.now().strftime('%y%m%d%H%M')}{timestamp % 10000:04d}"
            
            # Insert new discounted invoice
            cursor.execute('''
                INSERT INTO invoices (
                    invoice_number, invoice_type, customer_name, customer_phone,
                    customer_address, sales_manager, bank_name, account_number,
                    total_quantity, gross_total, discount_percent, discount_amount, net_total,
                    original_invoice_id, is_discounted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                new_invoice_number,
                original_invoice['invoice_type'],
                original_invoice['customer_name'],
                original_invoice.get('customer_phone', ''),
                original_invoice.get('customer_address', ''),
                original_invoice['sales_manager'],
                original_invoice['bank_name'],
                original_invoice['account_number'],
                original_invoice['total_quantity'],
                gross_total, # Same gross total as original
                discount_percent, # Fixed 20% discount
                discount_amount,
                net_total,
                original_invoice_id,
                1 # Mark as discounted
            ))
            discounted_invoice_id = cursor.lastrowid
            
            # Insert items for the discounted invoice (exact same items)
            for item in original_items:
                cursor.execute('''
                    INSERT INTO invoice_items (
                        invoice_id, book_code, book_title, book_grade, book_subject, rate, quantity, gross_amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    discounted_invoice_id,
                    item['book_code'],
                    item['book_title'],
                    item.get('book_grade', ''),
                    item.get('book_subject', ''),
                    item['rate'],
                    item['quantity'],
                    item['gross_amount']
                ))
            
            conn.commit()
            return discounted_invoice_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

# Initialize database instance
db = InvoiceDatabase()

# Import schools from CSV if they haven't been imported yet
def initialize_schools_from_csv():
    """Import schools from unique_schools.csv if database is empty"""
    try:
        conn = sqlite3.connect('invoices.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM schools')
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            print("Importing schools from CSV...")
            imported = db.import_schools_from_csv('unique_schools.csv')
            print(f"Imported {imported} schools from CSV")
        else:
            print(f"Database already contains {count} schools")
    except Exception as e:
        print(f"Could not import schools from CSV: {e}")

# Run initialization
try:
    initialize_schools_from_csv()
    print("Database initialization completed successfully")
except Exception as e:
    print(f"Database initialization failed: {e}")
