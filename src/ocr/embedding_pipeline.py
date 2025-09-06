#!/usr/bin/env python3
"""
OCR to Embeddings Pipeline
Convert scanned book pages to text embeddings for search and retrieval
Handles complex layouts and maintains document structure
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from datetime import datetime

class EmbeddingPipeline:
    """
    Pipeline to convert OCR results to structured embeddings
    Optimized for complex book layouts and non-sequential pages
    """
    
    def __init__(self):
        """Initialize embedding pipeline"""
        self.chunk_size = 500  # Characters per chunk
        self.overlap = 50      # Character overlap between chunks
        
    def process_ocr_results(self, ocr_json_path: str) -> Dict[str, Any]:
        """
        Process OCR results and prepare for embedding generation
        """
        
        with open(ocr_json_path, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        # Extract text chunks maintaining structure
        structured_chunks = self._extract_structured_chunks(ocr_data)
        
        # Generate metadata for each chunk
        embedding_data = self._prepare_embedding_data(structured_chunks, ocr_data)
        
        return embedding_data
    
    def _extract_structured_chunks(self, ocr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract text chunks while preserving document structure
        """
        
        chunks = []
        book_results = ocr_data.get("book_scan_results", {})
        pages = book_results.get("pages", [])
        
        for page in pages:
            page_chunks = self._process_page_for_chunks(page)
            chunks.extend(page_chunks)
        
        return chunks
    
    def _process_page_for_chunks(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a single page and create chunks
        """
        
        chunks = []
        text_blocks = page_data.get("text_blocks", [])
        
        # Combine text blocks in reading order
        page_text = ""
        block_positions = []
        
        for block in sorted(text_blocks, key=lambda b: b.get("reading_order", 0)):
            block_text = block.get("text", "")
            if block_text and not block_text.startswith("[Text block"):  # Skip placeholders
                start_pos = len(page_text)
                page_text += block_text + " "
                end_pos = len(page_text)
                
                block_positions.append({
                    "block_id": block.get("block_id"),
                    "start": start_pos,
                    "end": end_pos,
                    "bbox": block.get("bbox"),
                    "region": block.get("region")
                })
        
        # Create overlapping chunks from page text
        if page_text.strip():
            page_chunks = self._create_overlapping_chunks(
                page_text, 
                page_data, 
                block_positions
            )
            chunks.extend(page_chunks)
        
        return chunks
    
    def _create_overlapping_chunks(self, text: str, page_data: Dict[str, Any], block_positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create overlapping text chunks for better embedding coverage
        """
        
        chunks = []
        text_length = len(text)
        
        start = 0
        chunk_id = 1
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at word boundary
            if end < text_length:
                # Find last space before end position
                last_space = text.rfind(' ', start, end)
                if last_space > start + self.chunk_size * 0.5:  # Don't make chunks too small
                    end = last_space
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                # Find which blocks this chunk spans
                spanning_blocks = self._find_spanning_blocks(start, end, block_positions)
                
                chunk = {
                    "chunk_id": f"page_{page_data.get('page_number', 0)}_chunk_{chunk_id}",
                    "text": chunk_text,
                    "page_number": page_data.get("page_number"),
                    "filename": page_data.get("filename"),
                    "layout_type": page_data.get("layout", {}).get("layout_type"),
                    "char_start": start,
                    "char_end": end,
                    "spanning_blocks": spanning_blocks,
                    "chunk_length": len(chunk_text),
                    "hash": hashlib.md5(chunk_text.encode('utf-8')).hexdigest()
                }
                
                chunks.append(chunk)
                chunk_id += 1
            
            # Move start position with overlap
            start = max(start + 1, end - self.overlap)
        
        return chunks
    
    def _find_spanning_blocks(self, start: int, end: int, block_positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find which text blocks a chunk spans across
        """
        
        spanning = []
        
        for block in block_positions:
            block_start = block["start"]
            block_end = block["end"]
            
            # Check if chunk overlaps with this block
            if not (end <= block_start or start >= block_end):
                # Calculate overlap
                overlap_start = max(start, block_start)
                overlap_end = min(end, block_end)
                overlap_length = overlap_end - overlap_start
                
                if overlap_length > 0:
                    spanning.append({
                        "block_id": block["block_id"],
                        "region": block["region"],
                        "bbox": block["bbox"],
                        "overlap_chars": overlap_length,
                        "overlap_ratio": overlap_length / (block_end - block_start)
                    })
        
        return spanning
    
    def _prepare_embedding_data(self, chunks: List[Dict[str, Any]], ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare final data structure for embedding generation
        """
        
        # Add global metadata
        metadata = ocr_data.get("metadata", {})
        
        embedding_data = {
            "embedding_pipeline": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "chunk_size": self.chunk_size,
                "overlap": self.overlap
            },
            "source_metadata": metadata,
            "chunks": chunks,
            "statistics": {
                "total_chunks": len(chunks),
                "total_characters": sum(c["chunk_length"] for c in chunks),
                "average_chunk_length": sum(c["chunk_length"] for c in chunks) / len(chunks) if chunks else 0,
                "pages_processed": len(set(c["page_number"] for c in chunks if c.get("page_number"))),
                "layout_distribution": self._get_layout_distribution(chunks)
            }
        }
        
        return embedding_data
    
    def _get_layout_distribution(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get distribution of chunks by layout type
        """
        
        distribution = {}
        for chunk in chunks:
            layout = chunk.get("layout_type", "unknown")
            distribution[layout] = distribution.get(layout, 0) + 1
        
        return distribution
    
    def save_embedding_ready_data(self, embedding_data: Dict[str, Any], output_path: str):
        """
        Save data in format ready for embedding generation
        """
        
        # Create main embedding file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(embedding_data, f, indent=2, ensure_ascii=False)
        
        # Create simple text file for quick processing
        text_output_path = output_path.replace('.json', '_texts.txt')
        with open(text_output_path, 'w', encoding='utf-8') as f:
            for chunk in embedding_data["chunks"]:
                f.write(f"=== {chunk['chunk_id']} ===\n")
                f.write(f"{chunk['text']}\n\n")
        
        # Create metadata file
        meta_output_path = output_path.replace('.json', '_metadata.json')
        metadata = {
            "pipeline_info": embedding_data["embedding_pipeline"],
            "statistics": embedding_data["statistics"],
            "source_metadata": embedding_data["source_metadata"]
        }
        
        with open(meta_output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Embedding-ready data saved:")
        print(f"   📄 Main data: {output_path}")
        print(f"   📝 Text only: {text_output_path}")
        print(f"   📊 Metadata: {meta_output_path}")
    
    def create_embeddings_from_book(self, image_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        Complete pipeline: OCR → Text Extraction → Embedding Preparation
        """
        
        from .document_scanner import DocumentScanner
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Step 1: OCR Processing
        print("🔍 Step 1: OCR Processing...")
        scanner = DocumentScanner()
        ocr_output = output_dir / "book_ocr_results.json"
        ocr_data = scanner.process_book_batch(image_dir, str(ocr_output))
        
        # Step 2: Text Extraction and Chunking
        print("📝 Step 2: Text Extraction and Chunking...")
        embedding_data = self.process_ocr_results(str(ocr_output))
        
        # Step 3: Save Embedding-Ready Data
        print("💾 Step 3: Saving Embedding-Ready Data...")
        embedding_output = output_dir / "book_embeddings_ready.json"
        self.save_embedding_ready_data(embedding_data, str(embedding_output))
        
        return {
            "ocr_results": str(ocr_output),
            "embedding_data": str(embedding_output),
            "statistics": embedding_data["statistics"],
            "success": True
        }

def test_embedding_pipeline():
    """
    Test the embedding pipeline
    """
    
    print("🔄 OCR to Embeddings Pipeline")
    print("=" * 40)
    
    pipeline = EmbeddingPipeline()
    
    print("✅ Pipeline Features:")
    print(f"  📏 Chunk size: {pipeline.chunk_size} characters")
    print(f"  🔄 Overlap: {pipeline.overlap} characters")
    print("  📖 Maintains reading order")
    print("  🏷️  Preserves block metadata")
    print("  📊 Generates statistics")
    print()
    
    print("🎯 Perfect for:")
    print("  📚 Complex book layouts")
    print("  🔤 Amharic text embeddings")
    print("  📄 Non-sequential pages")
    print("  🔍 Semantic search preparation")
    print("  💾 Embedding model training")
    print()
    
    print("💡 Usage:")
    print("  # Complete pipeline")
    print("  result = pipeline.create_embeddings_from_book(")
    print("      'book_images/', 'output/')")
    print()
    print("  # Process existing OCR results")
    print("  embedding_data = pipeline.process_ocr_results('ocr.json')")
    print()
    
    print("📤 Output Files:")
    print("  📄 book_embeddings_ready.json - Full embedding data")
    print("  📝 book_embeddings_ready_texts.txt - Text only")
    print("  📊 book_embeddings_ready_metadata.json - Statistics")

if __name__ == "__main__":
    test_embedding_pipeline()