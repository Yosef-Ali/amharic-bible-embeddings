"""
ChromaDB Vector Database Manager for Amharic Bible Embeddings
"""

import chromadb
from chromadb.config import Settings
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ChromaBibleDB:
    """ChromaDB manager for Amharic Bible embeddings with late chunking"""
    
    def __init__(self, persist_directory: str = "./data/embeddings/chroma_db"):
        """
        Initialize ChromaDB client
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Collection for bible embeddings
        self.collection_name = "amharic_bible_late_chunking"
        self.collection = None
        
    def create_collection(self, reset: bool = False) -> None:
        """Create or get the bible collection"""
        
        try:
            if reset and self.collection_name in [c.name for c in self.client.list_collections()]:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Reset collection: {self.collection_name}")
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Amharic Bible with Late Chunking Embeddings",
                    "embedding_model": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
                    "chunking_method": "late_chunking",
                    "language": "amharic",
                    "bible_version": "Catholic Edition"
                }
            )
            
            logger.info(f"Collection ready: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def add_bible_chunks(self, chunks_file: str) -> Dict[str, Any]:
        """
        Add late-chunked bible embeddings to the vector database
        """
        
        if not self.collection:
            self.create_collection()
        
        # Load chunks
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = [json.loads(line) for line in f]
        
        logger.info(f"Loading {len(chunks)} chunks into ChromaDB")
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            # Create unique ID
            chunk_id = f"chunk_{chunk['id']:05d}"
            ids.append(chunk_id)
            
            # Extract embedding
            embedding = chunk['embedding']
            if isinstance(embedding, list):
                embedding = np.array(embedding)
            embeddings.append(embedding.tolist())
            
            # Document text
            documents.append(chunk['text'])
            
            # Rich metadata for filtering and retrieval
            books = [chunk['book']] if isinstance(chunk['book'], str) else chunk.get('books', [])
            
            metadata = {
                'chunk_id': chunk['id'],
                'passage_id': chunk.get('passage_id', 0),
                'books': json.dumps(books),  # Store as JSON string
                'word_count': chunk.get('character_count', len(chunk['text'])),
                'sentence_count': chunk.get('paragraph_count', 0),
                'testament': 'old' if any('ኦሪት' in book or 'መጽሐፀ' in book or 'ትንቢተ' in book 
                                        for book in books) else 'new',
                'biblical_context': chunk.get('enhanced_context', {}).get('biblical_context', '')[:500],  # Truncate
                'theological_themes': chunk.get('enhanced_context', {}).get('theological_themes', '')[:500]
            }
            metadatas.append(metadata)
        
        # Add to ChromaDB in batches
        batch_size = 500
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))
            
            self.collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
            
            logger.info(f"Added batch {i//batch_size + 1}: {end_idx - i} chunks")
        
        # Get collection stats
        stats = {
            'total_chunks': self.collection.count(),
            'collection_name': self.collection_name,
            'embedding_dimension': len(embeddings[0]) if embeddings else 0,
            'books_covered': len(set([chunk['book'] for chunk in chunks if 'book' in chunk])),
            'persist_directory': str(self.persist_directory)
        }
        
        logger.info(f"ChromaDB populated: {stats['total_chunks']} chunks")
        return stats
    
    def semantic_search(self, 
                       query: str, 
                       n_results: int = 5,
                       book_filter: Optional[List[str]] = None,
                       testament_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Semantic search across the bible collection
        """
        
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_collection() first.")
        
        # Build where clause for filtering
        where_clause = {}
        if testament_filter:
            where_clause['testament'] = testament_filter
        
        # If book filter is provided, we'll need to post-process since Chroma doesn't support complex JSON queries
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            result = {
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                'books': json.loads(results['metadatas'][0][i]['books'])
            }
            
            # Apply book filter if provided
            if book_filter:
                if not any(book in result['books'] for book in book_filter):
                    continue
            
            formatted_results.append(result)
        
        return formatted_results[:n_results]  # Ensure we return requested number
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get comprehensive collection statistics"""
        
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            count = self.collection.count()
            
            # Sample some chunks to analyze
            sample_results = self.collection.peek(limit=100)
            
            # Analyze testament distribution
            testament_counts = {'old': 0, 'new': 0}
            for metadata in sample_results['metadatas']:
                testament_counts[metadata.get('testament', 'unknown')] += 1
            
            stats = {
                'total_chunks': count,
                'collection_name': self.collection_name,
                'testament_distribution': testament_counts,
                'sample_books': list(set([
                    json.loads(metadata['books'])[0] if json.loads(metadata['books']) else 'Unknown'
                    for metadata in sample_results['metadatas'][:10]
                ])),
                'persist_directory': str(self.persist_directory)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

def main():
    """Initialize ChromaDB with bible embeddings"""
    
    db = ChromaBibleDB()
    
    # Create collection
    db.create_collection(reset=True)
    
    # Use production embeddings with all 1,827 chunks
    chunks_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/embeddings/production_embeddings.jsonl"
    
    if Path(chunks_file).exists():
        # Add bible chunks
        stats = db.add_bible_chunks(chunks_file)
        
        print("ChromaDB Setup Complete:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Test search
        print("\nTesting semantic search:")
        results = db.semantic_search("ፍቅር", n_results=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. Books: {result['books']}, Similarity: {result['similarity']:.3f}")
            print(f"     Text: {result['document'][:100]}...")
    else:
        print(f"Chunks file not found: {chunks_file}")
        print("Please run the late chunking embedder first.")

if __name__ == "__main__":
    main()