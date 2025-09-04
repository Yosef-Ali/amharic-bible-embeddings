"""
LLM configuration and clients for contextual enhancement
"""
import os
from typing import Optional, Dict, Any
import asyncio
from abc import ABC, abstractmethod

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

try:
    import httpx
except ImportError:
    httpx = None

class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    async def generate_context(self, text: str, prompt_template: str) -> str:
        """Generate contextual information for a text chunk"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM client is properly configured"""
        pass

class ClaudeClient(BaseLLMClient):
    """Claude API client for contextual enhancement"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        if self.api_key and anthropic:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    async def generate_context(self, text: str, prompt_template: str) -> str:
        if not self.client:
            raise ValueError("Claude client not properly initialized")
        
        prompt = prompt_template.format(text=text)
        
        message = self.client.messages.create(
            model="claude-3-sonnet-20240229",  # Update to Claude 4 when available
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text if message.content else ""
    
    def is_available(self) -> bool:
        return self.client is not None

class GeminiClient(BaseLLMClient):
    """Gemini API client for contextual enhancement"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def generate_context(self, text: str, prompt_template: str) -> str:
        if not self.model:
            raise ValueError("Gemini client not properly initialized")
        
        prompt = prompt_template.format(text=text)
        response = await asyncio.to_thread(self.model.generate_content, prompt)
        
        return response.text if response.text else ""
    
    def is_available(self) -> bool:
        return self.model is not None

class DeepSeekClient(BaseLLMClient):
    """DeepSeek API client using OpenAI-compatible interface"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.client = None
        if self.api_key and openai:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
    
    async def generate_context(self, text: str, prompt_template: str) -> str:
        if not self.client:
            raise ValueError("DeepSeek client not properly initialized")
        
        prompt = prompt_template.format(text=text)
        
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.1
        )
        
        return response.choices[0].message.content if response.choices else ""
    
    def is_available(self) -> bool:
        return self.client is not None

class OpenRouterClient(BaseLLMClient):
    """OpenRouter API client supporting multiple models"""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.api_url = api_url or os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.available = bool(self.api_key and httpx)
    
    async def generate_context(self, text: str, prompt_template: str) -> str:
        if not self.available:
            raise ValueError("OpenRouter client not properly configured")
        
        prompt = prompt_template.format(text=text)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Yosef-Ali/amharic-bible-embeddings",
            "X-Title": "Amharic Bible Embeddings"
        }
        
        payload = {
            "model": "anthropic/claude-3-sonnet",  # Can use any OpenRouter model
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"] if result.get("choices") else ""
    
    def is_available(self) -> bool:
        return self.available

class LLMManager:
    """Manages multiple LLM clients and provides fallback options"""
    
    def __init__(self, preferred_llm: str = "openrouter"):
        self.clients: Dict[str, BaseLLMClient] = {
            "openrouter": OpenRouterClient(),
            "claude": ClaudeClient(),
            "gemini": GeminiClient(),
            "deepseek": DeepSeekClient()
        }
        self.preferred_llm = preferred_llm
    
    def get_available_client(self) -> Optional[BaseLLMClient]:
        """Get the first available LLM client, preferring the configured one"""
        
        # Try preferred client first
        if self.preferred_llm in self.clients and self.clients[self.preferred_llm].is_available():
            return self.clients[self.preferred_llm]
        
        # Fall back to any available client
        for name, client in self.clients.items():
            if client.is_available():
                print(f"Using fallback LLM: {name}")
                return client
        
        return None
    
    async def generate_context(self, text: str, context_type: str = "biblical") -> str:
        """Generate contextual information using available LLM"""
        
        client = self.get_available_client()
        if not client:
            raise ValueError("No LLM clients are available. Please configure API keys.")
        
        templates = {
            "biblical": """
Analyze this Amharic Bible text and provide contextual information:

Text: {text}

Please provide:
1. Book and chapter identification
2. Key theological themes
3. Important characters or events mentioned
4. Historical/cultural context
5. Cross-references to related passages

Respond in English, but preserve Amharic terms where appropriate.
Keep response under 200 words.
""",
            "semantic": """
Analyze this Amharic Bible text for semantic chunking:

Text: {text}

Identify:
1. Natural semantic boundaries
2. Topic transitions
3. Narrative flow
4. Thematic coherence

Suggest optimal chunking points and explain reasoning.
Response in English, max 150 words.
""",
            "cross_reference": """
For this Amharic Bible text, identify related passages:

Text: {text}

Find:
1. Parallel passages
2. Thematic connections
3. Prophetic fulfillments
4. Doctrinal relationships

List specific book:chapter:verse references.
Max 100 words.
"""
        }
        
        template = templates.get(context_type, templates["biblical"])
        return await client.generate_context(text, template)

# Global LLM manager instance
llm_manager = LLMManager()
