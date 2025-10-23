#!/usr/bin/env python3
"""
Script to check database status
"""
import sqlite3
import os
from datetime import datetime

def check_database():
    """Check database status and show current data"""
    db_path = "invoices.db"
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check schools
        cursor.execute("SELECT COUNT(*) FROM schools")
        school_count = cursor.fetchone()[0]
        print(f"Schools in database: {school_count}")
        
        # Check invoices
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        print(f"Invoices in database: {invoice_count}")
        
        # Check invoice items
        cursor.execute("SELECT COUNT(*) FROM invoice_items")
        item_count = cursor.fetchone()[0]
        print(f"Invoice items in database: {item_count}")
        
        if invoice_count > 0:
            print("\nRecent invoices:")
            cursor.execute("""
                SELECT invoice_number, customer_name, created_at, net_total 
                FROM invoices 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            for row in cursor.fetchall():
                invoice_num, customer, created_at, net_total = row
                print(f"  {invoice_num} - {customer} - {created_at} - N{net_total:,.2f}")
        
        if school_count > 0:
            print(f"\nSample schools:")
            cursor.execute("SELECT school_name, sales_manager FROM schools LIMIT 3")
            for row in cursor.fetchall():
                school_name, sales_manager = row
                print(f"  {school_name} - {sales_manager}")
                
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Database Status Check")
    print("=" * 50)
    check_database()
