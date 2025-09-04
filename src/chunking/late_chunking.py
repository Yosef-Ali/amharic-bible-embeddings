"""
LLM-powered contextual enhancement for Amharic Bible chunks
"""
import asyncio
from typing import List, Dict, Any, Optional
from config.llm_config import llm_manager
import logging

logger = logging.getLogger(__name__)

class LLMContextualizer:
    """
    Uses modern LLMs (Claude 4, Gemini Pro 2.5, DeepSeek 3.1) 
    to enhance Amharic Bible chunks with rich contextual information
    """
    
    def __init__(self):
        self.llm_manager = llm_manager
        
        # Prompt templates for different enhancement types
        self.prompts = {
            "biblical_context": """
Analyze this Amharic Bible verse and provide contextual information:

Amharic Text: {text}

Please provide a concise context summary including:
1. Book and chapter identification (if recognizable)
2. Key theological themes present
3. Important characters or events mentioned
4. Historical/cultural significance
5. Any cross-references to related biblical passages

Keep response under 200 words. Write in English but preserve important Amharic terms.
""",
            
            "semantic_boundaries": """
Analyze this Amharic Bible text for optimal semantic chunking:

Text: {text}

Identify:
1. Natural topic transitions
2. Narrative flow breaks
3. Theological theme changes
4. Character/speaker changes

Suggest where to split this text for better semantic coherence.
Response in English, max 150 words.
""",
            
            "cross_references": """
For this Amharic Bible text, identify related passages:

Text: {text}

Find connections to:
1. Parallel passages in other Gospels
2. Prophetic fulfillments
3. Thematic relationships across books
4. Doctrinal connections

List specific biblical references (Book Chapter:Verse format).
Max 100 words.
""",
            
            "theological_themes": """
Identify the main theological themes in this Amharic Bible text:

Text: {text}

Focus on:
1. Core doctrinal concepts
2. Spiritual teachings
3. Moral instructions
4. Prophetic elements
5. Covenant relationships

Provide theme keywords and brief explanations.
Max 150 words.
"""
        }
    
    async def enhance_single_chunk(self, 
                                  text: str, 
                                  enhancement_type: str = "biblical_context") -> Dict[str, Any]:
        """
        Enhance a single text chunk with LLM-generated context
        """
        
        if enhancement_type not in self.prompts:
            raise ValueError(f"Unknown enhancement type: {enhancement_type}")
        
        try:
            context = await self.llm_manager.generate_context(text, enhancement_type)
            
            return {
                "original_text": text,
                "enhancement_type": enhancement_type,
                "generated_context": context,
                "enhanced_text": f"{context}\n\nOriginal: {text}",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to enhance chunk: {e}")
            return {
                "original_text": text,
                "enhancement_type": enhancement_type,
                "generated_context": "",
                "enhanced_text": text,  # Fall back to original
                "success": False,
                "error": str(e)
            }
    
    async def enhance_chunks_batch(self, 
                                  chunks: List[str], 
                                  enhancement_type: str = "biblical_context",
                                  batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Enhance multiple chunks in batches to avoid rate limits
        """
        
        results = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [
                self.enhance_single_chunk(chunk, enhancement_type) 
                for chunk in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                    results.append({
                        "original_text": "",
                        "enhancement_type": enhancement_type,
                        "generated_context": "",
                        "enhanced_text": "",
                        "success": False,
                        "error": str(result)
                    })
                else:
                    results.append(result)
            
            # Small delay between batches to respect rate limits
            await asyncio.sleep(1)
        
        return results
    
    async def create_contextual_chunks(self, 
                                     bible_chapter: str,
                                     book_name: str,
                                     chapter_num: int) -> List[Dict[str, Any]]:
        """
        Create contextually enhanced chunks from a Bible chapter
        """
        
        # Split into verses (simple approach - can be improved)
        verses = self._split_into_verses(bible_chapter)
        
        enhanced_chunks = []
        
        for verse_num, verse_text in enumerate(verses, 1):
            # Generate multiple types of context for each verse
            enhancements = await asyncio.gather(
                self.enhance_single_chunk(verse_text, "biblical_context"),
                self.enhance_single_chunk(verse_text, "theological_themes"),
                return_exceptions=True
            )
            
            biblical_context = enhancements[0] if not isinstance(enhancements[0], Exception) else None
            theological_themes = enhancements[1] if not isinstance(enhancements[1], Exception) else None
            
            # Combine all contextual information
            combined_context = ""
            if biblical_context and biblical_context.get("success"):
                combined_context += f"Context: {biblical_context['generated_context']}\n"
            if theological_themes and theological_themes.get("success"):
                combined_context += f"Themes: {theological_themes['generated_context']}\n"
            
            enhanced_chunks.append({
                "verse_id": f"{book_name}_{chapter_num}_{verse_num}",
                "book": book_name,
                "chapter": chapter_num,
                "verse": verse_num,
                "original_text": verse_text,
                "contextual_enhancement": combined_context,
                "enhanced_text": f"{combined_context}\n\nVerse: {verse_text}",
                "metadata": {
                    "verse_length": len(verse_text),
                    "context_length": len(combined_context),
                    "enhancement_success": bool(combined_context)
                }
            })
        
        return enhanced_chunks
    
    def _split_into_verses(self, chapter_text: str) -> List[str]:
        """
        Simple verse splitting - can be enhanced with better parsing
        """
        import re
        
        # Split on verse numbers (both Arabic and Ge'ez numerals)
        verse_pattern = r'(\d+[:፦]|\d+\s|[፩-፼]+[:፦]?)'
        verses = re.split(verse_pattern, chapter_text)
        
        # Clean and filter verses
        clean_verses = []
        for verse in verses:
            verse = verse.strip()
            if len(verse) > 10 and not re.match(r'^\d+[:፦]?$', verse):
                clean_verses.append(verse)
        
        return clean_verses
    
    async def enhance_cross_references(self, 
                                     main_chunk: str, 
                                     related_chunks: List[str]) -> Dict[str, Any]:
        """
        Enhanced cross-reference analysis using LLM understanding
        """
        
        combined_text = f"Main passage: {main_chunk}\n\nRelated passages:\n"
        for i, related in enumerate(related_chunks, 1):
            combined_text += f"{i}. {related}\n"
        
        enhancement = await self.enhance_single_chunk(combined_text, "cross_references")
        
        return {
            "main_chunk": main_chunk,
            "related_chunks": related_chunks,
            "cross_reference_analysis": enhancement.get("generated_context", ""),
            "enhanced_main_chunk": enhancement.get("enhanced_text", main_chunk)
        }

# Global contextualizer instance
llm_contextualizer = LLMContextualizer()
