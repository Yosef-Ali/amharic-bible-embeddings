"""
Configuration settings for Amharic Bible Embeddings project
"""
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CHUNKS_DIR = DATA_DIR / "chunks"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

# Ensure directories exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, CHUNKS_DIR, EMBEDDINGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

class Settings:
    """Application settings"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Vector Database
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chromadb")
    CHROMADB_PATH = os.getenv("CHROMADB_PATH", str(EMBEDDINGS_DIR / "chromadb"))
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # LLM Enhancement
    CONTEXT_ENHANCEMENT_LLM = os.getenv("CONTEXT_ENHANCEMENT_LLM", "claude")
    MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "2000"))
    ENABLE_CROSS_REFERENCES = os.getenv("ENABLE_CROSS_REFERENCES", "true").lower() == "true"
    ENABLE_THEOLOGICAL_CONTEXT = os.getenv("ENABLE_THEOLOGICAL_CONTEXT", "true").lower() == "true"
    
    # Processing
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    CACHE_EMBEDDINGS = os.getenv("CACHE_EMBEDDINGS", "true").lower() == "true"
    
    # Application
    APP_PORT = int(os.getenv("APP_PORT", "8501"))
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Bible structure configuration
BIBLE_BOOKS = {
    "old_testament": [
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
        "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
        "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
        "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
        "Ecclesiastes", "Song of Songs", "Isaiah", "Jeremiah",
        "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
        "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
        "Haggai", "Zechariah", "Malachi"
    ],
    "new_testament": [
        "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
        "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
        "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
        "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
        "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
    ]
}

# Amharic-specific settings
AMHARIC_CONFIG = {
    "script": "ethiopic",
    "direction": "ltr",
    "geez_numerals": True,
    "fidel_normalization": True,
    "morphological_analysis": True
}

settings = Settings()