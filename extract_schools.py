import pandas as pd
import sys

def extract_unique_schools(excel_file):
    """
    Extract unique school information from the Excel file
    """
    try:
        # Read the Excel file without headers first to see the structure
        df = pd.read_excel(excel_file, header=None)
        
        print("Excel file structure:")
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        # Look at the first few rows to understand the structure
        print("\nFirst 10 rows:")
        print(df.head(10))
        
        # Look for the header row (usually contains 'SMName' or similar)
        header_row = None
        for i in range(min(10, len(df))):
            row_values = df.iloc[i].astype(str).str.lower()
            if any('smname' in str(val) for val in row_values):
                header_row = i
                break
        
        if header_row is not None:
            print(f"\nFound header row at index: {header_row}")
            # Re-read with proper header
            df = pd.read_excel(excel_file, header=header_row)
            print("\nColumns after setting header:")
            print(df.columns.tolist())
            
            # Find the relevant columns
            smname_col = None
            customer_col = None
            phone_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if 'smname' in col_lower or ('sm' in col_lower and 'name' in col_lower):
                    smname_col = col
                elif 'customer' in col_lower and 'name' in col_lower:
                    customer_col = col
                elif 'phone' in col_lower or 'contact' in col_lower:
                    phone_col = col
            
            print(f"\nIdentified columns:")
            print(f"SM Name: {smname_col}")
            print(f"Customer Name: {customer_col}")
            print(f"Phone: {phone_col}")
            
            # If we found the columns, extract unique data
            if smname_col and customer_col and phone_col:
                # Extract unique combinations
                unique_schools = df[[smname_col, customer_col, phone_col]].drop_duplicates()
                unique_schools = unique_schools.dropna()  # Remove rows with missing data
                
                print(f"\nFound {len(unique_schools)} unique schools")
                
                # Rename columns for clarity
                unique_schools.columns = ['SM_Name', 'Customer_Name', 'Phone_Number']
                
                return unique_schools
            else:
                print("Could not identify all required columns.")
                print("Available columns:")
                for i, col in enumerate(df.columns):
                    print(f"  {i}: {col}")
                return None
        else:
            print("Could not find header row with 'SMName'. Let's examine the data structure more carefully.")
            
            # Look for patterns in the data
            print("\nExamining data patterns...")
            for i in range(min(5, len(df))):
                print(f"Row {i}: {df.iloc[i].tolist()}")
            
            return None
            
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def save_to_csv(data, filename):
    """
    Save the unique school data to CSV
    """
    try:
        data.to_csv(filename, index=False)
        print(f"Successfully saved {len(data)} unique schools to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    excel_file = "Visit Report_2025-02-12_2025-08-19.xlsx"
    
    print("Extracting unique school information from Excel file...")
    unique_schools = extract_unique_schools(excel_file)
    
    if unique_schools is not None and len(unique_schools) > 0:
        print("\nUnique schools data:")
        print(unique_schools)
        
        # Save to CSV
        csv_filename = "unique_schools.csv"
        save_to_csv(unique_schools, csv_filename)
    else:
        print("No unique school data could be extracted.")


