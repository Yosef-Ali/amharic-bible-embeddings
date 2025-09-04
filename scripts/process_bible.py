#!/usr/bin/env python3
"""
Main processing pipeline for Amharic Bible embeddings
Integrates Late Chunking with modern LLM enhancement
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings, RAW_DATA_DIR, PROCESSED_DATA_DIR, CHUNKS_DIR, EMBEDDINGS_DIR
from src.preprocessing.amharic_cleaner import amharic_cleaner
from src.chunking.late_chunking import late_chunking_embedder, ChunkInfo
from src.enhancement.llm_contextualizer import llm_contextualizer

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BibleProcessor:
    """Main pipeline for processing Amharic Bible text"""
    
    def __init__(self):
        self.cleaner = amharic_cleaner
        self.embedder = late_chunking_embedder
        self.contextualizer = llm_contextualizer
    
    def load_bible_data(self) -> Dict[str, str]:
        """Load Amharic Bible data from raw directory"""
        
        bible_files = {}
        raw_path = Path(RAW_DATA_DIR)
        
        # Look for common Bible file formats
        for file_path in raw_path.glob("*"):
            if file_path.suffix in ['.txt', '.json', '.csv']:
                logger.info(f"Loading Bible file: {file_path.name}")
                
                try:
                    if file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            bible_files[file_path.stem] = data
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            bible_files[file_path.stem] = content
                            
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")
        
        return bible_files
    
    def parse_bible_structure(self, text: str) -> List[Dict[str, Any]]:
        """Parse Bible text into books, chapters, and verses"""
        
        chapters = []
        
        # Simple parsing - can be enhanced with better structure detection
        # This assumes one chapter per processing call
        
        # Clean the text
        cleaned_text = self.cleaner.preprocess_for_embeddings(text)
        
        # Split into verses (basic approach)
        verses = self._split_verses(cleaned_text)
        
        for i, verse_text in enumerate(verses, 1):
            if verse_text.strip():
                chapters.append({
                    "verse_number": i,
                    "text": verse_text.strip(),
                    "cleaned_text": verse_text.strip(),
                    "length": len(verse_text)
                })
        
        return chapters
    
    def _split_verses(self, text: str) -> List[str]:
        """Split text into verses using various indicators"""
        import re
        
        # Try multiple splitting patterns
        patterns = [
            r'\n\d+\s',  # Newline + number + space
            r'\d+[:፦]\d+',  # Chapter:verse format
            r'[፩-፼]+\s',  # Ge'ez numerals
            r'።\s*(?=\S)',  # Amharic period followed by text
        ]
        
        for pattern in patterns:
            verses = re.split(pattern, text)
            if len(verses) > 1:
                return [v.strip() for v in verses if v.strip()]
        
        # Fallback: split by sentences
        sentences = text.split('።')
        return [s.strip() + '።' for s in sentences if s.strip()]
    
    def create_chunk_infos(self, parsed_verses: List[Dict[str, Any]], 
                          book_name: str, chapter_num: int) -> List[ChunkInfo]:
        """Convert parsed verses to ChunkInfo objects"""
        
        chunk_infos = []
        current_pos = 0
        
        for verse in parsed_verses:
            verse_text = verse["cleaned_text"]
            verse_num = verse["verse_number"]
            
            chunk_info = ChunkInfo(
                text=verse_text,
                start_pos=current_pos,
                end_pos=current_pos + len(verse_text),
                book=book_name,
                chapter=chapter_num,
                verse_range=(verse_num, verse_num)
            )
            
            chunk_infos.append(chunk_info)
            current_pos += len(verse_text) + 1  # +1 for separator
        
        return chunk_infos
    
    async def process_chapter(self, chapter_text: str, 
                            book_name: str, chapter_num: int) -> Dict[str, Any]:
        """Process a single Bible chapter through the complete pipeline"""
        
        logger.info(f"Processing {book_name} Chapter {chapter_num}")
        
        # Step 1: Parse structure
        parsed_verses = self.parse_bible_structure(chapter_text)
        logger.info(f"Found {len(parsed_verses)} verses")
        
        # Step 2: Create chunk infos
        chunk_infos = self.create_chunk_infos(parsed_verses, book_name, chapter_num)
        
        # Step 3: LLM Enhancement (optional - can be disabled for speed)
        if settings.ENABLE_THEOLOGICAL_CONTEXT:
            logger.info("Enhancing with LLM context...")
            enhanced_chunks = await self.contextualizer.create_contextual_chunks(
                chapter_text, book_name, chapter_num
            )
            
            # Update chunk_infos with enhanced context
            for i, enhanced in enumerate(enhanced_chunks):
                if i < len(chunk_infos):
                    chunk_infos[i].context = enhanced.get("contextual_enhancement", "")
        
        # Step 4: Late Chunking Embedding
        logger.info("Generating Late Chunking embeddings...")
        embeddings_result = self.embedder.embed_with_late_chunking(chapter_text, chunk_infos)
        
        # Step 5: Save results
        chapter_data = {
            "book": book_name,
            "chapter": chapter_num,
            "total_verses": len(parsed_verses),
            "chunks": embeddings_result,
            "processing_metadata": {
                "late_chunking_enabled": True,
                "llm_enhancement_enabled": settings.ENABLE_THEOLOGICAL_CONTEXT,
                "embedding_model": settings.EMBEDDING_MODEL,
                "chunk_count": len(embeddings_result)
            }
        }
        
        return chapter_data
    
    async def process_all_bible(self) -> Dict[str, Any]:
        """Process the entire Bible through the pipeline"""
        
        logger.info("Starting Amharic Bible processing pipeline")
        
        # Load Bible data
        bible_data = self.load_bible_data()
        if not bible_data:
            raise ValueError("No Bible data found in raw directory")
        
        all_results = {}
        
        for filename, content in bible_data.items():
            logger.info(f"Processing file: {filename}")
            
            if isinstance(content, dict):
                # Handle structured JSON data
                for book_name, book_content in content.items():
                    if isinstance(book_content, dict):
                        for chapter_key, chapter_text in book_content.items():
                            chapter_num = self._extract_chapter_number(chapter_key)
                            result = await self.process_chapter(chapter_text, book_name, chapter_num)
                            all_results[f"{book_name}_{chapter_num}"] = result
                    else:
                        # Single book content
                        result = await self.process_chapter(book_content, book_name, 1)
                        all_results[f"{book_name}_1"] = result
            else:
                # Handle plain text
                result = await self.process_chapter(content, filename, 1)
                all_results[f"{filename}_1"] = result
        
        # Save complete results
        output_path = PROCESSED_DATA_DIR / "complete_bible_embeddings.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            # Convert numpy arrays to lists for JSON serialization
            serializable_results = self._make_json_serializable(all_results)
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Processing complete. Results saved to {output_path}")
        return all_results
    
    def _extract_chapter_number(self, chapter_key: str) -> int:
        """Extract chapter number from various chapter key formats"""
        import re
        
        # Look for numbers in the key
        match = re.search(r'\d+', str(chapter_key))
        return int(match.group()) if match else 1
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert numpy arrays and other non-serializable objects"""
        import numpy as np
        
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        else:
            return obj

