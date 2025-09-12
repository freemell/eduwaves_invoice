import re
import json
import pandas as pd

def parse_books_catalog():
    """
    Parse the BOOKS_CATALOG.md file and create a structured database
    """
    with open('BOOKS_CATALOG.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    books = []
    
    # Split content into sections
    sections = content.split('### ')
    
    current_subject = ""
    
    for section in sections:
        if '| Book Title |' in section:
            # Extract subject from section header
            lines = section.split('\n')
            subject_line = lines[0].strip()
            if subject_line:
                current_subject = subject_line
            
            # Find the table
            table_start = -1
            for i, line in enumerate(lines):
                if '| Book Title |' in line:
                    table_start = i
                    break
            
            if table_start >= 0:
                # Process table rows
                for i in range(table_start + 2, len(lines)):  # Skip header and separator
                    line = lines[i].strip()
                    if line.startswith('|') and '|' in line[1:]:
                        parts = [part.strip() for part in line.split('|')]
                        if len(parts) >= 5 and parts[1]:  # Ensure we have data
                            title = parts[1]
                            grade = parts[2]
                            price_str = parts[3].replace('₦', '').replace(',', '').strip()
                            
                            try:
                                price = float(price_str)
                                
                                # Generate book code
                                book_code = generate_book_code(title, grade, current_subject)
                                
                                books.append({
                                    'book_code': book_code,
                                    'title': title,
                                    'grade': grade,
                                    'price': price,
                                    'subject': current_subject,
                                    'search_terms': f"{title} {grade} {current_subject}".lower()
                                })
                            except ValueError:
                                continue
    
    return books

def generate_book_code(title, grade, subject):
    """
    Generate a unique book code based on title, grade, and subject
    """
    # Extract key words from title
    title_words = title.split()
    code_parts = []
    
    # Add subject abbreviation
    subject_abbr = {
        'Mathematics': 'MATH',
        'English': 'ENG',
        'Basic Science & Technology': 'BST',
        'Computer Studies': 'COMP',
        'National Values Education': 'NVE',
        'History': 'HIST',
        'Quantitative Reasoning': 'QR',
        'Verbal Reasoning': 'VR',
        'Writing': 'WRIT',
        'Health Education': 'HEALTH',
        'Social Studies': 'SOC',
        'Literature': 'LIT'
    }
    
    code_parts.append(subject_abbr.get(subject, 'GEN'))
    
    # Add grade abbreviation
    if 'Primary' in grade:
        grade_num = grade.split()[-1]
        code_parts.append(f"P{grade_num}")
    elif 'JSS' in grade:
        grade_num = grade.split()[-1]
        code_parts.append(f"J{grade_num}")
    else:
        code_parts.append("GEN")
    
    # Create more unique title abbreviation
    # Extract meaningful words and create unique identifier
    meaningful_words = []
    for word in title_words:
        word_clean = word.upper().replace('BOOK', '').replace('BK', '').replace('THE', '').replace('AND', '').replace('FOR', '').replace('OF', '').replace('IN', '').replace('TO', '')
        if len(word_clean) > 2:
            meaningful_words.append(word_clean)
    
    # Create unique identifier from meaningful words
    if meaningful_words:
        # Take first 2-3 characters from each meaningful word
        title_abbr = ''.join([word[:3] for word in meaningful_words[:3]])
        # Limit to 6 characters max
        title_abbr = title_abbr[:6]
    else:
        title_abbr = "GEN"
    
    code_parts.append(title_abbr)
    
    # Add a unique suffix based on subject to ensure uniqueness
    subject_suffix = {
        'Mathematics': 'M',
        'English': 'E',
        'Basic Science & Technology': 'S',
        'Computer Studies': 'C',
        'National Values Education': 'N',
        'History': 'H',
        'Quantitative Reasoning': 'Q',
        'Verbal Reasoning': 'V',
        'Writing': 'W',
        'Health Education': 'H',
        'Social Studies': 'S',
        'Literature': 'L',
        # Handle subjects with emojis
        '🏥 Health Education': 'H',
        '🌍 Social Studies': 'S',
        '📐 Mathematics': 'M',
        '📚 English': 'E',
        '🔬 Basic Science & Technology': 'S',
        '💻 Computer Studies': 'C',
        '🏛️ National Values Education': 'N',
        '📖 History': 'H',
        '🧮 Quantitative Reasoning': 'Q',
        '📝 Verbal Reasoning': 'V',
        '✍️ Writing': 'W',
        '📚 Literature': 'L',
        # Additional subject variations found in the data
        '📖 English Language': 'E',
        '🗣️ Verbal Reasoning': 'V',
        '✍️ Writing Skills': 'W'
    }
    
    # Add subject suffix to make it unique
    suffix = subject_suffix.get(subject, 'X')
    code_parts.append(suffix)
    
    return '/'.join(code_parts)

def save_books_database(books):
    """
    Save books to JSON and CSV for easy access
    """
    # Save as JSON
    with open('books_database.json', 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=2, ensure_ascii=False)
    
    # Save as CSV
    df = pd.DataFrame(books)
    df.to_csv('books_database.csv', index=False)
    
    print(f"✅ Parsed {len(books)} books successfully!")
    print(f"📚 Books saved to books_database.json and books_database.csv")
    
    return books

if __name__ == "__main__":
    print("📚 Parsing EDUwaves Books Catalog...")
    books = parse_books_catalog()
    save_books_database(books)
    
    # Show sample
    print("\n📖 Sample books:")
    for book in books[:5]:
        print(f"  {book['book_code']} - {book['title']} - ₦{book['price']:,.0f}")
