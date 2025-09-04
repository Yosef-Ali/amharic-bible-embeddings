"""
Production-scale embedding processor for all 1,827 bible chunks
"""
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import sys
sys.path.append('/Users/mekdesyared/Embedding/amharic-bible-embeddings')
import logging

logger = logging.getLogger(__name__)

class ProductionEmbedder:
    """Process all 1,827 chunks with embeddings"""
    
    def __init__(self):
        # Use faster, smaller model for production
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        
    def process_all_chunks(self, input_file: str, output_file: str, batch_size: int = 50):
        """Process all chunks with embeddings"""
        
        print("🔄 Processing ALL 1,827 chunks for production embeddings...")
        
        # Load all chunks
        with open(input_file, 'r', encoding='utf-8') as f:
            chunks = [json.loads(line) for line in f]
        
        print(f"📊 Loaded {len(chunks)} chunks from {len(set(c['book'] for c in chunks))} books")
        
        # Process in batches to manage memory
        processed_chunks = []
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_texts = [chunk['text'] for chunk in batch_chunks]
            
            print(f"   Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")
            
            # Generate embeddings
            embeddings = self.model.encode(batch_texts, show_progress_bar=False)
            
            # Add embeddings to chunks
            for j, chunk in enumerate(batch_chunks):
                chunk['embedding'] = embeddings[j].tolist()
                chunk['embedding_dimension'] = len(embeddings[j])
                processed_chunks.append(chunk)
        
        # Save all embedded chunks
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for chunk in processed_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        # Analysis
        books_covered = set(chunk['book'] for chunk in processed_chunks)
        
        summary = {
            'total_chunks_processed': len(processed_chunks),
            'books_covered': len(books_covered),
            'embedding_dimension': processed_chunks[0]['embedding_dimension'],
            'output_file': str(output_path),
            'sample_books': sorted(list(books_covered))[:10]
        }
        
        print(f"✅ Production embedding complete!")
        print(f"   📝 Chunks: {summary['total_chunks_processed']}")
        print(f"   📚 Books: {summary['books_covered']}")
        print(f"   🧮 Dimension: {summary['embedding_dimension']}")
        
        return summary

def main():
    embedder = ProductionEmbedder()
    
    input_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/complete_extraction/complete_bible_chunks.jsonl"
    output_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/embeddings/production_embeddings.jsonl"
    
    result = embedder.process_all_chunks(input_file, output_file)
    
    print(f"\n🎯 Ready for ChromaDB with {result['total_chunks_processed']} embedded chunks!")

if __name__ == "__main__":
    main()