#!/usr/bin/env python3
"""
Streamlit web interface for Amharic Bible Q&A using embeddings
"""

import streamlit as st
import asyncio
import json
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings, PROCESSED_DATA_DIR
from src.enhancement.llm_contextualizer import llm_contextualizer

st.set_page_config(
    page_title="Amharic Bible Q&A",
    page_icon="📖",
    layout="wide"
)

def load_embeddings():
    """Load processed embeddings"""
    embeddings_file = PROCESSED_DATA_DIR / "complete_bible_embeddings.json"
    
    if not embeddings_file.exists():
        return None
    
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_similarity(query_embedding: np.ndarray, chunk_embedding: List[float]) -> float:
    """Calculate cosine similarity between query and chunk"""
    chunk_array = np.array(chunk_embedding)
    
    dot_product = np.dot(query_embedding, chunk_array)
    norm_query = np.linalg.norm(query_embedding)
    norm_chunk = np.linalg.norm(chunk_array)
    
    if norm_query == 0 or norm_chunk == 0:
        return 0.0
    
    return dot_product / (norm_query * norm_chunk)

async def search_bible(query: str, embeddings_data: Dict, top_k: int = 5) -> List[Dict]:
    """Search Bible using embeddings and return top matches"""
    
    # Generate query embedding
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    query_embedding = model.encode([query])[0]
    
    # Search through all chunks
    results = []
    
    for chapter_key, chapter_data in embeddings_data.items():
        for chunk in chapter_data["chunks"]:
            similarity = calculate_similarity(query_embedding, chunk["embedding"])
            
            results.append({
                "similarity": similarity,
                "text": chunk["text"],
                "book": chunk["book"],
                "chapter": chunk["chapter"],
                "verse_range": chunk["verse_range"],
                "context": chunk.get("context", ""),
                "chunk_id": chunk["chunk_id"]
            })
    
    # Sort by similarity and return top_k
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]

def main():
    """Main Streamlit application"""
    
    st.title("🇪🇹 Amharic Bible Q&A with Late Chunking")
    st.markdown("*Advanced semantic search using modern LLM enhancement and contextualized embeddings*")
    
    # Load embeddings
    with st.spinner("Loading Bible embeddings..."):
        embeddings_data = load_embeddings()
    
    if not embeddings_data:
        st.error("❌ No processed embeddings found!")
        st.info("Run `python scripts/process_bible.py` first to process your Bible data")
        return
    
    st.success(f"✅ Loaded {len(embeddings_data)} chapters/books")
    
    # Query interface
    st.header("🔍 Ask Questions About the Bible")
    
    query = st.text_input(
        "Enter your question (in Amharic or English):",
        placeholder="ኢየሱስ ምንድን ነው የተናገረው? or What did Jesus say about love?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("Search", type="primary")
    with col2:
        top_k = st.slider("Number of results", 3, 10, 5)
    
    if search_button and query:
        with st.spinner("Searching Bible..."):
            # Run async search
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(search_bible(query, embeddings_data, top_k))
            finally:
                loop.close()
        
        if results:
            st.header("📖 Search Results")
            
            for i, result in enumerate(results, 1):
                with st.expander(f"Result {i}: {result['book']} {result['chapter']} (Similarity: {result['similarity']:.3f})"):
                    
                    # Main verse text
                    st.markdown("**📜 Verse Text:**")
                    st.write(result['text'])
                    
                    # Context if available
                    if result['context']:
                        st.markdown("**🧠 AI-Generated Context:**")
                        st.info(result['context'])
                    
                    # Metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Book", result['book'])
                    with col2:
                        st.metric("Chapter", result['chapter'])
                    with col3:
                        st.metric("Verse Range", f"{result['verse_range'][0]}-{result['verse_range'][1]}")
        else:
            st.warning("No results found. Try a different query.")
    
    # Sidebar with project info
    with st.sidebar:
        st.header("ℹ️ Project Info")
        st.info("""
        This application uses:
        - **Late Chunking** for context preservation
        - **Modern LLMs** (Claude 4, Gemini Pro 2.5) for enhancement
        - **Multilingual embeddings** optimized for Amharic
        """)
        
        st.header("📊 Statistics")
        if embeddings_data:
            total_chunks = sum(len(chapter["chunks"]) for chapter in embeddings_data.values())
            st.metric("Total Chapters", len(embeddings_data))
            st.metric("Total Chunks", total_chunks)
            st.metric("Embedding Model", settings.EMBEDDING_MODEL.split("/")[-1])
        
        st.header("🔧 Configuration")
        st.code(f"""
Embedding Model: {settings.EMBEDDING_MODEL}
LLM Enhancement: {settings.CONTEXT_ENHANCEMENT_LLM}
Vector DB: {settings.VECTOR_DB_TYPE}
Chunk Size: {settings.CHUNK_SIZE}
        """)

if __name__ == "__main__":
    main()
