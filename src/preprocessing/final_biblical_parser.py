"""
Final Biblical parser optimized for the Catholic Amharic Bible structure
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ParsedVerse:
    book: str
    chapter: int
    verse: int
    text: str
    reference: str

class CatholicAmharicBibleParser:
    """Optimized parser for Catholic Amharic Bible"""
    
    def __init__(self):
        # 72 Catholic Bible books in order
        self.catholic_books = [
            # Old Testament (46)
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
            
            # New Testament (27)
            'የማቴዎስ ወንጌል', 'የማርቆስ ወንጌል', 'የሉቃስ ወንጌል', 'የዮሐንስ ወንጌል',
            'የሐዋርያት ሥራ', 'ወደ ሮሜ ሰዎች', '1ኛ ወደ ቆሮንቶስ ሰዎች', '2ኛ ወደ ቆሮንቶስ ሰዎች',
            'ወደ ገላትያ ሰዎች', 'ወደ ኤፌሶን ሰዎች', 'ወደ ፊልጵስዩስ ሰዎች', 'ወደ ቈላስይስ ሰዎች',
            '1ኛ ወደ ተሰሎንቄ ሰዎች', '2ኛ ወደ ተሰሎንቄ ሰዎች', '1ኛ ወደ ጢሞቴዎስ', '2ኛ ወደ ጢሞቴዎስ',
            'ወደ ቲቶ', 'ወደ ፊልሞና', 'ወደ ዕብራውያን', 'የያዕቆብ መልእክት',
            '1ኛ የጴጥሮስ መልእክት', '2ኛ የጴጥሮስ መልእክት', '1ኛ የዮሐንስ መልእክት', '2ኛ የዮሐንስ መልእክት',
            '3ኛ የዮሐንስ መልእክት', 'የይሁዳ መልእክት', 'የዮሐንስ ራእይ'
        ]
    
    def extract_simple_verses(self, text: str) -> List[Dict]:
        """Extract verses using the chapter-range format (e.g., 'ኦሪት ዘፍጥረት 1-2')"""
        
        verses = []
        
        # Pattern to find book headers with chapter ranges
        book_chapter_pattern = r'([^0-9\n]+)\s+(\d+)(?:[–-](\d+))?'
        
        # Split text into sections
        sections = re.split(r'\n\s*\n', text)
        
        current_book = None
        current_chapter = 1
        verse_counter = 1
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Check if this section starts with a book name
            book_match = None
            for book in self.catholic_books:
                if section.startswith(book):
                    # Found a new book header
                    match = re.match(rf'{re.escape(book)}\s+(\d+)(?:[–-](\d+))?', section)
                    if match:
                        current_book = book
                        current_chapter = int(match.group(1))
                        verse_counter = 1
                        book_match = match
                        break
            
            if book_match and current_book:
                # Process the content after the book header
                content_start = book_match.end()
                content = section[content_start:].strip()
                
                # Extract verses from this section
                verse_texts = self.extract_verse_texts(content)
                
                for verse_text in verse_texts:
                    if len(verse_text.strip()) > 20:  # Filter very short text
                        verses.append({
                            'book': current_book,
                            'chapter': current_chapter,
                            'verse': verse_counter,
                            'text': verse_text.strip(),
                            'reference': f"{current_book} {current_chapter}:{verse_counter}"
                        })
                        verse_counter += 1
            
            elif current_book and not book_match:
                # Continue processing content for current book
                verse_texts = self.extract_verse_texts(section)
                
                for verse_text in verse_texts:
                    if len(verse_text.strip()) > 20:
                        verses.append({
                            'book': current_book,
                            'chapter': current_chapter,
                            'verse': verse_counter,
                            'text': verse_text.strip(),
                            'reference': f"{current_book} {current_chapter}:{verse_counter}"
                        })
                        verse_counter += 1
        
        return verses
    
    def extract_verse_texts(self, content: str) -> List[str]:
        """Extract individual verse texts from content"""
        
        # Try to split by verse markers
        verse_patterns = [
            r'(\d+)\s*[።]\s*',     # 1። verse marker
            r'(\d+)\s+',            # Simple number followed by space
            r'[።፣፤]\s*',           # Amharic punctuation
        ]
        
        # Try verse number pattern first
        verse_splits = re.split(r'\d+\s*[።]\s*', content)
        if len(verse_splits) > 1:
            return [v.strip() for v in verse_splits if v.strip()]
        
        # Try sentence splits
        sentence_splits = re.split(r'[።፤]\s*', content)
        if len(sentence_splits) > 1:
            return [s.strip() for s in sentence_splits if len(s.strip()) > 10]
        
        # Return as single verse if no clear splits
        return [content] if content.strip() else []
    
    def parse_catholic_bible(self, input_file: str) -> Dict:
        """Parse the Catholic Amharic Bible"""
        
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f"Parsing Catholic Bible from {len(text)} characters")
        
        # Extract all verses
        verses = self.extract_simple_verses(text)
        
        # Organize by books
        books_data = {}
        for verse in verses:
            book_name = verse['book']
            
            if book_name not in books_data:
                books_data[book_name] = {
                    'name': book_name,
                    'testament': 'old' if book_name in self.catholic_books[:46] else 'new',
                    'chapters': {}
                }
            
            chapter_num = verse['chapter']
            if chapter_num not in books_data[book_name]['chapters']:
                books_data[book_name]['chapters'][chapter_num] = []
            
            books_data[book_name]['chapters'][chapter_num].append({
                'verse': verse['verse'],
                'text': verse['text'],
                'reference': verse['reference']
            })
        
        # Convert to final format
        final_books = []
        for book_name in self.catholic_books:
            if book_name in books_data:
                book_data = books_data[book_name]
                chapters_list = []
                
                for chapter_num in sorted(book_data['chapters'].keys()):
                    chapters_list.append({
                        'chapter': chapter_num,
                        'verses': book_data['chapters'][chapter_num]
                    })
                
                book_data['chapters'] = chapters_list
                final_books.append(book_data)
        
        total_verses = sum(len(v) for v in verses)
        total_chapters = sum(len(book['chapters']) for book in final_books)
        
        return {
            'books': final_books,
            'total_books': len(final_books),
            'total_chapters': total_chapters,
            'total_verses': total_verses,
            'all_verses': verses
        }
    
    def save_results(self, parsed_data: Dict, output_dir: str) -> Dict[str, str]:
        """Save parsing results"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save complete structured data
        json_file = output_path / "catholic_bible_final.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        
        # Save verses for embedding (JSONL format)
        verses_file = output_path / "verses_for_embedding.jsonl"
        with open(verses_file, 'w', encoding='utf-8') as f:
            for verse in parsed_data['all_verses']:
                f.write(json.dumps(verse, ensure_ascii=False) + '\n')
        
        # Save readable summary
        summary_file = output_path / "final_parsing_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Catholic Amharic Bible - Final Parsing Summary\n")
            f.write("=" * 55 + "\n\n")
            f.write(f"Books Successfully Parsed: {parsed_data['total_books']}/73\n")")}],} ⏎```
            f.write(f"Total Chapters: {parsed_data['total_chapters']}\n")
            f.write(f"Total Verses: {parsed_data['total_verses']}\n\n")
            
            old_books = [b for b in parsed_data['books'] if b['testament'] == 'old']
            new_books = [b for b in parsed_data['books'] if b['testament'] == 'new']
            
            f.write(f"Old Testament ({len(old_books)} books):\n")
            for book in old_books:
                total_verses = sum(len(ch['verses']) for ch in book['chapters'])
                f.write(f"  {book['name']}: {len(book['chapters'])} chapters, {total_verses} verses\n")
            
            f.write(f"\nNew Testament ({len(new_books)} books):\n")
            for book in new_books:
                total_verses = sum(len(ch['verses']) for ch in book['chapters'])
                f.write(f"  {book['name']}: {len(book['chapters'])} chapters, {total_verses} verses\n")
        
        return {
            'json_file': str(json_file),
            'verses_file': str(verses_file),
            'summary_file': str(summary_file)
        }

def main():
    """Parse the Catholic Bible with optimized approach"""
    parser = CatholicAmharicBibleParser()
    
    input_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed/amharic_bible_cleaned.txt"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed"
    
    # Parse
    result = parser.parse_catholic_bible(input_file)
    
    # Save
    files = parser.save_results(result, output_dir)
    
    print("Catholic Bible Parsing Complete:")
    print(f"  Books parsed: {result['total_books']}/73")
    print(f"  Chapters: {result['total_chapters']}")
    print(f"  Verses: {result['total_verses']}")
    print(f"  Files: {list(files.values())}")

if __name__ == "__main__":
    main()