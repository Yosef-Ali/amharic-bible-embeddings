# Changelog

All notable changes to the Amharic Bible Embeddings project.

## [2.0.0] - 2025-09-06 - Major Book Digitization Update

### 🎯 Major Features Added

#### Complete Book Digitization System
- **TOC Analysis FIRST** - Critical requirement: understands book structure before processing
- **Multi-page book handling** - Perfect for complex religious texts
- **Chapter-aware embeddings** - Each text chunk includes structural context
- **PDF recreation** - Preserves original layout with searchable text overlay
- **5 output formats** - Optimized for different use cases

#### Advanced TOC Detection
- **Automatic TOC detection** in first 10 pages
- **Amharic religious term recognition** (ምዕራፍ, ክፍል, በዓል, ጾም)
- **Hierarchical structure extraction** (chapters → sections → subsections)
- **Page number pattern detection** (dots, dashes, lines)
- **Validation against available pages**

#### Enhanced OCR Pipeline
- **Complex layout detection** (single/double page, multi-column)
- **Reading order preservation** across complex layouts
- **Batch processing** for entire books
- **Context-aware chunking** with chapter information
- **No spell correction** - focuses on accurate text extraction

### 🔧 Technical Improvements

#### New Components
- `TOCAnalyzer` - Comprehensive Table of Contents analysis
- `BookDigitizer` - Complete book processing pipeline
- `DocumentScanner` - Advanced layout detection
- `EmbeddingPipeline` - Context-aware text chunking

#### Dependencies Added
- OpenCV (`opencv-python`) - Image processing and layout detection
- ReportLab (`reportlab`) - PDF generation with original layouts
- Pillow (`pillow`) - Enhanced image handling

### 📤 Output Formats

1. **embeddings.json** - AI training data with chapter context
2. **recreated.pdf** - Searchable PDF preserving original layout
3. **text.txt** - Structured plain text
4. **metadata.json** - TOC structure and processing statistics
5. **training.jsonl** - Machine learning optimized format

### 🎯 Perfect For

- **Catholic Catechism** - Tested with actual Compendium of Catechism
- **Ethiopian Orthodox texts** - Bible, liturgical books, prayer books
- **Complex religious manuscripts** - Multi-chapter, hierarchical structure
- **AI/ML training data** - Contextual embeddings for better models

### 📋 Processing Pipeline

```
Step 0: TOC Analysis (CRITICAL FIRST STEP)
├── Detect TOC pages in first 10 pages
├── Extract chapter structure and page numbers
├── Validate against available images
└── Create book structure map

Step 1: OCR Processing (with TOC context)
├── Process pages in proper order
├── Apply complex layout detection
├── Add chapter context to each text block
└── Maintain reading order

Step 2: Embedding Preparation
├── Create contextual chunks with chapter info
├── Preserve hierarchical relationships
├── Generate structured metadata
└── Optimize for AI training

Step 3: PDF Recreation
├── Preserve original page layouts
├── Add invisible searchable text overlay
├── Support Amharic fonts
└── Create fully searchable document
```

### 🚀 Usage

```python
from src.ocr.book_digitizer import BookDigitizer

digitizer = BookDigitizer()
result = digitizer.digitize_book(
    'book_images/',           # Scanned pages (.tif, .jpg, .png)
    'output/',               # Output directory
    'Ethiopian Bible'        # Book title
)
```

---

## [1.0.0] - 2025-09-05 - Initial Release

### Ethiopian Calendar System
- Accurate Gregorian ↔ Ethiopian date conversion
- Ethiopian Orthodox Easter (Fasika) calculations
- Liturgical seasons and feast day calculations
- Fasting calendar with traditional rules

### Liturgical Calendar
- Western and Eastern Orthodox liturgical systems
- Interactive Streamlit calendar interface
- Scripture readings integration
- Multi-tradition liturgical support

### AI Integration
- MCP server for AI assistant access
- Unified liturgical agent
- Calendar embedding system

### Project Organization
- Clean branch structure (feature branches)
- Consolidated from multiple separate repositories
- Proper Git workflow implementation
- Comprehensive documentation

---

## Future Roadmap

### Planned Features
- **Enhanced OCR accuracy** with trained Amharic models
- **Liturgical reading system** with Ethiopian Orthodox feast days
- **MCP server integration** for AI assistant access
- **Advanced font support** for better PDF recreation
- **Batch processing optimizations** for large book collections

### Integration Targets
- **Tesseract OCR** integration for improved accuracy
- **Advanced ML models** for Amharic text recognition
- **Cloud processing** support for large documents
- **API endpoints** for external integration