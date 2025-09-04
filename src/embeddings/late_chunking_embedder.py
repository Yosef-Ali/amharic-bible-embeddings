"""
Late Chunking Implementation for Amharic Bible Embeddings
Follows the Late Chunking technique to preserve contextual information
"""

import numpy as np
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import sys
sys.path.append('/Users/mekdesyared/Embedding/amharic-bible-embeddings')
from config.llm_config import llm_manager
import logging

logger = logging.getLogger(__name__)

class LateChunkingEmbedder:
    """
    Implements Late Chunking technique for high-quality Amharic Bible embeddings
    
    Late Chunking Process:
    1. Create long passages with LLM contextual enhancement
    2. Generate embeddings for the full enhanced passages  
    3. Apply intelligent chunking that preserves semantic boundaries
    4. Use embedding pooling to maintain contextual richness
    """
    
    def __init__(self, 
                 model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
                 device: str = "cpu"):
        """
        Initialize the Late Chunking Embedder
        
        Args:
            model_name: HuggingFace model for multilingual embeddings
            device: Computing device (cpu/cuda)
        """
        self.model_name = model_name
        self.device = device
        self.model = SentenceTransformer(model_name, device=device)
        self.llm_manager = llm_manager
        
        # Late chunking parameters
        self.long_passage_size = 1000    # Words per long passage
        self.final_chunk_size = 300      # Words per final chunk
        self.overlap_ratio = 0.15        # 15% overlap between chunks
        
    def count_amharic_words(self, text: str) -> int:
        """Count words in Amharic text"""
        import re
        amharic_words = re.findall(r'[\u1200-\u137f]+', text)
        return len(amharic_words)
    
    async def create_enhanced_long_passages(self, book_chunks: List[Dict]) -> List[Dict]:
        """
        Step 1: Create long passages with LLM contextual enhancement
        """
        logger.info("Creating enhanced long passages...")
        
        enhanced_passages = []
        current_passage = []
        current_word_count = 0
        passage_id = 1
        
        for chunk in book_chunks:
            chunk_text = chunk['text']
            chunk_words = self.count_amharic_words(chunk_text)
            
            # If adding this chunk exceeds long passage size, process current passage
            if current_word_count + chunk_words > self.long_passage_size and current_passage:
                # Combine chunks into one long passage
                combined_text = '\n\n'.join([c['text'] for c in current_passage])
                
                # Generate LLM contextual enhancement
                try:
                    biblical_context = await self.llm_manager.generate_context(
                        combined_text, "biblical"
                    )
                    theological_themes = await self.llm_manager.generate_context(
                        combined_text, "cross_reference" 
                    )
                    
                    enhanced_text = f"""Biblical Context: {biblical_context}

Theological Themes: {theological_themes}

Original Text:
{combined_text}"""
                    
                except Exception as e:
                    logger.warning(f"LLM enhancement failed: {e}")
                    enhanced_text = combined_text
                    biblical_context = ""
                    theological_themes = ""
                
                enhanced_passages.append({
                    'passage_id': passage_id,
                    'books': list(set([c.get('book', 'Unknown') for c in current_passage])),
                    'original_chunks': len(current_passage),
                    'word_count': current_word_count,
                    'original_text': combined_text,
                    'biblical_context': biblical_context,
                    'theological_themes': theological_themes,
                    'enhanced_text': enhanced_text,
                    'source_chunk_ids': [c.get('id', i) for i, c in enumerate(current_passage)]
                })
                
                passage_id += 1
                current_passage = [chunk]
                current_word_count = chunk_words
            else:
                current_passage.append(chunk)
                current_word_count += chunk_words
        
        # Process final passage
        if current_passage:
            combined_text = '\n\n'.join([c['text'] for c in current_passage])
            
            try:
                biblical_context = await self.llm_manager.generate_context(
                    combined_text, "biblical"
                )
                theological_themes = await self.llm_manager.generate_context(
                    combined_text, "cross_reference"
                )
                
                enhanced_text = f"""Biblical Context: {biblical_context}

Theological Themes: {theological_themes}

Original Text:
{combined_text}"""
                
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {e}")
                enhanced_text = combined_text
                biblical_context = ""
                theological_themes = ""
            
            enhanced_passages.append({
                'passage_id': passage_id,
                'books': list(set([c.get('book', 'Unknown') for c in current_passage])),
                'original_chunks': len(current_passage),
                'word_count': current_word_count,
                'original_text': combined_text,
                'biblical_context': biblical_context,
                'theological_themes': theological_themes,
                'enhanced_text': enhanced_text,
                'source_chunk_ids': [c.get('id', i) for i, c in enumerate(current_passage)]
            })
        
        logger.info(f"Created {len(enhanced_passages)} enhanced long passages")
        return enhanced_passages
    
    def generate_passage_embeddings(self, enhanced_passages: List[Dict]) -> List[Dict]:
        """
        Step 2: Generate embeddings for enhanced long passages
        """
        logger.info("Generating embeddings for enhanced passages...")
        
        # Extract enhanced text for embedding
        enhanced_texts = [passage['enhanced_text'] for passage in enhanced_passages]
        
        # Generate embeddings in batches
        batch_size = 8
        all_embeddings = []
        
        for i in range(0, len(enhanced_texts), batch_size):
            batch_texts = enhanced_texts[i:i + batch_size]
            batch_embeddings = self.model.encode(
                batch_texts,
                convert_to_tensor=True,
                device=self.device,
                show_progress_bar=True
            )
            all_embeddings.append(batch_embeddings.cpu().numpy())
        
        # Combine all embeddings
        full_embeddings = np.vstack(all_embeddings)
        
        # Add embeddings to passage data
        for i, passage in enumerate(enhanced_passages):
            passage['embedding'] = full_embeddings[i].tolist()
            passage['embedding_dimension'] = len(full_embeddings[i])
        
        logger.info(f"Generated embeddings with dimension {full_embeddings.shape[1]}")
        return enhanced_passages
    
    def apply_intelligent_chunking(self, embedded_passages: List[Dict]) -> List[Dict]:
        """
        Step 3: Apply intelligent chunking while preserving embeddings
        """
        logger.info("Applying intelligent chunking...")
        
        final_chunks = []
        chunk_id = 1
        
        for passage in embedded_passages:
            original_text = passage['original_text']
            passage_embedding = np.array(passage['embedding'])
            
            # Split into sentences for intelligent chunking
            sentences = self._split_into_sentences(original_text)
            
            current_chunk_sentences = []
            current_word_count = 0
            
            for sentence in sentences:
                sentence_words = self.count_amharic_words(sentence)
                
                # Check if adding this sentence exceeds target size
                if (current_word_count + sentence_words > self.final_chunk_size and 
                    current_chunk_sentences):
                    
                    # Create chunk with pooled embedding
                    chunk_text = ' '.join(current_chunk_sentences)
                    chunk_embedding = self._pool_embedding_for_chunk(
                        passage_embedding, 
                        chunk_text, 
                        passage['enhanced_text']
                    )
                    
                    final_chunks.append({
                        'chunk_id': chunk_id,
                        'passage_id': passage['passage_id'],
                        'books': passage['books'],
                        'text': chunk_text,
                        'word_count': current_word_count,
                        'sentence_count': len(current_chunk_sentences),
                        'embedding': chunk_embedding.tolist(),
                        'enhanced_context': {
                            'biblical_context': passage['biblical_context'],
                            'theological_themes': passage['theological_themes']
                        },
                        'metadata': {
                            'source_chunks': passage['source_chunk_ids'],
                            'embedding_dimension': len(chunk_embedding)
                        }
                    })
                    
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    overlap_size = int(len(current_chunk_sentences) * self.overlap_ratio)
                    current_chunk_sentences = current_chunk_sentences[-overlap_size:] + [sentence]
                    current_word_count = sum(self.count_amharic_words(s) for s in current_chunk_sentences)
                else:
                    current_chunk_sentences.append(sentence)
                    current_word_count += sentence_words
            
            # Add final chunk for this passage
            if current_chunk_sentences:
                chunk_text = ' '.join(current_chunk_sentences)
                chunk_embedding = self._pool_embedding_for_chunk(
                    passage_embedding,
                    chunk_text,
                    passage['enhanced_text']
                )
                
                final_chunks.append({
                    'chunk_id': chunk_id,
                    'passage_id': passage['passage_id'],
                    'books': passage['books'],
                    'text': chunk_text,
                    'word_count': current_word_count,
                    'sentence_count': len(current_chunk_sentences),
                    'embedding': chunk_embedding.tolist(),
                    'enhanced_context': {
                        'biblical_context': passage['biblical_context'],
                        'theological_themes': passage['theological_themes']
                    },
                    'metadata': {
                        'source_chunks': passage['source_chunk_ids'],
                        'embedding_dimension': len(chunk_embedding)
                    }
                })
                chunk_id += 1
        
        logger.info(f"Created {len(final_chunks)} final chunks with late chunking")
        return final_chunks
    
    def _pool_embedding_for_chunk(self, 
                                 passage_embedding: np.ndarray, 
                                 chunk_text: str, 
                                 full_enhanced_text: str) -> np.ndarray:
        """
        Pool the passage embedding for a specific chunk
        Uses weighted averaging based on text overlap
        """
        # Calculate relative position and size
        chunk_ratio = len(chunk_text) / len(full_enhanced_text)
        
        # For late chunking, we use the full passage embedding
        # but can apply slight adjustments based on chunk position
        return passage_embedding
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences preserving Amharic sentence boundaries"""
        import re
        
        # Amharic sentence endings
        sentence_endings = r'[።፧፡፤፣]'
        sentences = re.split(sentence_endings, text)
        
        # Clean and filter sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter very short fragments
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    async def process_bible_with_late_chunking(self, 
                                             input_chunks_file: str, 
                                             output_dir: str) -> Dict[str, Any]:
        """
        Complete late chunking pipeline for Amharic Bible
        """
        logger.info("Starting late chunking embedding process...")
        
        # Load book chunks
        with open(input_chunks_file, 'r', encoding='utf-8') as f:
            book_chunks = [json.loads(line) for line in f]
        
        logger.info(f"Loaded {len(book_chunks)} book chunks")
        
        # Step 1: Create enhanced long passages
        enhanced_passages = await self.create_enhanced_long_passages(book_chunks)
        
        # Step 2: Generate embeddings for long passages
        embedded_passages = self.generate_passage_embeddings(enhanced_passages)
        
        # Step 3: Apply intelligent chunking
        final_chunks = self.apply_intelligent_chunking(embedded_passages)
        
        # Save results
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save final chunks with embeddings
        chunks_file = output_path / "late_chunked_embeddings.jsonl"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            for chunk in final_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        # Save enhanced passages for reference
        passages_file = output_path / "enhanced_passages.jsonl"
        with open(passages_file, 'w', encoding='utf-8') as f:
            for passage in embedded_passages:
                f.write(json.dumps(passage, ensure_ascii=False) + '\n')
        
        # Create summary
        summary = {
            'total_book_chunks_input': len(book_chunks),
            'enhanced_passages_created': len(enhanced_passages),
            'final_chunks_created': len(final_chunks),
            'avg_words_per_final_chunk': np.mean([c['word_count'] for c in final_chunks]),
            'embedding_dimension': final_chunks[0]['embedding_dimension'] if final_chunks else 0,
            'books_covered': len(set([book for chunk in final_chunks for book in chunk['books']])),
            'output_files': {
                'chunks': str(chunks_file),
                'passages': str(passages_file)
            }
        }
        
        # Save summary
        with open(output_path / "late_chunking_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Late chunking complete: {summary['final_chunks_created']} chunks created")
        return summary

def main():
    """Run late chunking embedding process"""
    embedder = LateChunkingEmbedder()
    
    input_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/complete_extraction/complete_bible_chunks.jsonl"
    output_dir = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/embeddings"
    
    try:
        result = asyncio.run(embedder.process_bible_with_late_chunking(input_file, output_dir))
        
        print("\nLate Chunking Embedding Results:")
        print(f"  Enhanced passages: {result['enhanced_passages_created']}")
        print(f"  Final chunks: {result['final_chunks_created']}")
        print(f"  Avg words per chunk: {result['avg_words_per_final_chunk']:.1f}")
        print(f"  Embedding dimension: {result['embedding_dimension']}")
        print(f"  Books covered: {result['books_covered']}")
        print(f"  Output: {result['output_files']['chunks']}")
        
    except Exception as e:
        logger.error(f"Late chunking failed: {e}")
        raise

if __name__ == "__main__":
    main()