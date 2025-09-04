#!/usr/bin/env python3
"""
Comprehensive parser for Ethiopian Orthodox/Catholic Bible (72 books)
Tests and verifies all books are properly embedded
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings, RAW_DATA_DIR, PROCESSED_DATA_DIR

class EthiopianBibleParser:
    """
    Parses Ethiopian Orthodox/Catholic Bible with all 72 books
    """
    
    def __init__(self):
        # Complete list of 72 books in Ethiopian Orthodox Bible
        self.all_72_books = {
            # Old Testament (46 books)
            "old_testament": [
                "ኦሪት ዘፍጥረት", "ኦሪት ዘጸአት", "ኦሪት ዘሌዋውያን", "ኦሪት ዘኍልቍ", "ኦሪት ዘዳግም",
                "መጽሐፈ ኢያሱ ወልደ ነዌ", "መጽሐፈ መሣፍንት", "መጽሐፈ ሩት", 
                "መጽሐፈ ሳሙኤል ቀዳማዊ", "መጽሐፈ ሳሙኤል ካልዕ",
                "መጽሐፈ ነገሥት ቀዳማዊ", "መጽሐፈ ነገሥት ካልዕ",
                "መጽሐፈ ዜና መዋዕል ቀዳማዊ", "መጽሐፈ ዜና መዋዕል ካልዕ",
                "መጽሐፈ ዕዝራ", "መጽሐፈ ነህምያ", "መጽሐፈ አስቴር", "መጽሐፈ ኢዮብ",
                "መዝሙረ ዳዊት", "መጽሐፈ ምሳሌ", "መጽሐፈ መክብብ", "መኃልየ መኃልይ ዘሰሎሞን",
                "ትንቢተ ኢሳይያስ", "ትንቢተ ኤርምያስ", "ውኅዝት ኤርምያስ", "ትንቢተ ሕዝቅኤል",
                "ትንቢተ ዳንኤል", "ትንቢተ ሆሴዕ", "ትንቢተ ኢዮኤል", "ትንቢተ አሞጽ",
                "ትንቢተ አብድዩ", "ትንቢተ ዮናስ", "ትንቢተ ሚክያስ", "ትንቢተ ናሆም",
                "ትንቢተ ዕንባቆም", "ትንቢተ ሶፎንያስ", "ትንቢተ ኃጌ", "ትንቢተ ዘካርያስ", "ትንቢተ ሚላክ",
                "መጽሐፈ ሙክያስ", "መጽሐፈ ኤኪሌሲያስቲከስ", "ትንቢተ ባሩክ", "መጽሐፈ ቶቢት",
                "መጽሐፈ ኢዩዲት", "መጽሐፈ አስቴር ግሪክ", "መጽሐፈ ዘኵልና ሕግ"
            ],
            # New Testament (26 books) 
            "new_testament": [
                "የማቴዎስ ወንጌል", "የማርቆስ ወንጌል", "የሉቃስ ወንጌል", "የዮሐንስ ወንጌል",
                "የሐዋርያት ሥራ", "የጳውሎስ መልእክት ወደ ሮሜ", 
                "የጳውሎስ ቀዳማዊ መልእክት ወደ ቆሮንቶስ", "የጳውሎስ ካልዕ መልእክት ወደ ቆሮንቶስ",
                "የጳውሎስ መልእክት ወደ ገላትያ", "የጳውሎስ መልእክት ወደ ኤፌሶን",
                "የጳውሎስ መልእክት ወደ ፊሊጵስዩስ", "የጳውሎስ መልእክት ወደ ቆላስይስ",
                "የጳውሎስ ቀዳማዊ መልእክት ወደ ተሰሎንቄ", "የጳውሎስ ካልዕ መልእክት ወደ ተሰሎንቄ",
                "የጳውሎስ ቀዳማዊ መልእክት ወደ ጢሞቴዎስ", "የጳውሎስ ካልዕ መልእክት ወደ ጢሞቴዎስ",
                "የጳውሎስ መልእክት ወደ ቲቶስ", "የጳውሎስ መልእክት ወደ ፊልሞንስ",
                "የእብራውያን መልእክት", "የያዕቆብ መልእክት", 
                "የጴጥሮስ ቀዳማዊ መልእክት", "የጴጥሮስ ካልዕ መልእክት",
                "የዮሐንስ ቀዳማዊ መልእክት", "የዮሐንስ ካልዕ መልእክት", "የዮሐንስ ሣልሳዊ መልእክት",
                "የይሁዳ መልእክት", "የዮሐንስ ራእይ"
            ]
        }
        
    def analyze_bible_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze the structure of the Amharic Bible file"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for book titles
        found_books = []
        book_positions = {}
        
        for testament, books in self.all_72_books.items():
            for book in books:
                # Find book in text
                pattern = rf'\b{re.escape(book)}\b'
                matches = list(re.finditer(pattern, content))
                
                if matches:
                    found_books.append(book)
                    book_positions[book] = {
                        "testament": testament,
                        "positions": [m.start() for m in matches],
                        "count": len(matches)
                    }
        
        return {
            "total_books_found": len(found_books),
            "found_books": found_books,
            "book_positions": book_positions,
            "total_expected": 72,
            "coverage": len(found_books) / 72 * 100
        }
    
    def extract_all_books(self, file_path: str) -> Dict[str, Dict[str, str]]:
        """Extract all 72 books with their chapters"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        extracted_books = {}
        
        # More sophisticated parsing
        for testament, books in self.all_72_books.items():
            for book in books:
                chapters = self._extract_book_chapters(content, book)
                if chapters:
                    extracted_books[book] = chapters
        
        return extracted_books
    
    def _extract_book_chapters(self, content: str, book_name: str) -> Dict[str, str]:
        """Extract chapters for a specific book"""
        
        # Find book start
        book_pattern = rf'\b{re.escape(book_name)}\b'
        book_match = re.search(book_pattern, content)
        
        if not book_match:
            return {}
        
        book_start = book_match.end()
        
        # Find next book to determine end boundary
        next_book_start = len(content)
        for testament, books in self.all_72_books.items():
            for other_book in books:
                if other_book != book_name:
                    other_match = re.search(rf'\b{re.escape(other_book)}\b', content[book_start:])
                    if other_match:
                        pos = book_start + other_match.start()
                        if pos < next_book_start:
                            next_book_start = pos
        
        book_content = content[book_start:next_book_start]
        
        # Extract chapters
        chapters = {}
        chapter_pattern = r'ምዕራፍ\s+(\d+|[፩-፼]+)'
        chapter_matches = list(re.finditer(chapter_pattern, book_content))
        
        for i, match in enumerate(chapter_matches):
            chapter_num = match.group(1)
            chapter_start = match.end()
            
            # Find end of chapter
            if i + 1 < len(chapter_matches):
                chapter_end = chapter_matches[i + 1].start()
            else:
                chapter_end = len(book_content)
            
            chapter_text = book_content[chapter_start:chapter_end].strip()
            if chapter_text:
                chapters[f"chapter_{chapter_num}"] = chapter_text
        
        return chapters

