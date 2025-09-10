# 📚 EDUwaves Invoice Generator

A professional web-based invoice generation system for EDUwaves Publishers Limited.

## ✨ Features

- **📖 Book Search**: Search through 93 educational books with autocomplete
- **🏫 School Database**: Access to 2,032 unique schools with smart search
- **💰 Invoice Types**: 
  - Floating Stock (Zenith Bank)
  - Credit School (Zenith Bank) 
  - Special Market (Globus Bank)
- **🏦 Bank Selection**: Automatic bank selection based on invoice type
- **📄 PDF Generation**: Professional invoices matching exact design
- **🎨 Modern UI**: Responsive design with EDUwaves branding
- **⚡ Real-time Calculations**: Automatic totals and discount calculations

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Visit http://localhost:5000
```

### Vercel Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Login and deploy
vercel login
vercel
vercel --prod
```

## 📁 Project Structure

```
├── app.py                 # Flask application
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Frontend interface
├── books_database.json  # Books catalog (93 books)
├── unique_schools.csv   # Schools database (2,032 schools)
└── logo.png            # EDUwaves logo
```

## 🎯 Usage

1. **Select Invoice Type**: Choose between Floating Stock, Credit School, or Special Market
2. **Add Customer**: Search and select school or enter manually for special markets
3. **Add Books**: Search and add books with quantities
4. **Set Discount**: Enter percentage discount (0-100%)
5. **Generate PDF**: Download professional invoice

## 🏦 Bank Details

### Zenith Bank (Normal Operations)
- **Account Name**: EDUWAVES PUBLISHERS LTD
- **Account Number**: 1229600064

### Globus Bank (Special Markets)
- **Account Name**: EDUWAVES PUBLISHERS LTD  
- **Account Number**: 1000429262

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **PDF Generation**: ReportLab
- **Data Processing**: Pandas
- **Deployment**: Vercel

## 📊 Data Sources

- **Books**: 93 educational books from Primary 1-6 and JSS 1-3
- **Schools**: 2,032 unique schools from visit reports
- **Prices**: ₦1,500 - ₦4,400 range

## 🔧 Configuration

The application automatically:
- Selects Zenith Bank for normal operations
- Selects Globus Bank for special markets
- Enables manual input for special market schools
- Generates unique invoice numbers (HO/IN/YYMMDDHHMM)

## 📱 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🆘 Support

For technical support or feature requests, please contact the development team.

---

**EDUwaves Publishers Limited**  
*Global Positioning for the African Child*
