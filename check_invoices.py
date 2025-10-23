import sqlite3

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM invoices')
count = cursor.fetchone()[0]
print(f'Total invoices: {count}')

if count > 0:
    cursor.execute('SELECT invoice_number, customer_name, created_at FROM invoices ORDER BY created_at DESC LIMIT 3')
    print('\nRecent invoices:')
    for row in cursor.fetchall():
        print(f'  {row[0]} - {row[1]} - {row[2]}')

conn.close()