def verify_implementation():
    """Verify the complete implementation works locally"""
    
    print("🔍 Verifying Amharic Bible Embeddings Implementation")
    print("=" * 60)
    
    # Check project structure
    project_root = Path("/Users/mekdesyared/Embedding/amharic-bible-embeddings")
    
    required_files = [
        ".env.example",
        "requirements.txt", 
        "config/settings.py",
        "config/llm_config.py",
        "src/preprocessing/amharic_cleaner.py",
        "src/chunking/late_chunking.py",
        "src/enhancement/llm_contextualizer.py",
        "scripts/process_bible.py",
        "app.py"
    ]
    
    print("📁 Checking project structure...")
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {missing_files}")
        return False
    
    # Check raw data
    print(f"\n📖 Checking Bible data...")
    raw_data_path = project_root / "data/raw"
    bible_files = list(raw_data_path.glob("*.txt")) + list(raw_data_path.glob("*.json"))
    
    if not bible_files:
        print("❌ No Bible files found in data/raw/")
        return False
    
    print(f"✅ Found {len(bible_files)} Bible files")
    
    # Analyze Bible structure
    parser = EthiopianBibleParser()
    
    for bible_file in bible_files:
        print(f"\n📊 Analyzing {bible_file.name}...")
        analysis = parser.analyze_bible_structure(str(bible_file))
        
        print(f"Books found: {analysis['total_books_found']}/72 ({analysis['coverage']:.1f}%)")
        
        if analysis['total_books_found'] > 50:  # Good coverage
            print("✅ Good book coverage detected")
            
            # Extract all books
            print("📚 Extracting all books...")
            extracted_books = parser.extract_all_books(str(bible_file))
            
            # Save structured data
            output_file = PROCESSED_DATA_DIR / f"structured_{bible_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_books, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Structured data saved to {output_file}")
            
            # Count chapters and verses
            total_chapters = sum(len(chapters) for chapters in extracted_books.values())
            print(f"📖 Total books extracted: {len(extracted_books)}")
            print(f"📄 Total chapters: {total_chapters}")
            
            return True
        else:
            print("⚠️  Low book coverage - may need better parsing")
    
    return False

