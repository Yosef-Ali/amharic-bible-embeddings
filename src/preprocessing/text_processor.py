"""
Text processing pipeline for extracted Amharic Bible text
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.amharic_cleaner import amharic_cleaner

logger = logging.getLogger(__name__)

class AmharicBibleProcessor:
    """Process raw extracted Bible text into structured format"""
    
    def __init__(self):
        self.cleaner = amharic_cleaner
        
    def identify_books_structure(self, text: str) -> Dict[str, str]:
        """Identify biblical books and their sections"""
        
        # Common Amharic Bible book patterns
        book_patterns = {
            # Old Testament
            r'ዘፍጥረት|ዘፍጠረት|ኦሪት ዘፍጠረት': 'ዘፍጥረት',
            r'ዘጸአት|ኦሪት ዘጸአት': 'ዘጸአት', 
            r'ዘሌዋውያን|ኦሪት ዘሌዋውያን': 'ዘሌዋውያን',
            r'ዘኍልቍ|ኦሪት ዘኍልቍ': 'ዘኍልቍ',
            r'ዘዳግም ሕግ|ኦሪት ዘዳግም ሕግ': 'ዘዳግም ሕግ',
            r'መጽሐፈ ኢያሱ|ኢያሱ': 'ኢያሱ',
            r'መጽሐፈ መሣፍንት|መሣፍንት': 'መሣፍንት',
            r'መጽሐፈ ሩት|ሩት': 'ሩት',
            r'መጽሐፈ ሳሙኤል ቀዳማዊ|1ኛ ሳሙኤል': '1ኛ ሳሙኤል',
            r'መጽሐፈ ሳሙኤል ካልዓዊ|2ኛ ሳሙኤል': '2ኛ ሳሙኤል',
            r'መጽሐፈ ነገሥት ቀዳማዊ|1ኛ ነገሥት': '1ኛ ነገሥት',
            r'መጽሐፈ ነገሥት ካልዓዊ|2ኛ ነገሥት': '2ኛ ነገሥት',
            r'መጽሐፈ ዜና መዋዕል ቀዳማዊ|1ኛ ዜና መዋዕል': '1ኛ ዜና መዋዕል',
            r'መጽሐፈ ዜና መዋዕል ካልዓዊ|2ኛ ዜና መዋዕል': '2ኛ ዜና መዋዕል',
            r'መጽሐፈ ዕዝራ|ዕዝራ': 'ዕዝራ',
            r'መጽሐፈ ነህምያ|ነህምያ': 'ነህምያ',
            r'መጽሐፈ አስቴር|አስቴር': 'አስቴር',
            r'መጽሐፈ ኢዮብ|ኢዮብ': 'ኢዮብ',
            r'መዝሙረ ዳዊት|መዝሙር': 'መዝሙረ ዳዊት',
            r'መጽሐፈ ምሳሌ|ምሳሌ': 'ምሳሌ',
            r'መጽሐፈ ማኅተመ ቃላት|ማኅተመ ቃላት': 'ማኅተመ ቃላት',
            r'መጽሐፈ መክብብ|መክብብ': 'መክብብ',
            r'ወልደ ሲራክ|ሲራክ': 'ወልደ ሲራክ',
            r'ኢሳይያስ': 'ኢሳይያስ',
            r'ኤርምያስ': 'ኤርምያስ',
            r'ሰቆቃው ኤርምያስ|ሰቆቃወ ኤርምያስ': 'ሰቆቃወ ኤርምያስ',
            r'ዕዝቅኤል': 'ዕዝቅኤል',
            r'ዳንኤል': 'ዳንኤል',
            r'ሆሴዕ': 'ሆሴዕ',
            r'ኢዮኤል': 'ኢዮኤል',
            r'አሞጽ': 'አሞጽ',
            r'አብድዩ|ዖባድያ': 'አብድዩ',
            r'ዮናስ': 'ዮናስ',
            r'ሚክያስ': 'ሚክያስ',
            r'ናሙ': 'ናሙ',
            r'ኃበቆቅ': 'ኃበቆቅ',
            r'ሶፎንያስ': 'ሶፎንያስ',
            r'ሐጌ': 'ሐጌ',
            r'ዘካርያስ': 'ዘካርያስ',
            r'ማላኪ': 'ማላኪ',
            
            # New Testament
            r'ወንጌል ዘማቴዎስ|ማቴዎስ': 'ማቴዎስ',
            r'ወንጌል ዘማርቆስ|ማርቆስ': 'ማርቆስ',
            r'ወንጌል ዘሉቃስ|ሉቃስ': 'ሉቃስ',
            r'ወንጌል ዘዮሐንስ|ዮሐንስ': 'ዮሐንስ',
            r'ግብረ ሐዋርያት|ግብረ ሀዋርያት': 'ግብረ ሐዋርያት',
            r'መልእክተ ጳውሎስ ወጣዴዎስ ቀዳማዊ|1ኛ ቆስጠንጢኖስ': '1ኛ ቆስጠንጢኖስ',
            r'መልእክተ ጳውሎስ ወጣዴዎስ ካልዓዊ|2ኛ ቆስጠንጢኖስ': '2ኛ ቆስጠንጢኖስ',
        }
        
        books_found = {}
        for pattern, book_name in book_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                position = match.start()
                books_found[book_name] = position
                
        return books_found
    
    def extract_chapters_and_verses(self, text: str) -> List[Dict]:
        """Extract structured chapters and verses"""
        
        # Patterns for chapters and verses
        chapter_pattern = r'መዋዕል\s*(\d+)|ምዕራፍ\s*(\d+)|(\d+)\s*፡'
        verse_pattern = r'(\d+)\s*[።፣]'
        
        chapters = []
        chapter_matches = list(re.finditer(chapter_pattern, text, re.MULTILINE))
        
        for i, chapter_match in enumerate(chapter_matches):
            chapter_start = chapter_match.end()
            chapter_end = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(text)
            
            chapter_text = text[chapter_start:chapter_end]
            chapter_num = (chapter_match.group(1) or 
                          chapter_match.group(2) or 
                          chapter_match.group(3))
            
            # Extract verses within this chapter
            verses = []
            verse_matches = list(re.finditer(verse_pattern, chapter_text))
            
            for j, verse_match in enumerate(verse_matches):
                verse_start = verse_match.end()
                verse_end = verse_matches[j+1].start() if j+1 < len(verse_matches) else len(chapter_text)
                
                verse_text = chapter_text[verse_start:verse_end]
                verse_num = verse_match.group(1)
                
                if verse_text.strip():
                    verses.append({
                        'verse': int(verse_num) if verse_num.isdigit() else verse_num,
                        'text': self.cleaner.clean_text(verse_text)
                    })
            
            if verses:
                chapters.append({
                    'chapter': int(chapter_num) if chapter_num.isdigit() else chapter_num,
                    'verses': verses
                })
                
        return chapters
    
    def process_raw_text(self, input_path: str, output_dir: str) -> Dict:
        """Process raw extracted text and save structured output"""
        
        input_file = Path(input_path)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Read raw text
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        
        logger.info(f"Processing {len(raw_text)} characters of raw text")
        
        # Clean the text
        cleaned_text = self.cleaner.clean_text(raw_text)
        
        # Identify books
        books_structure = self.identify_books_structure(cleaned_text)
        
        # Save cleaned text
        cleaned_file = output_path / "amharic_bible_cleaned.txt"
        with open(cleaned_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        # Save structure info
        structure_file = output_path / "bible_structure.txt"
        with open(structure_file, 'w', encoding='utf-8') as f:
            f.write("Identified Books:\n")
            for book, position in sorted(books_structure.items(), key=lambda x: x[1]):
                f.write(f"{book} (position: {position})\n")
        
        result = {
            "original_length": len(raw_text),
            "cleaned_length": len(cleaned_text),
            "books_found": len(books_structure),
            "books_list": list(books_structure.keys()),
            "cleaned_file": str(cleaned_file),
            "structure_file": str(structure_file)
        }
        
        logger.info(f"Processing complete: {result}")
        return result

def main():
    """Process the extracted Bible text"""
    processor = AmharicBibleProcessor()
    
    input_path = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/raw/amharic_bible_raw.txt"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed"
    
    result = processor.process_raw_text(input_path, output_dir)
    
    print("Text Processing Results:")
    for key, value in result.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()