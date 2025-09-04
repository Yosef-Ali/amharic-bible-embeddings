"""
Simple but effective chunking for Amharic Bible text
"""

import re
import json
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class AmharicBibleChunker:
    """Create meaningful chunks from Amharic Bible text for embeddings"""
    
    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size  # Target words per chunk
        self.overlap = overlap        # Words to overlap between chunks
        
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using Amharic punctuation"""
        
        # Split by Amharic sentence endings
        sentences = re.split(r'[።፤፧]\s*', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and any(c.isalpha() for c in sentence):
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def count_amharic_words(self, text: str) -> int:
        """Count words in Amharic text"""
        # Split by whitespace and count non-empty tokens
        words = [w for w in text.split() if w.strip()]
        return len(words)
    
    def create_semantic_chunks(self, text: str) -> List[Dict]:
        """Create chunks that preserve semantic meaning"""
        
        sentences = self.split_into_sentences(text)
        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_id = 1
        
        for i, sentence in enumerate(sentences):
            sentence_words = self.count_amharic_words(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_word_count + sentence_words > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'word_count': current_word_count,
                    'sentence_count': len(current_chunk),
                    'start_sentence': i - len(current_chunk),
                    'end_sentence': i - 1
                })
                
                chunk_id += 1
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_word_count = sum(self.count_amharic_words(s) for s in current_chunk)
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_word_count += sentence_words
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'word_count': current_word_count,
                'sentence_count': len(current_chunk),
                'start_sentence': len(sentences) - len(current_chunk),
                'end_sentence': len(sentences) - 1
            })
        
        return chunks
    
    def add_context_metadata(self, chunks: List[Dict], source_file: str) -> List[Dict]:
        """Add contextual metadata to chunks"""
        
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Add neighboring context information
            prev_chunk = chunks[i-1] if i > 0 else None
            next_chunk = chunks[i+1] if i < len(chunks) - 1 else None
            
            enhanced_chunk = chunk.copy()
            enhanced_chunk.update({
                'source_file': source_file,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'has_previous': prev_chunk is not None,
                'has_next': next_chunk is not None,
                'context_window': {
                    'previous_text': prev_chunk['text'][-100:] if prev_chunk else None,
                    'next_text': next_chunk['text'][:100] if next_chunk else None
                }
            })
            
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def process_bible_text(self, input_file: str, output_dir: str) -> Dict:
        """Process Bible text into chunks for embedding"""
        
        # Read input
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f"Processing {len(text)} characters into chunks")
        
        # Create chunks
        chunks = self.create_semantic_chunks(text)
        
        # Add metadata
        enhanced_chunks = self.add_context_metadata(chunks, input_file)
        
        # Save results
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save chunks as JSONL for embedding pipeline
        chunks_file = output_path / "amharic_bible_chunks.jsonl"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            for chunk in enhanced_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        # Save summary
        summary_file = output_path / "chunking_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            avg_words = sum(c['word_count'] for c in chunks) / len(chunks)
            avg_sentences = sum(c['sentence_count'] for c in chunks) / len(chunks)
            
            f.write("Amharic Bible Chunking Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total chunks created: {len(chunks)}\n")
            f.write(f"Average words per chunk: {avg_words:.1f}\n")
            f.write(f"Average sentences per chunk: {avg_sentences:.1f}\n")
            f.write(f"Target chunk size: {self.chunk_size} words\n")
            f.write(f"Overlap size: {self.overlap} words\n")
            f.write(f"Original text length: {len(text):,} characters\n\n")
            
            # Sample chunks
            f.write("Sample chunks:\n")
            for i in range(min(5, len(chunks))):
                f.write(f"\nChunk {i+1}:\n")
                f.write(f"  Words: {chunks[i]['word_count']}\n")
                f.write(f"  Text preview: {chunks[i]['text'][:200]}...\n")
        
        return {
            'total_chunks': len(chunks),
            'chunks_file': str(chunks_file),
            'summary_file': str(summary_file),
            'average_words': avg_words,
            'average_sentences': avg_sentences
        }

def main():
    """Create chunks for embedding"""
    chunker = AmharicBibleChunker(chunk_size=300, overlap=50)
    
    input_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/processed/amharic_bible_cleaned.txt"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/chunks"
    
    result = chunker.process_bible_text(input_file, output_dir)
    
    print("Bible Chunking Complete:")
    for key, value in result.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()