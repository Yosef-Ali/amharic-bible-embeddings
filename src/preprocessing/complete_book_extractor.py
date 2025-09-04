"""
Complete book extractor to ensure all 72 Catholic books are captured
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

class CompleteBookExtractor:
    """Extract all 72 books using positional and pattern-based approach"""
    
    def __init__(self):
        # Complete Catholic Bible book list - all 72 books with exact TOC abbreviations
        self.book_mapping = {
            # Old Testament - 46 books
            'ዘፍ': 'መጽሐፈ ዘፍጥረት', 'ዘጸ': 'መጽሐፈ ዘጸአት', 'ዘሌ': 'መጽሐፈ ዘሌዋውያን', 
            'ዘኍ': 'መጽሐፈ ዘኍልቍ', 'ዘዳ': 'መጽሐፈ ዘዳግም', 'ኢያ': 'መጽሐፈ ኢያሱ',
            'መሳ': 'መጽሐፈ መሳፍንት', 'ሩት': 'መጽሐፈ ሩት', '1ሳሙ': '1ኛ መጽሐፈ ሳሙኤል',
            '2ሳሙ': '2ኛ መጽሐፈ ሳሙኤል', '1ነገ': '1ኛ መጽሐፈ ነገሥት', '2ነገ': '2ኛ መጽሐፈ ነገሥት',
            '1ዜ.መ': '1ኛ መጽሐፈ ዜና መዋዕል', '2ዜ.መ': '2ኛ መጽሐፈ ዜና መዋዕል',
            'ዕዝ': 'መጽሐፈ ዕዝራ', 'ነህ': 'መጽሐፈ ነህምያ', 'ጦቢ': 'መጽሐፈ ጦቢት',
            'ዮዲ': 'መጽሐፀ ዮዲት', 'አስ.ግ': 'መጽሐፈ አስቴር', '1መቃ': '1ኛ መጽሐፀ መቃብያን',
            '2መቃ': '2ኛ መጽሐፀ መቃብያን', 'ኢዮብ': 'መጽሐፀ ኢዮብ', 'መዝ': 'መዝሙረ ዳዊት',
            'ምሳ': 'መጽሐፀ ምሳሌ', 'መክ': 'መጽሐፀ መክብብ', 'መኃ.መኃ': 'መኃልየ መኃልይ',
            'ጥበ': 'መጽሐፀ ጥበብ', 'ሲራ': 'መጽሐፀ ሲራክ', 'ኢሳ': 'ትንቢተ ኢሳይያስ',
            'ኤር': 'ትንቢተ ኤርምያስ', 'ሰቆ.ኤ': 'ሰቆቃወ ኤርምያስ', 'ባሮክ': 'መጽሐፀ ባሮክ',
            'ሕዝ': 'ትንቢተ ሕዝቅኤል', 'ዳን': 'ትንቢተ ዳንኤል', 'ሆሴዕ': 'ትንቢተ ሆሴዕ',
            'ኢዩ': 'ትንቢተ ኢዩኤል', 'አሞጽ': 'ትንቢተ አሞጽ', 'አብ': 'ትንቢተ አብድዩ',
            'ዮናስ': 'ትንቢተ ዮናስ', 'ሚክ': 'ትንቢተ ሚክያስ', 'ናሆም': 'ትንቢተ ናሆም',
            'ዕን': 'ትንቢተ ዕንባቆም', 'ሶፎ': 'ትንቢተ ሶፎንያስ', 'ሐጌ': 'ትንቢተ ሐጌ',
            'ዘካ': 'ትንቢተ ዘካርያስ', 'ሚል': 'ትንቢተ ሚልክያስ',
            
            # New Testament - 27 books
            'ማቴ': 'የማቴዎስ ወንጌል', 'ማር': 'የማርቆስ ወንጌል', 'ሉቃ': 'የሉቃስ ወንጌል',
            'ዮሐ': 'የዮሐንስ ወንጌል', 'የሐዋ': 'የሐዋርያት ሥራ', 'ሮሜ': 'ወደ ሮሜ ሰዎች',
            '1ቆሮ': '1ኛ ወደ ቆሮንቶስ ሰዎች', '2ቆሮ': '2ኛ ወደ ቆሮንቶስ ሰዎች',
            'ገላ': 'ወደ ገላትያ ሰዎች', 'ኤፌ': 'ወደ ኤፌሶን ሰዎች', 'ፊልጵ': 'ወደ ፊልጵስዩስ ሰዎች',
            'ቈላ': 'ወደ ቈላስይስ ሰዎች', '1ተሰ': '1ኛ ወደ ተሰሎንቄ ሰዎች', '2ተሰ': '2ኛ ወደ ተሰሎንቄ ሰዎች',
            '1ጢሞ': '1ኛ ወደ ጢሞቴዎስ', '2ጢሞ': '2ኛ ወደ ጢሞቴዎስ', 'ቲቶ': 'ወደ ቲቶ',
            'ፊልሞ': 'ወደ ፊልሞና', 'ዕብ': 'ወደ ዕብራውያን', 'ያዕ': 'የያዕቆብ መልእክት',
            '1ጴጥ': '1ኛ የጴጥሮስ መልእክት', '2ጴጥ': '2ኛ የጴጥሮስ መልእክት',
            '1ዮሐ': '1ኛ የዮሐንስ መልእክት', '2ዮሐ': '2ኛ የዮሐንስ መልእክት',
            '3ዮሐ': '3ኛ የዮሐንስ መልእክት', 'ይሁዳ': 'የይሁዳ መልእክት', 'ራእ': 'የዮሐንስ ራእይ'
        }
    
    def find_all_book_references(self, text: str) -> Dict[str, List[int]]:
        """Find all references to books using multiple search strategies"""
        
        book_positions = {}
        
        # Strategy 1: Search with standard patterns
        for abbrev, full_name in self.book_mapping.items():
            patterns = [
                rf'{re.escape(full_name)}\s+(\d+)(?:[–-](\d+))?',  # Full name with chapters
                rf'{re.escape(abbrev)}\s*(\d+)(?:[–-](\d+))?',     # Abbreviation with chapters
                rf'{re.escape(full_name)}(?=\s|$)',                # Just the book name
                rf'{re.escape(abbrev)}(?=\s|$)',                   # Just the abbreviation
            ]
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
                
                if matches:
                    positions = [m.start() for m in matches]
                    
                    if full_name not in book_positions:
                        book_positions[full_name] = []
                    book_positions[full_name].extend(positions)
        
        # Strategy 2: Search using exact TOC format patterns
        for abbrev, full_name in self.book_mapping.items():
            if full_name not in book_positions:
                # Search for the exact book headers as they appear in the text
                exact_patterns = [
                    rf'መጽሐፈ\s+{re.escape(full_name.split()[-1])}',  # Last word pattern
                    rf'{re.escape(full_name)}',                      # Exact full name
                    rf'{re.escape(abbrev)}\s*\.*\s*\d+',            # TOC style: ጦቢ.....469
                    rf'{re.escape(full_name)}\s*\.*',               # Book name with dots
                ]
                
                for pattern in exact_patterns:
                    matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
                    if matches:
                        positions = [m.start() for m in matches]
                        if full_name not in book_positions:
                            book_positions[full_name] = []
                        book_positions[full_name].extend(positions)
        
        # Remove duplicates and sort
        for book in book_positions:
            book_positions[book] = sorted(list(set(book_positions[book])))
        
        return book_positions
    
    def extract_book_sections(self, text: str) -> Dict[str, str]:
        """Extract text content for each book"""
        
        book_positions = self.find_all_book_references(text)
        
        # Create a sorted list of all book starts
        all_positions = []
        for book, positions in book_positions.items():
            for pos in positions:
                all_positions.append((pos, book))
        
        all_positions.sort(key=lambda x: x[0])
        
        book_contents = {}
        
        for i, (start_pos, book_name) in enumerate(all_positions):
            # Find end position (start of next book or end of text)
            end_pos = all_positions[i + 1][0] if i + 1 < len(all_positions) else len(text)
            
            # Extract content
            content = text[start_pos:end_pos].strip()
            
            # If book already exists, concatenate (handling multiple occurrences)
            if book_name in book_contents:
                book_contents[book_name] += "\n\n" + content
            else:
                book_contents[book_name] = content
        
        return book_contents
    
    def create_book_chunks(self, book_contents: Dict[str, str]) -> List[Dict]:
        """Create chunks with book identification"""
        
        chunks = []
        chunk_id = 1
        
        for book_name, content in book_contents.items():
            # Split book content into manageable chunks
            paragraphs = content.split('\n\n')
            
            current_chunk = []
            current_length = 0
            target_length = 2000  # characters per chunk
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # If adding this paragraph exceeds target, save current chunk
                if current_length + len(paragraph) > target_length and current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    
                    chunks.append({
                        'id': chunk_id,
                        'book': book_name,
                        'testament': 'old' if chunk_id <= 46 else 'new',  # Approximate
                        'text': chunk_text,
                        'character_count': len(chunk_text),
                        'paragraph_count': len(current_chunk)
                    })
                    
                    chunk_id += 1
                    current_chunk = [paragraph]  # Start new chunk with current paragraph
                    current_length = len(paragraph)
                else:
                    current_chunk.append(paragraph)
                    current_length += len(paragraph)
            
            # Add final chunk for this book
            if current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'id': chunk_id,
                    'book': book_name,
                    'testament': 'old' if chunk_id <= 46 else 'new',
                    'text': chunk_text,
                    'character_count': len(chunk_text),
                    'paragraph_count': len(current_chunk)
                })
                chunk_id += 1
        
        return chunks
    
    def process_complete_bible(self, input_file: str, output_dir: str) -> Dict:
        """Process the complete Bible ensuring all 72 books are captured"""
        
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Processing {len(text)} characters for complete book extraction")
        
        # Find all book references
        book_positions = self.find_all_book_references(text)
        
        print(f"Books found: {len(book_positions)}/72")
        print("Found books:", list(book_positions.keys())[:10], "...")
        
        # Extract content for each book
        book_contents = self.extract_book_sections(text)
        
        # Create structured chunks
        chunks = self.create_book_chunks(book_contents)
        
        # Save results
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save chunks with book information
        chunks_file = output_path / "complete_bible_chunks.jsonl"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        # Save book mapping for reference
        books_file = output_path / "books_found.json"
        with open(books_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_books': len(book_positions),
                'books_found': list(book_positions.keys()),
                'book_positions': book_positions
            }, f, ensure_ascii=False, indent=2)
        
        # Create summary
        summary = {
            'total_books_found': len(book_positions),
            'total_chunks_created': len(chunks),
            'books_with_content': len(book_contents),
            'chunks_file': str(chunks_file),
            'books_file': str(books_file),
            'missing_books': []
        }
        
        # Check which books are missing
        expected_books = list(self.book_mapping.values())
        found_books = list(book_positions.keys())
        missing = [book for book in expected_books if book not in found_books]
        summary['missing_books'] = missing
        summary['missing_count'] = len(missing)
        
        return summary

def main():
    """Extract all 72 books"""
    extractor = CompleteBookExtractor()
    
    input_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed/amharic_bible_cleaned.txt"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/complete_extraction"
    
    result = extractor.process_complete_bible(input_file, output_dir)
    
    print("\nComplete Book Extraction Results:")
    print(f"  Books found: {result['total_books_found']}/72")
    print(f"  Books with content: {result['books_with_content']}")
    print(f"  Total chunks: {result['total_chunks_created']}")
    print(f"  Missing books: {result['missing_count']}")
    
    if result['missing_books']:
        print("  Missing book names:")
        for book in result['missing_books']:
            print(f"    {book}")
    
    # Print found books for verification
    print(f"\nAll found books ({len(result.get('books_found', []))}):") 
    for i, book in enumerate(result.get('books_found', []), 1):
        print(f"  {i:2d}. {book}")

if __name__ == "__main__":
    main()