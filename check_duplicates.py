import pandas as pd

def check_duplicates(csv_file):
    """
    Check for duplicates in the CSV file
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        print("=== DUPLICATE CHECK REPORT ===")
        print(f"Total rows in CSV: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for exact duplicate rows
        exact_duplicates = df[df.duplicated()]
        print(f"\nExact duplicate rows: {len(exact_duplicates)}")
        
        if len(exact_duplicates) > 0:
            print("Duplicate entries found:")
            print(exact_duplicates)
        
        # Check unique counts for each column
        print(f"\nUnique counts per column:")
        for col in df.columns:
            unique_count = df[col].nunique()
            print(f"  {col}: {unique_count} unique values")
        
        # Check for duplicates based on Customer_Name only (school names)
        customer_duplicates = df[df.duplicated(subset=['Customer_Name'], keep=False)]
        print(f"\nSchools with duplicate names: {len(customer_duplicates)}")
        
        if len(customer_duplicates) > 0:
            print("Schools with duplicate names:")
            # Group by customer name to show duplicates
            duplicate_groups = customer_duplicates.groupby('Customer_Name')
            for name, group in duplicate_groups:
                if len(group) > 1:
                    print(f"\nSchool: {name}")
                    print(group[['SM_Name', 'Customer_Name', 'Phone_Number']].to_string(index=False))
        
        # Check for duplicates based on Phone_Number only
        phone_duplicates = df[df.duplicated(subset=['Phone_Number'], keep=False)]
        print(f"\nSchools with duplicate phone numbers: {len(phone_duplicates)}")
        
        if len(phone_duplicates) > 0:
            print("Schools with duplicate phone numbers:")
            # Group by phone number to show duplicates
            phone_groups = phone_duplicates.groupby('Phone_Number')
            for phone, group in phone_groups:
                if len(group) > 1:
                    print(f"\nPhone: {phone}")
                    print(group[['SM_Name', 'Customer_Name', 'Phone_Number']].to_string(index=False))
        
        # Check for duplicates based on combination of Customer_Name and Phone_Number
        combo_duplicates = df[df.duplicated(subset=['Customer_Name', 'Phone_Number'], keep=False)]
        print(f"\nSchools with duplicate name+phone combinations: {len(combo_duplicates)}")
        
        if len(combo_duplicates) > 0:
            print("Schools with duplicate name+phone combinations:")
            # Group by combination to show duplicates
            combo_groups = combo_duplicates.groupby(['Customer_Name', 'Phone_Number'])
            for (name, phone), group in combo_groups:
                if len(group) > 1:
                    print(f"\nSchool: {name}, Phone: {phone}")
                    print(group[['SM_Name', 'Customer_Name', 'Phone_Number']].to_string(index=False))
        
        # Summary
        print(f"\n=== SUMMARY ===")
        print(f"Total unique schools (by name): {df['Customer_Name'].nunique()}")
        print(f"Total unique phone numbers: {df['Phone_Number'].nunique()}")
        print(f"Total unique combinations (name+phone): {len(df.drop_duplicates(subset=['Customer_Name', 'Phone_Number']))}")
        print(f"Total unique rows (all columns): {len(df.drop_duplicates())}")
        
        if len(exact_duplicates) == 0:
            print("✅ No exact duplicate rows found!")
        else:
            print("❌ Exact duplicate rows found!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_duplicates("unique_schools.csv")
