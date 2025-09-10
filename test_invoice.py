import requests
import json

def test_invoice_generation():
    """
    Test the invoice generation API
    """
    # Test data
    test_data = {
        "invoice_type": "floating",
        "customer_name": "FEDERAL GOVERNMENT COLLEGE, KWALI",
        "customer_phone": "08032401126",
        "customer_address": "KWALI, ABUJA",
        "sales_manager": "PETER ETIM",
        "items": [
            {
                "book_code": "LIT/PRI/PRAC",
                "title": "PRACTICE WHAT YOU PREACH",
                "price": 1500.00,
                "quantity": 20
            }
        ],
        "discount_percent": 20.0
    }
    
    try:
        # Test the API
        response = requests.post('http://localhost:5000/api/generate-invoice', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Invoice generated successfully!")
            print(f"📄 Invoice Number: {result['invoice_number']}")
            print(f"📁 Filename: {result['filename']}")
            print(f"🔗 Download URL: http://localhost:5000/generated_invoices/{result['filename']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_book_search():
    """
    Test the book search API
    """
    try:
        response = requests.get('http://localhost:5000/api/books/search?q=math')
        
        if response.status_code == 200:
            books = response.json()
            print(f"✅ Found {len(books)} books matching 'math'")
            if books:
                print(f"📚 Sample book: {books[0]['title']} - N{books[0]['price']:,.2f}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_school_search():
    """
    Test the school search API
    """
    try:
        response = requests.get('http://localhost:5000/api/schools/search?q=federal')
        
        if response.status_code == 200:
            schools = response.json()
            print(f"✅ Found {len(schools)} schools matching 'federal'")
            if schools:
                print(f"🏫 Sample school: {schools[0]['name']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing EDUwaves Invoice Generator...")
    print("=" * 50)
    
    print("\n1. Testing Book Search API...")
    test_book_search()
    
    print("\n2. Testing School Search API...")
    test_school_search()
    
    print("\n3. Testing Invoice Generation API...")
    test_invoice_generation()
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("\n📝 To use the application:")
    print("   1. Open your browser")
    print("   2. Go to: http://localhost:5000")
    print("   3. Start creating invoices!")
