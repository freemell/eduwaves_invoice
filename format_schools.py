#!/usr/bin/env python3
"""
Script to format schools from unique_schools.csv into tuples.
Each school will be formatted as: ('SCHOOL NAME', 'PHONE_NUMBER')
"""

import csv
import os

def format_schools():
    """Read the CSV file and format each school as a tuple."""
    
    input_file = r"C:\Users\1\Documents\milla projects\invoice gen\unique_schools.csv"
    output_file = r"C:\Users\1\Documents\milla projects\invoice gen\formatted_schools.txt"
    
    schools = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                school_name = row['Customer_Name'].strip()
                phone_number = row['Phone_Number'].strip()
                
                # Skip empty rows
                if school_name and phone_number:
                    schools.append((school_name, phone_number))
        
        # Write formatted schools to output file
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write("# Formatted Schools as Tuples\n")
            outfile.write("# Format: ('SCHOOL NAME', 'PHONE_NUMBER')\n\n")
            
            for school_name, phone_number in schools:
                outfile.write(f"('{school_name}', '{phone_number}'),\n")
        
        print(f"Successfully formatted {len(schools)} schools")
        print(f"Output saved to: {output_file}")
        
        # Also print first few examples
        print("\nFirst 5 formatted schools:")
        for i, (school_name, phone_number) in enumerate(schools[:5]):
            print(f"('{school_name}', '{phone_number}'),")
            
    except FileNotFoundError:
        print(f"Error: Could not find input file: {input_file}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    format_schools()


