# Invoice & School History System - User Guide

## Overview
The invoice generator now includes a comprehensive storage and history system that automatically saves all invoice data and school information to a local database.

## Features

### 1. Automatic School Management
- **Auto-Save Schools**: When you generate an invoice for a school, the system automatically:
  - Checks if the school exists in the database
  - If new: Saves the school with all provided information (name, phone, address, sales manager)
  - If existing: Updates the school information with any new data provided
  - Excludes "Floating Stock" from being saved as a school

- **School Database**: 
  - All schools from `unique_schools.csv` are imported on first run
  - New schools are added when invoices are created
  - School information is kept up-to-date automatically

### 2. Complete Invoice History
Every invoice generated is automatically saved with:
- Invoice number, date, and type
- Customer/school information
- Sales manager details
- Bank details used
- All items (books, quantities, prices)
- Discount information
- Total amounts
- Link to school (if applicable)

### 3. API Endpoints for History Access

#### Get School Invoice History
```
GET /api/schools/history/<school_name>
```
Returns all invoices for a specific school, including:
- Invoice numbers and dates
- Sales managers
- Item counts and totals
- All items in each invoice

**Example Response:**
```json
{
  "success": true,
  "school_name": "Federal Government College",
  "invoice_count": 5,
  "invoices": [
    {
      "invoice_number": "HO/IN/2510081430",
      "invoice_type": "Credit School",
      "date": "2025-10-08 14:30:45",
      "sales_manager": "DANIEL MMEYENE",
      "total_quantity": 50,
      "gross_total": 125000.00,
      "discount_percent": 10.0,
      "net_total": 112500.00,
      "item_count": 5,
      "items": [...]
    }
  ]
}
```

#### Get Specific Invoice Details
```
GET /api/invoices/<invoice_number>
```
Returns complete details of a specific invoice by its invoice number.

#### Reprint Existing Invoice
```
POST /api/invoices/reprint/<invoice_number>
```
Regenerates the PDF for an existing invoice. Returns the PDF as base64 data.

**Example Usage:**
```javascript
fetch('/api/invoices/reprint/HO/IN/2510081430', {
    method: 'POST'
})
.then(response => response.json())
.then(data => {
    // data.pdf_data contains the base64 PDF
    // Download or display the PDF
});
```

### 4. Database Structure

#### Schools Table
- `id`: Unique identifier
- `school_name`: School name (unique)
- `phone_number`: Contact phone
- `address`: School address
- `sales_manager`: Assigned sales manager
- `created_at`: When first added
- `updated_at`: Last update time
- `last_invoice_date`: Date of most recent invoice

#### Invoices Table
- `id`: Unique identifier
- `invoice_number`: Invoice number (unique)
- `invoice_type`: Type (Floating Stock, Credit School, Special Market)
- `customer_name`: Customer/school name
- `customer_phone`, `customer_address`: Contact details
- `sales_manager`: Sales manager name
- `bank_name`, `account_number`: Payment details
- `total_quantity`: Total items
- `gross_total`, `discount_percent`, `discount_amount`, `net_total`: Financial details
- `school_id`: Link to schools table (if applicable)
- `created_at`: Invoice generation date

#### Invoice Items Table
- `invoice_id`: Link to parent invoice
- `book_code`, `book_title`, `book_grade`, `book_subject`: Book details
- `rate`: Unit price
- `quantity`: Number of books
- `gross_amount`: Total for this item

## How It Works

### When Creating a New Invoice:

1. **Fill in school/customer details** on the form
2. **Click "Generate Invoice"**
3. The system automatically:
   - Checks if the school exists in the database
   - If new: Creates a new school record
   - If existing: Updates the school information
   - Saves the complete invoice with all items
   - Links the invoice to the school (if not Floating Stock)
   - Generates and returns the PDF

### To View Invoice History:

Use the API endpoints in your frontend or via direct HTTP requests:

```javascript
// Get all invoices for a school
async function getSchoolHistory(schoolName) {
    const response = await fetch(`/api/schools/history/${encodeURIComponent(schoolName)}`);
    const data = await response.json();
    console.log(`${data.school_name} has ${data.invoice_count} invoices`);
    return data.invoices;
}

// Get specific invoice
async function getInvoice(invoiceNumber) {
    const response = await fetch(`/api/invoices/${invoiceNumber}`);
    const data = await response.json();
    return data.invoice;
}

// Reprint an invoice
async function reprintInvoice(invoiceNumber) {
    const response = await fetch(`/api/invoices/reprint/${invoiceNumber}`, {
        method: 'POST'
    });
    const data = await response.json();
    
    if (data.success) {
        // Convert base64 to blob and download
        const blob = base64ToBlob(data.pdf_data, 'application/pdf');
        const url = URL.createObjectURL(blob);
        window.open(url);
    }
}
```

## Benefits

1. **No Data Loss**: Every invoice is permanently saved
2. **Easy Retrieval**: Quickly find and reprint old invoices
3. **School Tracking**: See complete transaction history per school
4. **Automatic Updates**: School information stays current
5. **Audit Trail**: Complete record of all transactions
6. **Database Reports**: Can generate reports by date range, school, sales manager, etc.

## Database Location
The database file is stored as `invoices.db` in the project root directory. This is a SQLite database that can be backed up, migrated, or queried using standard SQL tools.

## Notes

- **Floating Stock** invoices are saved but not linked to the schools table
- **Special Market** manual entries are saved but only added to schools table if not already existing
- The database automatically initializes with all schools from `unique_schools.csv` on first run
- All timestamps are in the server's local timezone
- Invoice numbers are guaranteed unique

## Future Enhancements
Potential additions to consider:
- Web interface for browsing invoice history
- Advanced search and filtering
- Export to Excel/CSV
- Analytics dashboard
- Email invoice copies
- Customer portal for schools to view their history


