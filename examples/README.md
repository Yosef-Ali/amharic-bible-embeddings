# Examples and Usage

This directory contains examples demonstrating the complete book digitization system.

## 📚 Available Examples

### 1. Complete Book Digitization
**File:** `digitize_book_example.py`
- Shows full pipeline: TOC → OCR → Embeddings + PDF
- Multiple book types (Bible, Calendar, Prayer Book)
- All output formats demonstrated

### 2. TOC Analysis Example  
**File:** `toc_example.py`
- Detailed TOC detection and structure analysis
- Shows importance of understanding book structure FIRST
- Contextual embedding generation

### 3. Real Book Testing
**File:** `test_catechism.py` (in parent directory)
- Tests with actual Catholic Catechism book
- Demonstrates handling of .tif files
- Shows expected TOC structure for religious texts

## 🚀 Quick Start

### Install Dependencies
```bash
pip install opencv-python reportlab pillow
```

### Run Complete Digitization
```python
from src.ocr.book_digitizer import BookDigitizer

digitizer = BookDigitizer()
result = digitizer.digitize_book(
    'path/to/scanned/pages/',     # Your book images
    'output/',                    # Output directory
    'My Ethiopian Book'           # Book title
)
```

## 📤 Output Files

Each digitization creates 5 files:

1. **embeddings.json** - AI training data with chapter context
2. **recreated.pdf** - Searchable PDF preserving original layout
3. **text.txt** - Plain text with book structure
4. **metadata.json** - TOC structure and statistics  
5. **training.jsonl** - Machine learning format

## 🎯 Perfect For

- **Religious texts** (Bibles, Catechisms, Prayer Books)
- **Complex layouts** (multi-column, mixed languages)
- **Multi-page books** with proper chapter structure
- **AI training data** with contextual information
- **Digital archives** with searchable content

## 📋 TOC Analysis Features

The system automatically:
- ✅ Detects Table of Contents in first 10 pages
- ✅ Recognizes Amharic religious terms (ምዕራፍ, ክፍል, በዓል)
- ✅ Extracts chapter titles and page numbers
- ✅ Validates structure against available pages
- ✅ Creates contextual embeddings with chapter information

## 🔧 Troubleshooting

### Missing Dependencies
```bash
# Install all required packages
pip install opencv-python reportlab pillow

# For better Amharic font support
# Download Noto Sans Ethiopic font
```

### File Format Support
- ✅ TIFF (.tif, .tiff)
- ✅ JPEG (.jpg, .jpeg)
- ✅ PNG (.png)
- ✅ BMP (.bmp)

### Common Issues
- **No TOC detected**: System continues with sequential processing
- **Missing fonts**: PDF uses default fonts, still searchable
- **Large files**: System handles files up to several MB per page

## 💡 Tips

1. **Organize your images**: Use consistent naming (page1.jpg, page2.jpg)
2. **Check TOC first**: TOC analysis is critical for proper structure
3. **Validate results**: Check metadata.json for TOC detection results
4. **Multiple formats**: Use different output files for different purposes