#!/usr/bin/env python3
"""
Deployment preparation script for Vercel
"""

import os
import shutil
import json

def prepare_for_vercel():
    """
    Prepare the project for Vercel deployment
    """
    print("🚀 Preparing project for Vercel deployment...")
    
    # Check required files
    required_files = [
        'app.py',
        'vercel.json', 
        'requirements.txt',
        'templates/index.html',
        'books_database.json',
        'unique_schools.csv',
        'WhatsApp_Image_2025-08-01_at_12.46.28_e1c96073-removebg-preview.png'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    
    # Check if data files have content
    try:
        with open('books_database.json', 'r') as f:
            books = json.load(f)
        print(f"✅ Books database: {len(books)} books")
    except:
        print("❌ Books database is empty or corrupted")
        return False
    
    try:
        import pandas as pd
        df = pd.read_csv('unique_schools.csv')
        print(f"✅ Schools database: {len(df)} schools")
    except:
        print("❌ Schools database is empty or corrupted")
        return False
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        print("✅ Created static directory")
    
    print("\n🎉 Project is ready for Vercel deployment!")
    print("\nNext steps:")
    print("1. Install Vercel CLI: npm i -g vercel")
    print("2. Login: vercel login")
    print("3. Deploy: vercel")
    print("4. Production: vercel --prod")
    
    return True

if __name__ == "__main__":
    prepare_for_vercel()
