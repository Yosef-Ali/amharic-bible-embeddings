"""
Bible Search Tool for Catholic Teaching Assistant MCP Server
Uses existing Amharic Bible embeddings for semantic search
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import settings, EMBEDDINGS_DIR

class BibleSearchTool:
    """MCP tool for searching the Amharic Bible using embeddings"""
    
    def __init__(self):
        self.model = None
        self.embeddings_data = None
        self._load_embeddings()
    
    def _load_embeddings(self):
        """Load the structured Bible embeddings"""
        
        # Try to load the structured embeddings
        embeddings_file = Path("data/embeddings/fixed_structured_embeddings.jsonl")
        
        if embeddings_file.exists():
            print(f"Loading Bible embeddings from: {embeddings_file}")
            
            self.embeddings_data = {"chunks": []}
            with open(embeddings_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.embeddings_data["chunks"].append(json.loads(line))
            
            print(f"Loaded {len(self.embeddings_data['chunks'])} Bible verses")
        else:
            print(f"❌ Bible embeddings not found: {embeddings_file}")
            self.embeddings_data = None
    
    def _get_model(self):
        """Lazy load the embedding model"""
        if self.model is None:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self.model
    
    def _calculate_similarity(self, query_embedding: np.ndarray, verse_embedding: List[float]) -> float:
        """Calculate cosine similarity between query and verse"""
        
        verse_array = np.array(verse_embedding)
        
        dot_product = np.dot(query_embedding, verse_array)
        norm_query = np.linalg.norm(query_embedding)
        norm_verse = np.linalg.norm(verse_array)
        
        if norm_query == 0 or norm_verse == 0:
            return 0.0
        
        return float(dot_product / (norm_query * norm_verse))
    
    async def search(self, 
                    query: str, 
                    max_results: int = 5,
                    min_similarity: float = 0.3,
                    book_filter: Optional[List[str]] = None,
                    testament_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Search the Bible for passages related to the query
        
        Args:
            query: Search question in Amharic or English
            max_results: Maximum number of results to return
            min_similarity: Minimum similarity score (0.0-1.0)
            book_filter: Optional list of book names to filter by
            testament_filter: Optional testament filter ('old' or 'new')
        
        Returns:
            Dictionary with search results and metadata
        """
        
        if not self.embeddings_data:
            return {
                "error": "Bible embeddings not available",
                "results": [],
                "query": query,
                "success": False
            }
        
        try:
            # Generate query embedding
            model = self._get_model()
            query_embedding = model.encode([query])[0]
            
            # Search through all verses
            results = []
            chunks = self.embeddings_data["chunks"]
            
            for chunk in chunks:
                # Apply filters if specified
                if book_filter and chunk.get("book") not in book_filter:
                    continue
                
                if testament_filter and chunk.get("testament") != testament_filter:
                    continue
                
                # Calculate similarity
                if "embedding" in chunk:
                    similarity = self._calculate_similarity(query_embedding, chunk["embedding"])
                    
                    if similarity >= min_similarity:
                        results.append({
                            "similarity": similarity,
                            "book": chunk.get("book", "Unknown"),
                            "chapter": chunk.get("chapter", 0),
                            "verse_number": chunk.get("verse_number", 0),
                            "verse_range": chunk.get("verse_range", [0, 0]),
                            "text": chunk.get("text", ""),
                            "testament": chunk.get("testament", "unknown"),
                            "word_count": chunk.get("word_count", 0),
                            "passage_id": chunk.get("id", 0)
                        })
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:max_results]
            
            # Calculate statistics
            unique_books = len(set(r["book"] for r in results))
            testaments = set(r["testament"] for r in results)
            
            return {
                "query": query,
                "results": results,
                "statistics": {
                    "total_matches": len(results),
                    "unique_books": unique_books,
                    "testaments_found": list(testaments),
                    "avg_similarity": np.mean([r["similarity"] for r in results]) if results else 0,
                    "best_similarity": max([r["similarity"] for r in results]) if results else 0
                },
                "search_params": {
                    "max_results": max_results,
                    "min_similarity": min_similarity,
                    "book_filter": book_filter,
                    "testament_filter": testament_filter
                },
                "success": True
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "results": [],
                "query": query,
                "success": False
            }
    
    async def get_verse_context(self, book: str, chapter: int, verse: int) -> Dict[str, Any]:
        """Get contextual information about a specific verse"""
        
        if not self.embeddings_data:
            return {"error": "Bible data not available"}
        
        # Find the specific verse
        for chunk in self.embeddings_data["chunks"]:
            if (chunk.get("book") == book and 
                chunk.get("chapter") == chapter and
                chunk.get("verse_number") == verse):
                
                return {
                    "verse": chunk,
                    "book_info": {
                        "name": book,
                        "testament": chunk.get("testament", "unknown")
                    },
                    "chapter_info": {
                        "number": chapter,
                        "verse_count": "unknown"  # Could calculate if needed
                    }
                }
        
        return {"error": f"Verse not found: {book} {chapter}:{verse}"}
    
    async def search_by_theme(self, theme: str, testament: Optional[str] = None) -> Dict[str, Any]:
        """Search for verses by thematic keywords"""
        
        # Common biblical themes in Amharic and English
        theme_queries = {
            "love": ["ፍቅር", "love", "agape"],
            "peace": ["ሰላም", "peace", "shalom"], 
            "forgiveness": ["ይቅር", "forgiveness", "mercy"],
            "faith": ["እምነት", "faith", "believe"],
            "hope": ["ተስፋ", "hope"],
            "salvation": ["መዳን", "salvation", "save"],
            "prayer": ["ጸሎት", "prayer", "pray"],
            "grace": ["ጸጋ", "grace", "favor"]
        }
        
        queries = theme_queries.get(theme.lower(), [theme])
        all_results = []
        
        for query in queries:
            search_result = await self.search(
                query=query,
                max_results=3,
                min_similarity=0.4,
                testament_filter=testament
            )
            
            if search_result["success"]:
                all_results.extend(search_result["results"])
        
        # Remove duplicates and sort by similarity
        seen_ids = set()
        unique_results = []
        
        for result in all_results:
            passage_id = result["passage_id"]
            if passage_id not in seen_ids:
                seen_ids.add(passage_id)
                unique_results.append(result)
        
        unique_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return {
            "theme": theme,
            "results": unique_results[:10],  # Top 10 unique results
            "total_found": len(unique_results),
            "success": True
        }