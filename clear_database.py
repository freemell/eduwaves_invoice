#!/usr/bin/env python3
"""
Script to clear all invoices from the database
"""
import sqlite3
import os

def clear_invoices():
    """Clear all invoices and invoice items from the database"""
    db_path = "invoices.db"
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Count current records
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoice_items")
        item_count = cursor.fetchone()[0]
        
        print(f"Found {invoice_count} invoices and {item_count} invoice items")
        
        if invoice_count > 0:
            # Clear invoice items first (due to foreign key constraints)
            cursor.execute("DELETE FROM invoice_items")
            print("Cleared invoice_items table")
            
            # Clear invoices
            cursor.execute("DELETE FROM invoices")
            print("Cleared invoices table")
            
            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='invoices'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='invoice_items'")
            print("Reset auto-increment counters")
            
            conn.commit()
            print("Database cleared successfully!")
        else:
            print("Database is already empty")
            
    except Exception as e:
        print(f"Error clearing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Clearing invoice database...")
    clear_invoices()
