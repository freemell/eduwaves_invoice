#!/usr/bin/env python3
"""
Test script to verify the discount functionality works correctly
"""

import requests
import json
import time

def test_discount_functionality():
    """Test the complete discount functionality"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing EDUwaves Invoice Discount Functionality")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Generate a sample invoice
    print("\n2. Generating sample invoice...")
    sample_invoice_data = {
        "invoice_type": "credit",
        "customer_name": "Test School",
        "customer_phone": "08012345678",
        "customer_address": "Test Address",
        "sales_manager": "Test Manager",
        "items": [
            {
                "book_code": "TEST001",
                "title": "Test Book 1",
                "grade": "Primary 1",
                "subject": "Mathematics",
                "price": 1000.0,
                "quantity": 2
            },
            {
                "book_code": "TEST002", 
                "title": "Test Book 2",
                "grade": "Primary 2",
                "subject": "English",
                "price": 1500.0,
                "quantity": 1
            }
        ],
        "discount_percent": 0,
        "bank_name": "ZENITH BANK",
        "account_number": "1229600064"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate-invoice",
            headers={"Content-Type": "application/json"},
            json=sample_invoice_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                invoice_number = data['invoice_number']
                print(f"✅ Sample invoice generated: {invoice_number}")
                
                # Test 3: Generate discounted version
                print("\n3. Generating 20% discounted invoice...")
                time.sleep(1)  # Small delay to ensure different timestamps
                
                discount_response = requests.post(
                    f"{base_url}/api/generate-discounted-invoice",
                    headers={"Content-Type": "application/json"},
                    json={"invoice_number": invoice_number}
                )
                
                if discount_response.status_code == 200:
                    discount_data = discount_response.json()
                    if discount_data.get('success'):
                        print(f"✅ Discounted invoice generated: {discount_data['discounted_invoice_number']}")
                        print(f"   Original total: N{discount_data['original_total']:,.2f}")
                        print(f"   Discounted total: N{discount_data['discounted_total']:,.2f}")
                        print(f"   Discount applied: {discount_data['discount_applied']}%")
                        
                        # Verify the discount calculation
                        expected_discount = discount_data['original_total'] * 0.20
                        expected_total = discount_data['original_total'] - expected_discount
                        
                        if abs(discount_data['discounted_total'] - expected_total) < 0.01:
                            print("✅ Discount calculation is correct")
                        else:
                            print("❌ Discount calculation is incorrect")
                            
                    else:
                        print(f"❌ Discounted invoice generation failed: {discount_data.get('error')}")
                else:
                    print(f"❌ Discounted invoice request failed: {discount_response.status_code}")
            else:
                print("❌ Sample invoice generation failed")
        else:
            print(f"❌ Sample invoice request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Discount functionality test completed!")

if __name__ == "__main__":
    test_discount_functionality()

