#!/usr/bin/env python3
"""
Example: Complete Book Digitization
Shows how to OCR books and recreate PDFs with original layout
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ocr.book_digitizer import BookDigitizer

def main():
    """
    Complete example of book digitization
    """
    
    print("📚 Amharic Book Digitization Example")
    print("=" * 50)
    
    # Initialize digitizer
    digitizer = BookDigitizer()
    
    # Example book paths (adjust these for your actual books)
    examples = [
        {
            "name": "Ethiopian Bible",
            "images": "sample_images/bible_pages/",
            "output": "digitized_books/ethiopian_bible/"
        },
        {
            "name": "Liturgical Calendar",
            "images": "sample_images/calendar_pages/",
            "output": "digitized_books/liturgical_calendar/"
        },
        {
            "name": "Prayer Book",
            "images": "sample_images/prayer_book/", 
            "output": "digitized_books/prayer_book/"
        }
    ]
    
    print("📖 Available Examples:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example['name']}")
        print(f"     Input: {example['images']}")
        print(f"     Output: {example['output']}")
        print()
    
    # Demonstrate the complete pipeline
    print("🔄 Complete Digitization Pipeline:")
    print("  1️⃣  OCR text extraction from scanned pages")
    print("  2️⃣  Create embedding-ready chunks")
    print("  3️⃣  Generate searchable PDF with original layout")
    print("  4️⃣  Save in multiple formats")
    print()
    
    # Example usage code
    print("💻 Usage Example:")
    print("""
# Initialize the digitizer
digitizer = BookDigitizer()

# Digitize complete book
result = digitizer.digitize_book(
    image_dir='book_images/',           # Directory with scanned pages  
    output_dir='digitized_output/',     # Where to save results
    book_title='My Amharic Book'        # Book title for metadata
)

# Results include:
# - embeddings.json (for AI training)
# - recreated.pdf (searchable PDF with layout)
# - text.txt (plain text version)  
# - metadata.json (statistics and info)
# - training.jsonl (ML training format)
""")
    
    print("🎯 Perfect For:")
    print("  📚 Digitizing Amharic religious books")
    print("  🔤 Creating embedding training data") 
    print("  📄 Preserving original book layouts")
    print("  🔍 Making scanned books searchable")
    print("  💾 Long-term digital archiving")
    print()
    
    print("⚙️  Setup Requirements:")
    print("  pip install opencv-python reportlab pillow")
    print("  # For better Amharic support:")
    print("  # Download Noto Sans Ethiopic font")
    print()
    
    # Simulate processing a single example
    print("🔄 Simulated Processing:")
    print("Processing 'Ethiopian Calendar 2016'...")
    print("  ✅ Layout detected: single_page_multi_section")
    print("  ✅ Text extracted: 33 blocks, 2,501 characters")
    print("  ✅ Embeddings: 52 chunks generated")
    print("  ✅ PDF created: Searchable with original layout")
    print("  ✅ Files saved: 5 formats")
    print()
    
    print("📤 Output Files Generated:")
    print("  📦 Ethiopian_Calendar_2016_embeddings.json")
    print("  📄 Ethiopian_Calendar_2016_recreated.pdf")
    print("  📝 Ethiopian_Calendar_2016_text.txt")
    print("  📊 Ethiopian_Calendar_2016_metadata.json")
    print("  🤖 Ethiopian_Calendar_2016_training.jsonl")
    
    print("\n✨ Your books are now ready for:")
    print("  🤖 AI model training")
    print("  🔍 Full-text search")
    print("  📖 Digital reading")
    print("  💾 Permanent archiving")

if __name__ == "__main__":
    main()