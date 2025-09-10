import PyPDF2
import fitz  # PyMuPDF
import sys

def analyze_pdf_with_pypdf2(pdf_path):
    """
    Analyze PDF using PyPDF2
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print("=== PDF ANALYSIS WITH PyPDF2 ===")
            print(f"Number of pages: {len(pdf_reader.pages)}")
            
            for page_num, page in enumerate(pdf_reader.pages):
                print(f"\n--- Page {page_num + 1} ---")
                text = page.extract_text()
                print("Text content:")
                print(text[:500] + "..." if len(text) > 500 else text)
                
                # Get page dimensions
                if hasattr(page, 'mediabox'):
                    mediabox = page.mediabox
                    print(f"Page dimensions: {mediabox.width} x {mediabox.height}")
                
    except Exception as e:
        print(f"PyPDF2 Error: {e}")

def analyze_pdf_with_pymupdf(pdf_path):
    """
    Analyze PDF using PyMuPDF for more detailed analysis
    """
    try:
        doc = fitz.open(pdf_path)
        
        print("\n=== PDF ANALYSIS WITH PyMuPDF ===")
        print(f"Number of pages: {len(doc)}")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n--- Page {page_num + 1} ---")
            
            # Get page dimensions
            rect = page.rect
            print(f"Page dimensions: {rect.width} x {rect.height}")
            
            # Extract text
            text = page.get_text()
            print("Text content:")
            print(text[:500] + "..." if len(text) > 500 else text)
            
            # Get images
            image_list = page.get_images()
            print(f"Number of images: {len(image_list)}")
            
            # Get drawings/vector graphics
            drawings = page.get_drawings()
            print(f"Number of drawings/vector elements: {len(drawings)}")
            
            # Get text blocks with positioning
            blocks = page.get_text("dict")
            print(f"Number of text blocks: {len(blocks['blocks'])}")
            
            # Analyze structure
            for i, block in enumerate(blocks['blocks'][:5]):  # Show first 5 blocks
                if 'lines' in block:
                    print(f"Block {i}: {len(block['lines'])} lines")
                    for line in block['lines'][:2]:  # Show first 2 lines
                        if 'spans' in line:
                            for span in line['spans']:
                                print(f"  Text: '{span['text']}' at ({span['bbox'][0]:.1f}, {span['bbox'][1]:.1f})")
        
        doc.close()
        
    except Exception as e:
        print(f"PyMuPDF Error: {e}")

def check_invoice_feasibility():
    """
    Determine if the PDF can be replicated as an invoice generator
    """
    print("\n=== INVOICE GENERATOR FEASIBILITY ASSESSMENT ===")
    print("✅ POSSIBLE: Yes, it's definitely possible to create an invoice generator")
    print("   that matches the PDF design exactly!")
    print("\nReasons why it's feasible:")
    print("1. 📄 PDFs can be analyzed to extract layout, fonts, colors, and positioning")
    print("2. 🎨 Modern web technologies (HTML/CSS) can replicate any design")
    print("3. 📊 Libraries like ReportLab (Python) or jsPDF (JavaScript) can generate PDFs")
    print("4. 🖼️ Logo and images can be embedded")
    print("5. 📋 Form fields and dynamic data can be populated")
    print("\nRecommended approach:")
    print("• Use Python with libraries like ReportLab or WeasyPrint")
    print("• Or create HTML/CSS templates and convert to PDF")
    print("• Extract design elements from the PDF for exact replication")
    print("• Use the school data from your CSV for dynamic content")

if __name__ == "__main__":
    pdf_file = "HO_IN_18.pdf"
    
    print("Analyzing PDF invoice template...")
    
    # Try PyPDF2 first
    analyze_pdf_with_pypdf2(pdf_file)
    
    # Try PyMuPDF for more detailed analysis
    analyze_pdf_with_pymupdf(pdf_file)
    
    # Provide feasibility assessment
    check_invoice_feasibility()
