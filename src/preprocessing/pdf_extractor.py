"""
PDF text extraction for Amharic Bible processing
"""

import fitz  # PyMuPDF
import pdfplumber
import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class AmharicBiblePDFExtractor:
    """Extract and preprocess text from Amharic Bible PDF"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.raw_text = ""
        self.structured_text = {}
        
    def extract_with_pymupdf(self) -> str:
        """Extract text using PyMuPDF (better for Amharic text)"""
        try:
            doc = fitz.open(self.pdf_path)
            text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_blocks.append(text)
                    
            doc.close()
            return "\n".join(text_blocks)
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            return ""
    
    def extract_with_pdfplumber(self) -> str:
        """Alternative extraction using pdfplumber"""
        try:
            text_blocks = []
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_blocks.append(text)
            
            return "\n".join(text_blocks)
            
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return ""
    
    def extract_text(self, method: str = "pymupdf") -> str:
        """Extract text from PDF using specified method"""
        if method == "pymupdf":
            text = self.extract_with_pymupdf()
        elif method == "pdfplumber":
            text = self.extract_with_pdfplumber()
        else:
            raise ValueError(f"Unknown extraction method: {method}")
            
        if not text:
            logger.warning(f"No text extracted using {method}, trying alternative")
            # Try alternative method
            alt_method = "pdfplumber" if method == "pymupdf" else "pymupdf"
            text = self.extract_text(alt_method)
            
        self.raw_text = text
        return text
    
    def save_raw_text(self, output_path: str) -> None:
        """Save extracted raw text to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.raw_text)
            
        logger.info(f"Raw text saved to {output_path}")
    
    def get_basic_stats(self) -> Dict:
        """Get basic statistics about the extracted text"""
        if not self.raw_text:
            return {}
            
        lines = self.raw_text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Basic Amharic character detection
        amharic_chars = re.findall(r'[\u1200-\u137F]', self.raw_text)
        
        return {
            "total_characters": len(self.raw_text),
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty_lines),
            "amharic_characters": len(amharic_chars),
            "amharic_ratio": len(amharic_chars) / len(self.raw_text) if self.raw_text else 0,
            "estimated_pages": len(lines) // 50  # Rough estimate
        }

def main():
    """Main function to extract Bible PDF text"""
    pdf_path = "/Users/mekdesyared/Embedding/The Amharic Bible (Catholic Edition - Emmaus) Final 2020_compressed.pdf"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/raw"
    
    # Initialize extractor
    extractor = AmharicBiblePDFExtractor(pdf_path)
    
    # Extract text
    print("Extracting text from PDF...")
    text = extractor.extract_text(method="pymupdf")
    
    if text:
        # Save raw text
        raw_output = f"{output_dir}/amharic_bible_raw.txt"
        extractor.save_raw_text(raw_output)
        
        # Print statistics
        stats = extractor.get_basic_stats()
        print("Extraction Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        print(f"\nRaw text saved to: {raw_output}")
        print(f"Text preview (first 500 chars):")
        print(text[:500])
        
    else:
        print("Failed to extract text from PDF")

if __name__ == "__main__":
    main()