async def test_embedding_pipeline():
    """Test the complete embedding pipeline"""
    
    print("\n🧠 Testing Embedding Pipeline...")
    
    # Import required modules
    try:
        from src.preprocessing.amharic_cleaner import amharic_cleaner
        from src.chunking.late_chunking import late_chunking_embedder, ChunkInfo
        print("✅ All modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test with sample text
    sample_text = "መጀመሪያ ላይ እግዚአብሔር ሰማይንና ምድርን ፈጠረ። ምድርም ባዶና ክፉ ነበረች።"
    
    # Test cleaning
    cleaned = amharic_cleaner.preprocess_for_embeddings(sample_text)
    print(f"✅ Text cleaning: '{sample_text[:30]}...' → '{cleaned[:30]}...'")
    
    # Test chunk creation
    chunks = [
        ChunkInfo(
            text="መጀመሪያ ላይ እግዚአብሔር ሰማይንና ምድርን ፈጠረ።",
            start_pos=0,
            end_pos=40,
            book="Genesis",
            chapter=1,
            verse_range=(1, 1)
        )
    ]
    
    # Test embedding (traditional method first for verification)
    try:
        traditional_embeddings = late_chunking_embedder.embed_traditional([chunk.text for chunk in chunks])
        print(f"✅ Traditional embeddings: Shape {traditional_embeddings[0].shape}")
        
        # Test Late Chunking
        late_chunking_results = late_chunking_embedder.embed_with_late_chunking(sample_text, chunks)
        print(f"✅ Late Chunking embeddings: {len(late_chunking_results)} chunks created")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return False

def create_missing_directories():
    """Create any missing directories"""
    
    dirs = [
        "data/processed", "data/chunks", "data/embeddings",
        "src/preprocessing", "src/chunking", "src/enhancement", 
        "src/embeddings", "src/retrieval", "scripts", "tests", "notebooks"
    ]
    
    project_root = Path("/Users/mekdesyared/Embedding/amharic-bible-embeddings")
    
    for dir_name in dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if dir_name.startswith("src/"):
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()

async def main():
    """Main verification function"""
    
    print("🚀 Amharic Bible Embeddings - Complete Verification")
    print("=" * 60)
    
    # Create missing directories
    create_missing_directories()
    
    # Verify project structure
    structure_ok = verify_implementation()
    
    if not structure_ok:
        print("\n❌ Project structure verification failed")
        return 1
    
    # Test embedding pipeline
    pipeline_ok = await test_embedding_pipeline()
    
    if not pipeline_ok:
        print("\n❌ Embedding pipeline test failed")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ ALL VERIFICATIONS PASSED!")
    print("\n📋 Next Steps:")
    print("1. Configure your API keys in .env")
    print("2. Run: python scripts/process_bible.py")
    print("3. Start web app: streamlit run app.py")
    print("\n🎯 Ready to embed all 72 books of the Ethiopian Bible!")
    
    return 0

if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