async def main():
    """Main execution function"""
    
    print("🔮 Amharic Bible Embeddings Pipeline")
    print("====================================")
    print()
    
    # Check for input data
    raw_files = list(Path(RAW_DATA_DIR).glob("*"))
    if not any(f.suffix in ['.txt', '.json', '.csv'] for f in raw_files):
        print(f"❌ No Bible files found in {RAW_DATA_DIR}")
        print("Please add your Amharic Bible files (.txt, .json, or .csv) to the data/raw/ directory")
        return
    
    # Initialize processor
    processor = BibleProcessor()
    
    try:
        # Run the pipeline
        results = await processor.process_all_bible()
        
        print(f"✅ Processing complete!")
        print(f"📊 Processed {len(results)} chapters/books")
        print(f"💾 Results saved to {PROCESSED_DATA_DIR}/complete_bible_embeddings.json")
        
        # Print summary statistics
        total_chunks = sum(len(chapter_data["chunks"]) for chapter_data in results.values())
        print(f"📝 Total chunks created: {total_chunks}")
        print(f"🧠 Embedding model: {settings.EMBEDDING_MODEL}")
        print(f"🤖 LLM enhancement: {'Enabled' if settings.ENABLE_THEOLOGICAL_CONTEXT else 'Disabled'}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
