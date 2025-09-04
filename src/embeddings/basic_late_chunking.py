"""
Basic Late Chunking Implementation - Core Logic Only
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import sys
sys.path.append('/Users/mekdesyared/Embedding/amharic-bible-embeddings')
import logging

logger = logging.getLogger(__name__)

class BasicLateChunkingEmbedder:
    """Basic late chunking without LLM enhancement for testing"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name, device="cpu")
        self.long_passage_size = 800     # Words per long passage
        self.final_chunk_size = 250      # Words per final chunk
        self.overlap_ratio = 0.10        # 10% overlap
        
    def count_amharic_words(self, text: str) -> int:
        """Count words in Amharic text"""
        import re
        amharic_words = re.findall(r'[\u1200-\u137f]+', text)
        return len(amharic_words)
    
    def create_long_passages(self, book_chunks: List[Dict]) -> List[Dict]:
        """Create long passages from book chunks"""
        
        enhanced_passages = []
        current_passage = []
        current_word_count = 0
        passage_id = 1
        
        for chunk in book_chunks:
            chunk_text = chunk['text']
            chunk_words = self.count_amharic_words(chunk_text)
            
            if current_word_count + chunk_words > self.long_passage_size and current_passage:
                # Create long passage
                combined_text = '\n\n'.join([c['text'] for c in current_passage])
                
                enhanced_passages.append({
                    'passage_id': passage_id,
                    'books': list(set([c.get('book', 'Unknown') for c in current_passage])),
                    'word_count': current_word_count,
                    'enhanced_text': combined_text,
                    'source_chunk_ids': [c.get('id', i) for i, c in enumerate(current_passage)]
                })
                
                passage_id += 1
                current_passage = [chunk]
                current_word_count = chunk_words
            else:
                current_passage.append(chunk)
                current_word_count += chunk_words
        
        # Final passage
        if current_passage:
            combined_text = '\n\n'.join([c['text'] for c in current_passage])
            enhanced_passages.append({
                'passage_id': passage_id,
                'books': list(set([c.get('book', 'Unknown') for c in current_passage])),
                'word_count': current_word_count,
                'enhanced_text': combined_text,
                'source_chunk_ids': [c.get('id', i) for i, c in enumerate(current_passage)]
            })
        
        return enhanced_passages
    
    def generate_embeddings(self, passages: List[Dict]) -> List[Dict]:
        """Generate embeddings for long passages"""
        
        texts = [p['enhanced_text'] for p in passages]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        for i, passage in enumerate(passages):
            passage['embedding'] = embeddings[i].tolist()
            passage['embedding_dimension'] = len(embeddings[i])
        
        return passages
    
    def apply_chunking(self, embedded_passages: List[Dict]) -> List[Dict]:
        """Apply final chunking with embedding pooling"""
        
        final_chunks = []
        chunk_id = 1
        
        for passage in embedded_passages:
            text = passage['enhanced_text']
            embedding = np.array(passage['embedding'])
            
            # Simple sentence-based chunking
            sentences = self._split_sentences(text)
            
            current_chunk = []
            current_words = 0
            
            for sentence in sentences:
                sentence_words = self.count_amharic_words(sentence)
                
                if current_words + sentence_words > self.final_chunk_size and current_chunk:
                    # Create final chunk
                    chunk_text = ' '.join(current_chunk)
                    
                    final_chunks.append({
                        'chunk_id': chunk_id,
                        'passage_id': passage['passage_id'],
                        'books': passage['books'],
                        'text': chunk_text,
                        'word_count': current_words,
                        'embedding': embedding.tolist(),  # Use passage embedding
                        'metadata': {
                            'source_chunks': passage['source_chunk_ids'],
                            'embedding_dimension': len(embedding)
                        }
                    })
                    
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    overlap_size = max(1, int(len(current_chunk) * self.overlap_ratio))
                    current_chunk = current_chunk[-overlap_size:] + [sentence]
                    current_words = sum(self.count_amharic_words(s) for s in current_chunk)
                else:
                    current_chunk.append(sentence)
                    current_words += sentence_words
            
            # Final chunk for passage
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                final_chunks.append({
                    'chunk_id': chunk_id,
                    'passage_id': passage['passage_id'],
                    'books': passage['books'],
                    'text': chunk_text,
                    'word_count': current_words,
                    'embedding': embedding.tolist(),
                    'metadata': {
                        'source_chunks': passage['source_chunk_ids'],
                        'embedding_dimension': len(embedding)
                    }
                })
                chunk_id += 1
        
        return final_chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split into sentences"""
        import re
        sentences = re.split(r'[።፧፡]', text)
        return [s.strip() for s in sentences if len(s.strip()) > 5]
    
    def process(self, input_file: str, output_dir: str) -> Dict[str, Any]:
        """Complete basic late chunking process"""
        
        # Load chunks
        with open(input_file, 'r', encoding='utf-8') as f:
            chunks = [json.loads(line) for line in f]
        
        print(f"Loaded {len(chunks)} chunks")
        
        # Create long passages
        passages = self.create_long_passages(chunks)
        print(f"Created {len(passages)} long passages")
        
        # Generate embeddings
        embedded_passages = self.generate_embeddings(passages)
        print(f"Generated embeddings for {len(embedded_passages)} passages")
        
        # Apply final chunking
        final_chunks = self.apply_chunking(embedded_passages)
        print(f"Created {len(final_chunks)} final chunks")
        
        # Save results
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path / "basic_late_chunks.jsonl", 'w', encoding='utf-8') as f:
            for chunk in final_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        summary = {
            'input_chunks': len(chunks),
            'long_passages': len(passages),
            'final_chunks': len(final_chunks),
            'avg_words_per_chunk': np.mean([c['word_count'] for c in final_chunks]),
            'books_covered': len(set([book for chunk in final_chunks for book in chunk['books']])),
        }
        
        return summary

def main():
    embedder = BasicLateChunkingEmbedder()
    
    input_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/complete_extraction/complete_bible_chunks.jsonl"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/embeddings"
    
    result = embedder.process(input_file, output_dir)
    
    print("\nBasic Late Chunking Results:")
    for key, value in result.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()