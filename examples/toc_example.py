#!/usr/bin/env python3
"""
Example: TOC Analysis for Multi-Page Books
Shows how the system detects and uses Table of Contents
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def simulate_toc_analysis():
    """
    Simulate TOC analysis on a multi-page book
    """
    
    print("📋 TOC Analysis Example - Multi-Page Book")
    print("=" * 60)
    
    # Simulate a complex Amharic religious book
    print("📚 Example Book: 'Ethiopian Orthodox Liturgical Guide'")
    print("📄 Pages: 150 scanned images")
    print("📋 TOC Location: Pages 3-5")
    print()
    
    print("🔍 Step 0: TOC Detection Process:")
    print("  1️⃣  Scan first 10 pages for TOC patterns")
    print("  2️⃣  Look for Ethiopian/Amharic chapter terms:")
    print("      - ምዕራፍ (Chapter)")
    print("      - ክፍል (Section)") 
    print("      - በዓል (Feast)")
    print("      - ጾም (Fast)")
    print("  3️⃣  Detect page number patterns (dots, lines)")
    print("  4️⃣  Extract hierarchical structure")
    print()
    
    print("✅ Detected TOC Structure:")
    print("-" * 40)
    
    # Simulate TOC entries
    toc_structure = {
        "has_toc": True,
        "toc_pages": [3, 4, 5],
        "entries": [
            {"title": "ምዕራፍ 1 - የአድባራት ስርዓት", "page_number": 12, "level": 1},
            {"title": "ምዕራፍ 2 - የበዓላት መርሃግብር", "page_number": 28, "level": 1},
            {"title": "በዓለ መስቀል", "page_number": 35, "level": 2},
            {"title": "በዓለ ልደት", "page_number": 42, "level": 2},
            {"title": "ምዕራፍ 3 - የጾም ስርዓቶች", "page_number": 68, "level": 1},
            {"title": "ዓቢይ ጾም", "page_number": 75, "level": 2},
            {"title": "የልደት ጾም", "page_number": 89, "level": 2},
            {"title": "ምዕራፍ 4 - የቅዱሳን ዘክር", "page_number": 105, "level": 1}
        ],
        "chapters": [
            {"title": "ምዕራፍ 1 - የአድባራት ስርዓት", "page_number": 12},
            {"title": "ምዕራፍ 2 - የበዓላት መርሃግብር", "page_number": 28}, 
            {"title": "ምዕራፍ 3 - የጾም ስርዓቶች", "page_number": 68},
            {"title": "ምዕራፍ 4 - የቅዱሳን ዘክር", "page_number": 105}
        ],
        "estimated_total_pages": 150
    }
    
    print("📖 Chapter Structure:")
    for chapter in toc_structure["chapters"]:
        print(f"  📚 {chapter['title']} (Page {chapter['page_number']})")
    print()
    
    print("🔍 TOC Validation Results:")
    print("  ✅ TOC covers 4 major chapters")
    print("  ✅ Page numbers in logical order")
    print("  ✅ Hierarchical structure detected")
    print("  ✅ Amharic religious terms identified")
    print("  ✅ Estimated 150 pages matches available images")
    print()
    
    print("🎯 How TOC Structure Guides Processing:")
    print("  1️⃣  Pages 1-11: Introduction/Preface")
    print("      → Embedding context: 'Introduction'")
    print("  2️⃣  Pages 12-27: Church Systems")
    print("      → Embedding context: 'ምዕራፍ 1 - የአድባራት ስርዓት'")
    print("  3️⃣  Pages 28-67: Feast Calendar")
    print("      → Embedding context: 'ምዕራፍ 2 - የበዓላት መርሃግብር'")
    print("  4️⃣  Pages 68-104: Fasting Rules")
    print("      → Embedding context: 'ምዕራፍ 3 - የጾም ስርዓቶች'")
    print("  5️⃣  Pages 105-150: Saints")
    print("      → Embedding context: 'ምዕራፍ 4 - የቅዱሳን ዘክር'")
    print()
    
    print("📦 Enhanced Embedding Chunks:")
    print("  🏷️  Each chunk now includes:")
    print("     - Chapter context from TOC")
    print("     - Section hierarchy level")
    print("     - Relative position in chapter")
    print("     - Book structure metadata")
    print()
    
    print("🚨 Why TOC Analysis is CRITICAL:")
    print("  ❌ WITHOUT TOC: Random page chunks")
    print("     'በዓለ መስቀል ይከበራል...'")
    print("     → No context about which chapter this belongs to")
    print()
    print("  ✅ WITH TOC: Contextual chunks")
    print("     'በዓለ መስቀል ይከበራል...'")
    print("     → Context: ምዕራፍ 2 - የበዓላት መርሃግብር, Page 35")
    print("     → AI understands this is about feast celebrations")
    print()
    
    print("💡 Real Usage:")
    print("""
from src.ocr.book_digitizer import BookDigitizer

digitizer = BookDigitizer()
result = digitizer.digitize_book(
    'ethiopian_book_images/',    # Your scanned pages
    'output/',                   # Output directory
    'Ethiopian Liturgical Guide' # Book title
)

# The system will:
# 1. FIRST analyze TOC structure
# 2. Then process pages with chapter context
# 3. Create embeddings with proper structure
# 4. Generate PDF preserving original layout
""")
    
    print("✨ Result: AI models trained on this data will understand:")
    print("  📚 Book structure and organization")
    print("  📖 Chapter relationships")
    print("  🎯 Context of each text passage")
    print("  🔍 Better semantic search capabilities")

def main():
    """Run the TOC example"""
    simulate_toc_analysis()
    
    print("\n" + "=" * 60)
    print("🎯 Key Takeaway:")
    print("TOC analysis MUST happen FIRST before any text processing!")
    print("This ensures embeddings have proper context and structure.")

if __name__ == "__main__":
    main()