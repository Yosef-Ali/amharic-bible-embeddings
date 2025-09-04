"""
Amharic text cleaning and preprocessing utilities
"""
import re
from typing import List, Dict, Tuple
import unicodedata

class AmharicCleaner:
    """Handles Amharic-specific text cleaning and normalization"""
    
    def __init__(self):
        # Ge'ez script Unicode range: U+1200–U+137F
        self.geez_range = (0x1200, 0x137F)
        
        # Common Amharic punctuation
        self.amharic_punctuation = "።፣፤፥፦፧፨"
        
        # Ge'ez numerals mapping
        self.geez_numerals = {
            '፩': '1', '፪': '2', '፫': '3', '፬': '4', '፭': '5',
            '፮': '6', '፯': '7', '፰': '8', '፱': '9', '፲': '10',
            '፳': '20', '፴': '30', '፵': '40', '፶': '50',
            '፷': '60', '፸': '70', '፹': '80', '፺': '90', '፻': '100'
        }
    
    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters"""
        # Normalize to NFC form for consistent character representation
        return unicodedata.normalize('NFC', text)
    
    def clean_whitespace(self, text: str) -> str:
        """Clean excessive whitespace while preserving structure"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
        text = re.sub(r'\n\s+', '\n', text)      # Remove indented empty lines
        
        return text.strip()
    
    def normalize_geez_numerals(self, text: str, convert_to_arabic: bool = True) -> str:
        """Convert Ge'ez numerals to Arabic numerals or normalize them"""
        if convert_to_arabic:
            for geez, arabic in self.geez_numerals.items():
                text = text.replace(geez, arabic)
        return text
    
    def handle_fidel_variations(self, text: str) -> str:
        """Handle Fidel character variations that represent the same sound"""
        
        # Common Fidel normalizations
        fidel_mappings = {
            # Normalize similar sounding characters
            'ሠ': 'ሰ',  # se variants
            'ኅ': 'ኽ',  # he variants  
            'ዐ': 'አ',  # a variants
            'ፀ': 'ጸ',  # tse variants
        }
        
        for variant, standard in fidel_mappings.items():
            text = text.replace(variant, standard)
        
        return text
    
    def remove_diacritics_selective(self, text: str, preserve_meaning: bool = True) -> str:
        """Selectively remove diacritics while preserving meaning-changing marks"""
        if not preserve_meaning:
            # Remove all diacritics
            return ''.join(c for c in unicodedata.normalize('NFD', text) 
                          if unicodedata.category(c) != 'Mn')
        
        # Keep meaning-preserving diacritics in Amharic
        # This is conservative - only remove clearly decorative marks
        return text
    
    def extract_verse_numbers(self, text: str) -> Tuple[str, List[str]]:
        """Extract verse numbers from text and return cleaned text + verse numbers"""
        
        # Pattern for verse numbers (both Arabic and Ge'ez)
        verse_pattern = r'(\d+[:፦]\d+|\d+|[፩-፼]+)'
        
        verse_numbers = re.findall(verse_pattern, text)
        cleaned_text = re.sub(verse_pattern, '', text)
        
        return self.clean_whitespace(cleaned_text), verse_numbers
    
    def is_amharic_text(self, text: str, threshold: float = 0.7) -> bool:
        """Check if text contains significant Amharic content"""
        if not text:
            return False
        
        amharic_chars = 0
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                if self.geez_range[0] <= ord(char) <= self.geez_range[1]:
                    amharic_chars += 1
        
        if total_chars == 0:
            return False
        
        return (amharic_chars / total_chars) >= threshold
    
    def clean_text(self, text: str, 
                   normalize_numerals: bool = True,
                   handle_fidel: bool = True,
                   extract_verses: bool = False) -> str:
        """Complete cleaning pipeline for Amharic text"""
        
        if not text or not self.is_amharic_text(text):
            return text
        
        # Step 1: Unicode normalization
        text = self.normalize_unicode(text)
        
        # Step 2: Handle Fidel variations
        if handle_fidel:
            text = self.handle_fidel_variations(text)
        
        # Step 3: Normalize numerals
        if normalize_numerals:
            text = self.normalize_geez_numerals(text)
        
        # Step 4: Extract verse numbers if requested
        if extract_verses:
            text, verses = self.extract_verse_numbers(text)
        
        # Step 5: Clean whitespace
        text = self.clean_whitespace(text)
        
        return text
    
    def preprocess_for_embeddings(self, text: str) -> str:
        """Preprocessing specifically optimized for embedding generation"""
        
        # Clean but preserve important punctuation for context
        text = self.clean_text(
            text, 
            normalize_numerals=True,
            handle_fidel=True,
            extract_verses=False  # Keep verse structure for context
        )
        
        # Preserve biblical punctuation that carries meaning
        text = re.sub(r'[^\w\s።፣፤፥፦፧፨\-]', ' ', text)
        
        return self.clean_whitespace(text)

# Global cleaner instance
amharic_cleaner = AmharicCleaner()
