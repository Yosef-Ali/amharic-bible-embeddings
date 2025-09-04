# Amharic Bible Embeddings Project

🇪🇹 **Advanced semantic search for the Amharic Bible using Late Chunking and modern LLM enhancement**

## Features

- **Late Chunking**: Preserves biblical context across verses
- **Modern LLM Integration**: Uses Claude 4, Gemini Pro 2.5, DeepSeek 3.1
- **Amharic Optimization**: Handles Ge'ez script and morphological complexity
- **Semantic Search**: Find relevant passages by meaning, not just keywords
- **Web Interface**: Easy-to-use Streamlit application

## Quick Start

### 1. Setup Environment

```bash
cd /Users/mekdesyared/Embedding/amharic-bible-embeddings
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
ANTHROPIC_API_KEY=your_claude_api_key
GOOGLE_API_KEY=your_gemini_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 3. Add Bible Data

Place your Amharic Bible files in `data/raw/`:
- Supported formats: `.txt`, `.json`, `.csv`
- Can be organized by books/chapters or as complete text

### 4. Process the Bible

```bash
python scripts/process_bible.py
```

This will:
- Clean and normalize Amharic text
- Apply Late Chunking with context preservation
- Generate LLM-enhanced contextual information
- Create high-quality embeddings
- Save results for fast retrieval

### 5. Start the Web Interface

```bash
streamlit run app.py
```

Visit `http://localhost:8501` to use the search interface.

## Architecture Overview

```
📄 Raw Amharic Bible Text
    ↓
🧹 Amharic Text Cleaning (Ge'ez normalization, Fidel handling)
    ↓  
🤖 LLM Contextual Enhancement (Claude/Gemini/DeepSeek)
    ↓
📚 Semantic Chunking (Verse-level with context windows)
    ↓
⚡ Late Chunking Embedding (Context-preserving embeddings)
    ↓
💾 Vector Storage (ChromaDB/Qdrant)
    ↓
🔍 Semantic Search & Q&A Interface
```

## Key Components

### Late Chunking Implementation
- **File**: `src/chunking/late_chunking.py`
- **Purpose**: Embeds entire chapters before chunking to preserve context
- **Benefits**: Maintains cross-verse references and narrative flow

### LLM Enhancement
- **File**: `src/enhancement/llm_contextualizer.py`
- **Purpose**: Uses modern LLMs to add theological and historical context
- **Benefits**: Enriches embeddings with deeper biblical understanding

### Amharic Processing
- **File**: `src/preprocessing/amharic_cleaner.py`
- **Purpose**: Handles Amharic-specific text normalization
- **Features**: Ge'ez numerals, Fidel variations, Unicode normalization

## Usage Examples

### Search Examples

**Amharic queries:**
- "ፍቅር ስለ ኢየሱስ" (About Jesus' love)
- "የመንግሥተ ሰማያት ምሳሌ" (Parables of the Kingdom of Heaven)

**English queries:**
- "Jesus healing the sick"
- "Parables about forgiveness"

### Python API Usage

```python
from src.chunking.late_chunking import late_chunking_embedder
from src.enhancement.llm_contextualizer import llm_contextualizer

# Process a chapter
chapter_text = "Your Amharic Bible chapter text here"
chunk_infos = [...] # Your chunk information

# Generate Late Chunking embeddings
results = late_chunking_embedder.embed_with_late_chunking(chapter_text, chunk_infos)

# Enhance with LLM context
enhanced = await llm_contextualizer.enhance_single_chunk(
    text="አመነ፥ እና ተድኖ ይሆን",
    enhancement_type="biblical_context"
)
```

## Configuration

Key settings in `.env`:

- `CONTEXT_ENHANCEMENT_LLM`: Choose `claude`, `gemini`, or `deepseek`
- `EMBEDDING_MODEL`: Default is `paraphrase-multilingual-mpnet-base-v2`
- `ENABLE_THEOLOGICAL_CONTEXT`: Enable LLM enhancement (slower but better)
- `CHUNK_SIZE`: Chunk size for processing (default: 512)

## Performance Notes

- **With LLM Enhancement**: Slower but higher quality context
- **Without LLM Enhancement**: Faster processing, still good embeddings
- **Late Chunking**: ~2x slower than traditional but much better context preservation

## Troubleshooting

1. **No API Key**: Set up at least one LLM API key in `.env`
2. **Memory Issues**: Reduce `BATCH_SIZE` in settings
3. **Slow Processing**: Disable `ENABLE_THEOLOGICAL_CONTEXT` for speed
4. **Import Errors**: Ensure all requirements are installed

## Next Steps

1. Add your Amharic Bible data to `data/raw/`
2. Configure your preferred LLM in `.env`
3. Run the processing pipeline
4. Start asking biblical questions!

---

*Built with Late Chunking, modern LLMs, and love for Ethiopian biblical scholarship* 🙏
