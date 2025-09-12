import json

# Load books database
with open('books_database.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

# Extract all book codes
codes = [book['book_code'] for book in books]

# Check for duplicates
unique_codes = set(codes)
duplicates = []

for code in unique_codes:
    if codes.count(code) > 1:
        duplicates.append(code)

print(f"Total books: {len(books)}")
print(f"Unique codes: {len(unique_codes)}")
print(f"Duplicate codes: {len(duplicates)}")

if duplicates:
    print("\nDuplicate codes found:")
    for code in duplicates:
        print(f"  {code}")
        # Show which books have this code
        for book in books:
            if book['book_code'] == code:
                print(f"    - {book['title']}")
else:
    print("\n✅ All book codes are unique!")

# Show the specific books that were causing issues
print("\nChecking the problematic books:")
health_habits = [book for book in books if 'HEALTH HABITS BK 1' in book['title']]
social_habits = [book for book in books if 'SOCIAL HABITS BK 1' in book['title']]

for book in health_habits:
    print(f"Health Habits BK 1: {book['book_code']} - {book['title']}")

for book in social_habits:
    print(f"Social Habits BK 1: {book['book_code']} - {book['title']}")