"""
Biblical text parser for Amharic Bible structure extraction
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Verse:
    """Represents a single Bible verse"""
    book: str
    chapter: int
    verse: int
    text: str
    original_text: str

@dataclass
class Chapter:
    """Represents a Bible chapter"""
    book: str
    chapter: int
    verses: List[Verse]

@dataclass 
class Book:
    """Represents a Bible book"""
    name: str
    chapters: List[Chapter]
    testament: str  # "old" or "new"

class AmharicBiblicalParser:
    """Parse Amharic Bible text into structured format"""
    
    def __init__(self):
        self.books = []
        # Complete Catholic Bible (72 books) - based on table of contents
        self.book_order = {
            # Old Testament (46 books)
            'ኦሪት ዘፍጥረት': 1, 'ኦሪት ዘጸአት': 2, 'ኦሪት ዘሌዋውያን': 3, 'ኦሪት ዘኍልቍ': 4, 'ኦሪት ዘዳግም': 5,
            'መጽሐፈ ኢያሱ': 6, 'መጽሐፈ መሳፍንት': 7, 'መጽሐፈ ሩት': 8, '1ኛ መጽሐፈ ሳሙኤል': 9, '2ኛ መጽሐፈ ሳሙኤል': 10,
            '1ኛ መጽሐፈ ነገሥት': 11, '2ኛ መጽሐፈ ነገሥት': 12, '1ኛ መጽሐፈ ዜና መዋዕል': 13, '2ኛ መጽሐፈ ዜና መዋዕል': 14,
            'መጽሐፈ ዕዝራ': 15, 'መጽሐፈ ነህምያ': 16, 'መጽሐፈ ጦቢት': 17, 'መጽሐፈ ዮዲት': 18, 'መጽሐፈ አስቴር': 19,
            '1ኛ መጽሐፈ መቃብያን': 20, '2ኛ መጽሐፈ መቃብያን': 21, 'መጽሐፈ ኢዮብ': 22, 'መዝሙረ ዳዊት': 23, 'መጽሐፈ ምሳሌ': 24,
            'መጽሐፈ መክብብ': 25, 'መኃልየ መኃልይ': 26, 'መጽሐፈ ጥበብ': 27, 'መጽሐፈ ሲራክ': 28,
            'ትንቢተ ኢሳይያስ': 29, 'ትንቢተ ኤርምያስ': 30, 'ሰቆቃወ ኤርምያስ': 31, 'መጽሐፈ ባሮክ': 32,
            'ትንቢተ ሕዝቅኤል': 33, 'ትንቢተ ዳንኤል': 34, 'ትንቢተ ሆሴዕ': 35, 'ትንቢተ ኢዩኤል': 36,
            'ትንቢተ አሞጽ': 37, 'ትንቢተ አብድዩ': 38, 'ትንቢተ ዮናስ': 39, 'ትንቢተ ሚክያስ': 40,
            'ትንቢተ ናሆም': 41, 'ትንቢተ ዕንባቆም': 42, 'ትንቢተ ሶፎንያስ': 43, 'ትንቢተ ሐጌ': 44,
            'ትንቢተ ዘካርያስ': 45, 'ትንቢተ ሚልክያስ': 46,
            
            # New Testament (27 books)
            'የማቴዎስ ወንጌል': 47, 'የማርቆስ ወንጌል': 48, 'የሉቃስ ወንጌል': 49, 'የዮሐንስ ወንጌል': 50,
            'የሐዋርያት ሥራ': 51, 'ወደ ሮሜ ሰዎች': 52, '1ኛ ወደ ቆሮንቶስ ሰዎች': 53, '2ኛ ወደ ቆሮንቶስ ሰዎች': 54,
            'ወደ ገላትያ ሰዎች': 55, 'ወደ ኤፌሶን ሰዎች': 56, 'ወደ ፊልጵስዩስ ሰዎች': 57, 'ወደ ቈላስይስ ሰዎች': 58,
            '1ኛ ወደ ተሰሎንቄ ሰዎች': 59, '2ኛ ወደ ተሰሎንቄ ሰዎች': 60, '1ኛ ወደ ጢሞቴዎስ': 61, '2ኛ ወደ ጢሞቴዎስ': 62,
            'ወደ ቲቶ': 63, 'ወደ ፊልሞና': 64, 'ወደ ዕብራውያን': 65, 'የያዕቆብ መልእክት': 66,
            '1ኛ የጴጥሮስ መልእክት': 67, '2ኛ የጴጥሮስ መልእክት': 68, '1ኛ የዮሐንስ መልእክት': 69, '2ኛ የዮሐንስ መልእክት': 70,
            '3ኛ የዮሐንስ መልእክት': 71, 'የይሁዳ መልእክት': 72, 'የዮሐንስ ራእይ': 73
        }
    
    def identify_book_boundaries(self, text: str) -> List[Tuple[str, int, int]]:
        """Identify where each book starts and ends in the text"""
        
        # Complete book patterns matching the Catholic Bible table of contents
        book_patterns = [
            # Old Testament (46 books)
            (r'ኦሪት\s+ዘፍጥረት', 'ኦሪት ዘፍጥረት'),
            (r'ኦሪት\s+ዘጸአት', 'ኦሪት ዘጸአት'),
            (r'ኦሪት\s+ዘሌዋውያን', 'ኦሪት ዘሌዋውያን'),
            (r'ኦሪት\s+ዘኍልቍ', 'ኦሪት ዘኍልቍ'),
            (r'ኦሪት\s+ዘዳግም', 'ኦሪት ዘዳግም'),
            (r'መጽሐፈ\s+ኢያሱ', 'መጽሐፈ ኢያሱ'),
            (r'መጽሐፈ\s+መሳፍንት', 'መጽሐፈ መሳፍንት'),
            (r'መጽሐፈ\s+ሩት', 'መጽሐፈ ሩት'),
            (r'1ኛ\s+መጽሐፈ\s+ሳሙኤል', '1ኛ መጽሐፈ ሳሙኤል'),
            (r'2ኛ\s+መጽሐፈ\s+ሳሙኤል', '2ኛ መጽሐፈ ሳሙኤል'),
            (r'1ኛ\s+መጽሐፈ\s+ነገሥት', '1ኛ መጽሐፈ ነገሥት'),
            (r'2ኛ\s+መጽሐፈ\s+ነገሥት', '2ኛ መጽሐፈ ነገሥት'),
            (r'1ኛ\s+መጽሐፈ\s+ዜና\s+መዋዕል', '1ኛ መጽሐፈ ዜና መዋዕል'),
            (r'2ኛ\s+መጽሐፈ\s+ዜና\s+መዋዕል', '2ኛ መጽሐፈ ዜና መዋዕል'),
            (r'መጽሐፈ\s+ዕዝራ', 'መጽሐፈ ዕዝራ'),
            (r'መጽሐፈ\s+ነህምያ', 'መጽሐፈ ነህምያ'),
            (r'መጽሐፈ\s+ጦቢት', 'መጽሐፈ ጦቢት'),
            (r'መጽሐፈ\s+ዮዲት', 'መጽሐፈ ዮዲት'),
            (r'መጽሐፈ\s+አስቴር', 'መጽሐፈ አስቴር'),
            (r'1ኛ\s+መጽሐፈ\s+መቃብያን', '1ኛ መጽሐፈ መቃብያን'),
            (r'2ኛ\s+መጽሐፈ\s+መቃብያን', '2ኛ መጽሐፈ መቃብያን'),
            (r'መጽሐፈ\s+ኢዮብ', 'መጽሐፈ ኢዮብ'),
            (r'መዝሙረ\s+ዳዊት', 'መዝሙረ ዳዊት'),
            (r'መጽሐፈ\s+ምሳሌ', 'መጽሐፈ ምሳሌ'),
            (r'መጽሐፈ\s+መክብብ', 'መጽሐፈ መክብብ'),
            (r'መኃልየ\s+መኃልይ', 'መኃልየ መኃልይ'),
            (r'መጽሐፈ\s+ጥበብ', 'መጽሐፈ ጥበብ'),
            (r'መጽሐፈ\s+ሲራክ', 'መጽሐፈ ሲራክ'),
            (r'ትንቢተ\s+ኢሳይያስ', 'ትንቢተ ኢሳይያስ'),
            (r'ትንቢተ\s+ኤርምያስ', 'ትንቢተ ኤርምያስ'),
            (r'ሰቆቃወ\s+ኤርምያስ', 'ሰቆቃወ ኤርምያስ'),
            (r'መጽሐፈ\s+ባሮክ', 'መጽሐፈ ባሮክ'),
            (r'ትንቢተ\s+ሕዝቅኤል', 'ትንቢተ ሕዝቅኤል'),
            (r'ትንቢተ\s+ዳንኤል', 'ትንቢተ ዳንኤል'),
            (r'ትንቢተ\s+ሆሴዕ', 'ትንቢተ ሆሴዕ'),
            (r'ትንቢተ\s+ኢዩኤል', 'ትንቢተ ኢዩኤል'),
            (r'ትንቢተ\s+አሞጽ', 'ትንቢተ አሞጽ'),
            (r'ትንቢተ\s+አብድዩ', 'ትንቢተ አብድዩ'),
            (r'ትንቢተ\s+ዮናስ', 'ትንቢተ ዮናስ'),
            (r'ትንቢተ\s+ሚክያስ', 'ትንቢተ ሚክያስ'),
            (r'ትንቢተ\s+ናሆም', 'ትንቢተ ናሆም'),
            (r'ትንቢተ\s+ዕንባቆም', 'ትንቢተ ዕንባቆም'),
            (r'ትንቢተ\s+ሶፎንያስ', 'ትንቢተ ሶፎንያስ'),
            (r'ትንቢተ\s+ሐጌ', 'ትንቢተ ሐጌ'),
            (r'ትንቢተ\s+ዘካርያስ', 'ትንቢተ ዘካርያስ'),
            (r'ትንቢተ\s+ሚልክያስ', 'ትንቢተ ሚልክያስ'),
            
            # New Testament patterns
            (r'የማቴዎስ\s+ወንጌል', 'የማቴዎስ ወንጌል'),
            (r'የማርቆስ\s+ወንጌል', 'የማርቆስ ወንጌል'),
            (r'የሉቃስ\s+ወንጌል', 'የሉቃስ ወንጌል'),
            (r'የዮሐንስ\s+ወንጌል', 'የዮሐንስ ወንጌል'),
            (r'የሐዋርያት\s+ሥራ', 'የሐዋርያት ሥራ'),
            (r'ወደ\s+ሮሜ\s+ሰዎች', 'ወደ ሮሜ ሰዎች'),
            (r'1ኛ\s+ወደ\s+ቆሮንቶስ\s+ሰዎች', '1ኛ ወደ ቆሮንቶስ ሰዎች'),
            (r'2ኛ\s+ወደ\s+ቆሮንቶስ\s+ሰዎች', '2ኛ ወደ ቆሮንቶስ ሰዎች'),
            (r'ወደ\s+ገላትያ\s+ሰዎች', 'ወደ ገላትያ ሰዎች'),
            (r'ወደ\s+ኤፌሶን\s+ሰዎች', 'ወደ ኤፌሶን ሰዎች'),
            (r'ወደ\s+ፊልጵስዩስ\s+ሰዎች', 'ወደ ፊልጵስዩስ ሰዎች'),
            (r'ወደ\s+ቈላስይስ\s+ሰዎች', 'ወደ ቈላስይስ ሰዎች'),
            (r'1ኛ\s+ወደ\s+ተሰሎንቄ\s+ሰዎች', '1ኛ ወደ ተሰሎንቄ ሰዎች'),
            (r'2ኛ\s+ወደ\s+ተሰሎንቄ\s+ሰዎች', '2ኛ ወደ ተሰሎንቄ ሰዎች'),
            (r'1ኛ\s+ወደ\s+ጢሞቴዎስ', '1ኛ ወደ ጢሞቴዎስ'),
            (r'2ኛ\s+ወደ\s+ጢሞቴዎስ', '2ኛ ወደ ጢሞቴዎስ'),
            (r'ወደ\s+ቲቶ', 'ወደ ቲቶ'),
            (r'ወደ\s+ፊልሞና', 'ወደ ፊልሞና'),
            (r'ወደ\s+ዕብራውያን', 'ወደ ዕብራውያን'),
            (r'የያዕቆብ\s+መልእክት', 'የያዕቆብ መልእክት'),
            (r'1ኛ\s+የጴጥሮስ\s+መልእክት', '1ኛ የጴጥሮስ መልእክት'),
            (r'2ኛ\s+የጴጥሮስ\s+መልእክት', '2ኛ የጴጥሮስ መልእክት'),
            (r'1ኛ\s+የዮሐንስ\s+መልእክት', '1ኛ የዮሐንስ መልእክት'),
            (r'2ኛ\s+የዮሐንስ\s+መልእክት', '2ኛ የዮሐንስ መልእክት'),
            (r'3ኛ\s+የዮሐንስ\s+መልእክት', '3ኛ የዮሐንስ መልእክት'),
            (r'የይሁዳ\s+መልእክት', 'የይሁዳ መልእክት'),
            (r'የዮሐንስ\s+ራእይ', 'የዮሐንስ ራእይ'),
        ]
        
        boundaries = []
        for pattern, book_name in book_patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
            for match in matches:
                boundaries.append((book_name, match.start(), match.end()))
        
        # Sort by position in text
        boundaries.sort(key=lambda x: x[1])
        return boundaries
    
    def parse_chapter_verse_structure(self, text: str, book_name: str) -> List[Chapter]:
        """Parse chapters and verses within a book"""
        
        chapters = []
        
        # Chapter patterns - various formats used in Amharic Bibles
        chapter_patterns = [
            r'(?:ምዕራፍ|መዋዕል)\s*(\d+)',  # ምዕራፍ 1, መዋዕል 1
            r'(\d+)\s*፡',                    # 1፡
            r'(\d+)\s*[።]',                   # 1።
            r'^(\d+)\s*$'                    # Standalone number on line
        ]
        
        # Try to find chapter divisions
        chapter_matches = []
        for pattern in chapter_patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE))
            if len(matches) > 1:  # Need at least 2 chapters to be valid
                chapter_matches = matches
                break
        
        if not chapter_matches:
            # If no clear chapters found, treat entire book as one chapter
            verses = self.extract_verses_from_text(text, book_name, 1)
            if verses:
                chapters.append(Chapter(book=book_name, chapter=1, verses=verses))
            return chapters
        
        # Process each chapter
        for i, chapter_match in enumerate(chapter_matches):
            chapter_num = int(chapter_match.group(1))
            chapter_start = chapter_match.end()
            chapter_end = (chapter_matches[i+1].start() if i+1 < len(chapter_matches) 
                          else len(text))
            
            chapter_text = text[chapter_start:chapter_end]
            verses = self.extract_verses_from_text(chapter_text, book_name, chapter_num)
            
            if verses:
                chapters.append(Chapter(
                    book=book_name,
                    chapter=chapter_num, 
                    verses=verses
                ))
        
        return chapters
    
    def extract_verses_from_text(self, text: str, book_name: str, chapter_num: int) -> List[Verse]:
        """Extract individual verses from chapter text"""
        
        verses = []
        
        # Verse number patterns
        verse_patterns = [
            r'(\d+)\s*[።፣፤]',           # 1። 1፣ 1፤
            r'(\d+)\s*[:\-]',            # 1: 1-
            r'^(\d+)\s+',                # Line starting with number
            r'(\d+)\.?\s+'               # 1. or 1 with space
        ]
        
        verse_matches = []
        for pattern in verse_patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE))
            if matches:
                verse_matches = matches
                break
        
        if not verse_matches:
            # No verse numbers found, treat as single verse
            cleaned_text = text.strip()
            if cleaned_text:
                verses.append(Verse(
                    book=book_name,
                    chapter=chapter_num,
                    verse=1,
                    text=cleaned_text,
                    original_text=cleaned_text
                ))
            return verses
        
        # Extract verses
        for i, verse_match in enumerate(verse_matches):
            verse_num = int(verse_match.group(1))
            verse_start = verse_match.end()
            verse_end = (verse_matches[i+1].start() if i+1 < len(verse_matches) 
                        else len(text))
            
            verse_text = text[verse_start:verse_end].strip()
            
            if verse_text:
                verses.append(Verse(
                    book=book_name,
                    chapter=chapter_num,
                    verse=verse_num,
                    text=verse_text,
                    original_text=verse_text
                ))
        
        return verses
    
    def parse_bible_text(self, text_file: str) -> List[Book]:
        """Parse the entire Bible text into structured format"""
        
        with open(text_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
        
        logger.info(f"Parsing {len(full_text)} characters of Bible text")
        
        # Identify book boundaries
        book_boundaries = self.identify_book_boundaries(full_text)
        
        books = []
        for i, (book_name, start, end) in enumerate(book_boundaries):
            # Determine text span for this book
            book_start = end  # Start after book title
            book_end = (book_boundaries[i+1][1] if i+1 < len(book_boundaries) 
                       else len(full_text))
            
            book_text = full_text[book_start:book_end]
            
            # Parse chapters and verses
            chapters = self.parse_chapter_verse_structure(book_text, book_name)
            
            if chapters:
                # Determine testament
                testament = "old" if self.book_order.get(book_name, 50) <= 40 else "new"
                
                book = Book(
                    name=book_name,
                    chapters=chapters,
                    testament=testament
                )
                books.append(book)
                
                logger.info(f"Parsed {book_name}: {len(chapters)} chapters")
        
        self.books = books
        return books
    
    def save_structured_data(self, output_dir: str) -> Dict[str, str]:
        """Save parsed structure to JSON and text files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Prepare structured data for JSON
        bible_data = []
        
        for book in self.books:
            book_data = {
                "name": book.name,
                "testament": book.testament,
                "chapters": []
            }
            
            for chapter in book.chapters:
                chapter_data = {
                    "chapter": chapter.chapter,
                    "verses": []
                }
                
                for verse in chapter.verses:
                    chapter_data["verses"].append({
                        "verse": verse.verse,
                        "text": verse.text
                    })
                
                book_data["chapters"].append(chapter_data)
            
            bible_data.append(book_data)
        
        # Save JSON structure
        json_file = output_path / "amharic_bible_structured.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(bible_data, f, ensure_ascii=False, indent=2)
        
        # Save readable text format
        text_file = output_path / "amharic_bible_verses.txt" 
        with open(text_file, 'w', encoding='utf-8') as f:
            for book in self.books:
                f.write(f"\n=== {book.name} ({book.testament.upper()} TESTAMENT) ===\n\n")
                
                for chapter in book.chapters:
                    f.write(f"--- ምዕራፍ {chapter.chapter} ---\n")
                    
                    for verse in chapter.verses:
                        f.write(f"{verse.verse}። {verse.text}\n")
                    
                    f.write("\n")
        
        # Generate summary
        summary_file = output_path / "parsing_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            total_chapters = sum(len(book.chapters) for book in self.books)
            total_verses = sum(sum(len(ch.verses) for ch in book.chapters) 
                             for book in self.books)
            
            f.write(f"Amharic Bible Parsing Summary\n")
            f.write(f"{'='*40}\n")
            f.write(f"Total Books: {len(self.books)}\n")
            f.write(f"Total Chapters: {total_chapters}\n")
            f.write(f"Total Verses: {total_verses}\n\n")
            
            f.write("Books by Testament:\n")
            old_testament = [b for b in self.books if b.testament == "old"]
            new_testament = [b for b in self.books if b.testament == "new"]
            
            f.write(f"\nOld Testament ({len(old_testament)} books):\n")
            for book in old_testament:
                f.write(f"  {book.name}: {len(book.chapters)} chapters\n")
            
            f.write(f"\nNew Testament ({len(new_testament)} books):\n") 
            for book in new_testament:
                f.write(f"  {book.name}: {len(book.chapters)} chapters\n")
        
        return {
            "json_file": str(json_file),
            "text_file": str(text_file),
            "summary_file": str(summary_file)
        }

def main():
    """Parse the cleaned Bible text"""
    parser = AmharicBiblicalParser()
    
    input_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed/amharic_bible_cleaned.txt"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed"
    
    # Parse the text
    books = parser.parse_bible_text(input_file)
    
    # Save structured data
    files = parser.save_structured_data(output_dir)
    
    print("Biblical Parsing Complete:")
    print(f"  Books parsed: {len(books)}")
    print(f"  Output files: {list(files.values())}")

if __name__ == "__main__":
    main()