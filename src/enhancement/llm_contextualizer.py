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

# Global contextualizer instance
llm_contextualizer = LLMContextualizer()
