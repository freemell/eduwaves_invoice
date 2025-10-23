#!/usr/bin/env python3
"""
Debug test to identify the issue with discount functionality
"""

import requests
import json

def debug_test():
    """Debug the discount functionality step by step"""
    base_url = "http://localhost:5000"
    
    print("🔍 Debugging EDUwaves Invoice Discount Functionality")
    print("=" * 60)
    
    # Test 1: Generate a simple invoice
    print("\n1. Generating simple test invoice...")
    sample_data = {
        "invoice_type": "credit",
        "customer_name": "Debug Test School",
        "customer_phone": "08012345678",
        "customer_address": "Test Address",
        "sales_manager": "Test Manager",
        "items": [
            {
                "book_code": "DEBUG001",
                "title": "Debug Test Book",
                "grade": "Primary 1",
                "subject": "Mathematics",
                "price": 1000.0,
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
            json=sample_data
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                invoice_number = data['invoice_number']
                print(f"✅ Invoice generated: {invoice_number}")
                
                # Test 2: Try to get the invoice from database
                print(f"\n2. Testing database retrieval for: {invoice_number}")
                
                # Test 3: Try discount generation
                print(f"\n3. Testing discount generation...")
                discount_data = {"invoice_number": invoice_number}
                
                discount_response = requests.post(
                    f"{base_url}/api/generate-discounted-invoice",
                    headers={"Content-Type": "application/json"},
                    json=discount_data
                )
                
                print(f"Discount response status: {discount_response.status_code}")
                print(f"Discount response content: {discount_response.text}")
                
            else:
                print("❌ Invoice generation failed")
        else:
            print(f"❌ Invoice request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_test()

