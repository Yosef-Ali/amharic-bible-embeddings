"""
Smart Biblical parser that uses the table of contents and structure markers
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class BibleVerse:
    book: str
    chapter: int
    verse: int
    text: str
    reference: str  # e.g., "ዘፍጥረት 1:1"

class SmartAmharicBibleParser:
    """Smart parser using structural markers and patterns"""
    
    def __init__(self):
        # Catholic Bible books in order (72 total)
        self.book_names = [
            # Old Testament (46 books)
            'ኦሪት ዘፍጥረት', 'ኦሪት ዘጸአት', 'ኦሪት ዘሌዋውያን', 'ኦሪት ዘኍልቍ', 'ኦሪት ዘዳግም',
            'መጽሐፈ ኢያሱ', 'መጽሐፈ መሳፍንት', 'መጽሐፈ ሩት', '1ኛ መጽሐፈ ሳሙኤል', '2ኛ መጽሐፈ ሳሙኤል',
            '1ኛ መጽሐፈ ነገሥት', '2ኛ መጽሐፈ ነገሥት', '1ኛ መጽሐፈ ዜና መዋዕል', '2ኛ መጽሐፈ ዜና መዋዕል',
            'መጽሐፈ ዕዝራ', 'መጽሐፈ ነህምያ', 'መጽሐፈ ጦቢት', 'መጽሐፈ ዮዲት', 'መጽሐፈ አስቴር',
            '1ኛ መጽሐፈ መቃብያን', '2ኛ መጽሐፈ መቃብያን', 'መጽሐፈ ኢዮብ', 'መዝሙረ ዳዊት', 'መጽሐፈ ምሳሌ',
            'መጽሐፈ መክብብ', 'መኃልየ መኃልይ', 'መጽሐፈ ጥበብ', 'መጽሐፈ ሲራክ',
            'ትንቢተ ኢሳይያስ', 'ትንቢተ ኤርምያስ', 'ሰቆቃወ ኤርምያስ', 'መጽሐፈ ባሮክ',
            'ትንቢተ ሕዝቅኤል', 'ትንቢተ ዳንኤል', 'ትንቢተ ሆሴዕ', 'ትንቢተ ኢዩኤል',
            'ትንቢተ አሞጽ', 'ትንቢተ አብድዩ', 'ትንቢተ ዮናስ', 'ትንቢተ ሚክያስ',
            'ትንቢተ ናሆም', 'ትንቢተ ዕንባቆም', 'ትንቢተ ሶፎንያስ', 'ትንቢተ ሐጌ',
            'ትንቢተ ዘካርያስ', 'ትንቢተ ሚልክያስ',
            
            # New Testament (27 books)  
            'የማቴዎስ ወንጌል', 'የማርቆስ ወንጌል', 'የሉቃስ ወንጌል', 'የዮሐንስ ወንጌል',
            'የሐዋርያት ሥራ', 'ወደ ሮሜ ሰዎች', '1ኛ ወደ ቆሮንቶስ ሰዎች', '2ኛ ወደ ቆሮንቶስ ሰዎች',
            'ወደ ገላትያ ሰዎች', 'ወደ ኤፌሶን ሰዎች', 'ወደ ፊልጵስዩስ ሰዎች', 'ወደ ቈላስይስ ሰዎች',
            '1ኛ ወደ ተሰሎንቄ ሰዎች', '2ኛ ወደ ተሰሎንቄ ሰዎች', '1ኛ ወደ ጢሞቴዎስ', '2ኛ ወደ ጢሞቴዎስ',
            'ወደ ቲቶ', 'ወደ ፊልሞና', 'ወደ ዕብራውያን', 'የያዕቆብ መልእክት',
            '1ኛ የጴጥሮስ መልእክት', '2ኛ የጴጥሮስ መልእክት', '1ኛ የዮሐንስ መልእክት', '2ኛ የዮሐንስ መልእክት',
            '3ኛ የዮሐንስ መልእክት', 'የይሁዳ መልእክት', 'የዮሐንስ ራእይ'
        ]
        
    def find_book_headers(self, text: str) -> List[Tuple[str, int]]:
        """Find actual book header positions (not references)"""
        
        book_positions = []
        
        # Look for book headers that are likely to be actual book starts
        # These should be on their own lines or have specific formatting
        for book_name in self.book_names:
            # Escape special regex characters in book name
            escaped_name = re.escape(book_name)
            
            # Pattern for standalone book headers (on their own line)
            patterns = [
                rf'^{escaped_name}\s*$',           # Exact match on its own line
                rf'^{escaped_name}\s+\d+\s*$',     # Book name followed by chapter number
                rf'^\s*{escaped_name}\s*$',        # Book name with optional whitespace
            ]
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
                
                # Filter out matches that are clearly in the middle of text
                valid_matches = []
                for match in matches:
                    start_pos = match.start()
                    # Check if this looks like a book header context
                    context_before = text[max(0, start_pos-200):start_pos]
                    context_after = text[start_pos:start_pos+200]
                    
                    # Skip if this appears to be a cross-reference
                    if any(marker in context_before[-50:] for marker in ['፣', '።', '፤', '(']):
                        continue
                        
                    valid_matches.append((book_name, start_pos))
                
                if valid_matches:
                    book_positions.extend(valid_matches)
                    break  # Found valid matches for this book
        
        # Remove duplicates and sort by position
        unique_positions = {}
        for book, pos in book_positions:
            if book not in unique_positions or pos < unique_positions[book]:
                unique_positions[book] = pos
        
        return [(book, pos) for book, pos in unique_positions.items()]
    
    def extract_book_content(self, text: str, book_start: int, book_end: int) -> str:
        """Extract clean content for a book between positions"""
        content = text[book_start:book_end]
        
        # Remove book introduction/commentary sections
        # Look for the actual biblical text start
        patterns = [
            r'(\d+\s*[፦:]?\s*\d+)',  # Chapter:verse pattern
            r'(ምዕራፍ\s+\d+)',       # Chapter pattern
            r'(\d+\s*[።፣፤])',        # Verse start pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # Start from where biblical text begins
                content = content[match.start():]
                break
        
        return content.strip()
    
    def parse_chapters_and_verses(self, book_content: str, book_name: str) -> List[Dict]:
        """Parse chapters and verses from book content"""
        
        chapters = []
        
        # Find chapter markers
        chapter_pattern = r'(?:^|\n)\s*(?:ምዕራፍ\s+)?(\d+)\s*(?:[፦:]|$)'
        chapter_matches = list(re.finditer(chapter_pattern, book_content, re.MULTILINE))
        
        if not chapter_matches:
            # Try alternative patterns
            chapter_pattern = r'(\d+)\s*(?:[፦:].*?(?=\d+[።፣፤]|$))'
            chapter_matches = list(re.finditer(chapter_pattern, book_content, re.MULTILINE | re.DOTALL))
        
        if not chapter_matches:
            # Treat whole book as one chapter
            verses = self.extract_verses(book_content, book_name, 1)
            if verses:
                chapters.append({
                    'chapter': 1,
                    'verses': verses
                })
            return chapters
        
        # Process each chapter
        for i, chapter_match in enumerate(chapter_matches):
            try:
                chapter_num = int(chapter_match.group(1))
                chapter_start = chapter_match.end()
                chapter_end = (chapter_matches[i+1].start() if i+1 < len(chapter_matches) 
                              else len(book_content))
                
                chapter_text = book_content[chapter_start:chapter_end]
                verses = self.extract_verses(chapter_text, book_name, chapter_num)
                
                if verses:
                    chapters.append({
                        'chapter': chapter_num,
                        'verses': verses
                    })
            except (ValueError, IndexError):
                continue
        
        return chapters
    
    def extract_verses(self, chapter_text: str, book_name: str, chapter_num: int) -> List[Dict]:
        """Extract verses from chapter text"""
        
        verses = []
        
        # Pattern for verse numbers
        verse_pattern = r'(\d+)\s*[።፣፤]\s*(.*?)(?=\d+\s*[።፣፤]|$)'
        verse_matches = list(re.finditer(verse_pattern, chapter_text, re.DOTALL))
        
        if not verse_matches:
            # Alternative pattern
            verse_pattern = r'(\d+)\s+(.*?)(?=\n\d+\s|$)'
            verse_matches = list(re.finditer(verse_pattern, chapter_text, re.MULTILINE | re.DOTALL))
        
        for match in verse_matches:
            try:
                verse_num = int(match.group(1))
                verse_text = match.group(2).strip()
                
                if verse_text and len(verse_text) > 10:  # Filter out very short matches
                    # Clean the verse text
                    verse_text = re.sub(r'\s+', ' ', verse_text)
                    verse_text = verse_text.strip()
                    
                    verses.append({
                        'verse': verse_num,
                        'text': verse_text,
                        'reference': f"{book_name} {chapter_num}:{verse_num}"
                    })
            except (ValueError, IndexError):
                continue
        
        return verses
    
    def parse_bible(self, input_file: str) -> Dict:
        """Main parsing method"""
        
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f"Starting smart parsing of {len(text)} characters")
        
        # Find book header positions
        book_positions = self.find_book_headers(text)
        book_positions.sort(key=lambda x: x[1])  # Sort by position
        
        logger.info(f"Found {len(book_positions)} book headers")
        
        parsed_books = []
        
        for i, (book_name, start_pos) in enumerate(book_positions):
            # Determine end position
            end_pos = (book_positions[i+1][1] if i+1 < len(book_positions) 
                      else len(text))
            
            # Extract book content
            book_content = self.extract_book_content(text, start_pos, end_pos)
            
            if len(book_content) > 100:  # Skip very short books
                # Parse chapters and verses
                chapters = self.parse_chapters_and_verses(book_content, book_name)
                
                if chapters:
                    testament = "old" if book_name in self.book_names[:46] else "new"
                    
                    parsed_books.append({
                        'name': book_name,
                        'testament': testament,
                        'chapters': chapters,
                        'total_verses': sum(len(ch['verses']) for ch in chapters)
                    })
                    
                    logger.info(f"Parsed {book_name}: {len(chapters)} chapters, "
                               f"{sum(len(ch['verses']) for ch in chapters)} verses")
        
        return {
            'books': parsed_books,
            'total_books': len(parsed_books),
            'total_chapters': sum(len(book['chapters']) for book in parsed_books),
            'total_verses': sum(book['total_verses'] for book in parsed_books)
        }
    
    def save_parsed_data(self, parsed_data: Dict, output_dir: str) -> Dict[str, str]:
        """Save parsed data to files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON format
        json_file = output_path / "catholic_bible_structured.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        
        # Save verses in simple format for embeddings
        verses_file = output_path / "catholic_bible_verses.jsonl"
        with open(verses_file, 'w', encoding='utf-8') as f:
            for book in parsed_data['books']:
                for chapter in book['chapters']:
                    for verse in chapter['verses']:
                        verse_data = {
                            'book': book['name'],
                            'testament': book['testament'],
                            'chapter': chapter['chapter'],
                            'verse': verse['verse'],
                            'text': verse['text'],
                            'reference': verse['reference']
                        }
                        f.write(json.dumps(verse_data, ensure_ascii=False) + '\n')
        
        # Save human-readable summary
        summary_file = output_path / "catholic_bible_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Catholic Amharic Bible Parsing Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Books: {parsed_data['total_books']}\n")
            f.write(f"Total Chapters: {parsed_data['total_chapters']}\n") 
            f.write(f"Total Verses: {parsed_data['total_verses']}\n\n")
            
            # Books by testament
            old_books = [b for b in parsed_data['books'] if b['testament'] == 'old']
            new_books = [b for b in parsed_data['books'] if b['testament'] == 'new']
            
            f.write(f"Old Testament ({len(old_books)} books):\n")
            for book in old_books:
                f.write(f"  {book['name']}: {len(book['chapters'])} chapters, {book['total_verses']} verses\n")
            
            f.write(f"\nNew Testament ({len(new_books)} books):\n")
            for book in new_books:
                f.write(f"  {book['name']}: {len(book['chapters'])} chapters, {book['total_verses']} verses\n")
        
        return {
            'json_file': str(json_file),
            'verses_file': str(verses_file), 
            'summary_file': str(summary_file)
        }

def main():
    """Parse the Bible using smart approach"""
    parser = SmartAmharicBibleParser()
    
    input_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed/amharic_bible_cleaned.txt"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed"
    
    # Parse the Bible
    parsed_data = parser.parse_bible(input_file)
    
    # Save results
    files = parser.save_parsed_data(parsed_data, output_dir)
    
    print("Smart Biblical Parsing Results:")
    print(f"  Books found: {parsed_data['total_books']}/72")
    print(f"  Total chapters: {parsed_data['total_chapters']}")
    print(f"  Total verses: {parsed_data['total_verses']}")
    print(f"  Output files: {list(files.values())}")

if __name__ == "__main__":
    main()