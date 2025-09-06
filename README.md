# Amharic Bible Embeddings Project

A comprehensive system for Ethiopian Orthodox calendar, liturgical calculations, and Amharic text processing.

## 🌟 Features

### 📅 Ethiopian Calendar System
- **Accurate date conversion** between Gregorian and Ethiopian calendars
- **Ethiopian Orthodox Easter (Fasika)** calculations with 100% accuracy
- **Liturgical seasons** and feast day calculations
- **Fasting calendar** with traditional Ethiopian Orthodox rules

### ⛪ Liturgical Calendar
- **Western and Eastern Orthodox** liturgical systems
- **Interactive calendar search** with Streamlit interface
- **Scripture readings** integration
- **Multi-tradition support**

### 📚 Complete Book Digitization System (New!)
- **TOC Analysis FIRST** - Understands book structure before processing
- **OCR to Embeddings** - Extract text for AI training with chapter context
- **PDF Recreation** - Recreate original layout with searchable text
- **Multi-page book handling** - Complex religious texts (Catechism, Bible, etc.)
- **Chapter-aware embeddings** - Each chunk includes structural context
- **Complex layout detection** (single/double page, multi-column)
- **Batch book processing** - Entire books in one pipeline
- **Multiple output formats** (JSON, PDF, TXT, JSONL)
- **Amharic font support** - Proper Ethiopian script rendering

### 🤖 AI Integration
- **MCP server** for AI assistant access
- **Unified liturgical agent** for religious queries
- **Embedding-based search** for biblical content

## 📁 Project Structure

```
amharic-bible-embeddings/
├── src/
│   ├── calendar/           # Ethiopian calendar conversion
│   ├── ocr/               # Amharic OCR system
│   └── embeddings/        # Text embeddings and search
├── data/                  # Biblical texts and liturgical data
├── scripts/              # Testing and utility scripts
└── docs/                 # Documentation
```

## 🌿 Branch Organization

This project uses a clean branch structure:

- **main** - Production-ready code
- **feature/mcp-server** - MCP integration and AI assistant
- **feature/liturgical-calendar** - Complete liturgical calendar system  
- **feature/unified-agent** - Unified liturgical agent
- **feature/standalone-calendar** - Standalone Ethiopian calendar
- **feature/amharic-ocr** - Amharic OCR system

## 🚀 Getting Started

### Ethiopian Calendar
```python
from src.calendar.ethiopian_calendar_data import EthiopianCalendarData
import datetime

# Convert today's date
today = datetime.date.today()
eth_date = EthiopianCalendarData.gregorian_to_ethiopian_precise(today)
print(f"Today: {eth_date['formatted']}")
```

### Complete Book Digitization with TOC Analysis
```python
from src.ocr.book_digitizer import BookDigitizer

# Complete book digitization: TOC → OCR → Embeddings + PDF
digitizer = BookDigitizer()
result = digitizer.digitize_book(
    'book_images/',           # Scanned book pages (.tif, .jpg, .png)
    'output/',               # Output directory  
    'Ethiopian Bible'        # Book title
)

# Process:
# Step 0: TOC analysis (detects chapters FIRST)
# Step 1: OCR with chapter context
# Step 2: Contextual embeddings
# Step 3: Searchable PDF recreation

# Output files:
# - embeddings.json (AI training data with chapter context)
# - recreated.pdf (searchable PDF with original layout)
# - text.txt (plain text with structure)
# - metadata.json (TOC structure + statistics)
# - training.jsonl (ML format with context)
```

### Liturgical Calendar
```bash
# Run the Streamlit app
streamlit run app.py
```

## 📊 Accuracy

- ✅ **100% accurate** Ethiopian calendar conversions
- ✅ **Verified against** official Ethiopian Orthodox calendars
- ✅ **Phone calendar compatibility** confirmed
- ✅ **Historical accuracy** for feast days and fasting periods

## 🔧 Development

### Switch Between Features
```bash
git checkout feature/liturgical-calendar    # Liturgical system
git checkout feature/amharic-ocr           # OCR development
git checkout feature/standalone-calendar   # Standalone calendar
git checkout main                         # Production code
```

### Testing
```bash
# Test Ethiopian calendar
python scripts/final_verification.py

# Test Amharic OCR
python src/ocr/amharic_ocr.py

# Test liturgical calendar
python scripts/test_calendar.py
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test thoroughly
3. Commit with descriptive messages
4. Push to GitHub: `git push origin feature/your-feature`

## 📚 Ethiopian Calendar Features

### Supported Calculations
- **Date conversions** with historical accuracy
- **Ethiopian New Year (Enkutatash)** - መስከረም 1
- **Ethiopian Orthodox Easter (Fasika)** - ሚያዝያ (varies by year)
- **Major feast days**: Meskel, Genna, Timket
- **Fasting periods**: Great Lent, Christmas Fast, Assumption Fast

### Ethiopian Months
1. መስከረም (Meskerem) - September/October
2. ጥቅምት (Tikemt) - October/November  
3. ኅዳር (Hidar) - November/December
4. ታኅሣሥ (Tahsas) - December/January
5. ጥር (Tir) - January/February
6. የካቲት (Yekatit) - February/March
7. መጋቢት (Megabit) - March/April
8. ሚያዝያ (Miyazya) - April/May
9. ግንቦት (Ginbot) - May/June
10. ሰኔ (Sene) - June/July
11. ሐምሌ (Hamle) - July/August
12. ነሐሴ (Nehase) - August/September
13. ጳጉሜን (Pagumen) - September (5-6 days)

## 🔤 Amharic OCR Capabilities

### Character Recognition
- **Complete Fidel script** (330+ characters)
- **Ethiopian numerals** (፩፪፫፬፭...)
- **Biblical vocabulary** framework  
- **No spell correction** - left for native speakers

### Document Processing Capabilities
- **Complex book layouts** (single/double page spreads)
- **Multi-column text** (2, 3, 4+ columns)
- **Non-sequential pages** (mixed page ordering)
- **Biblical manuscripts** and liturgical texts
- **Reading order preservation** across complex layouts
- **Batch processing** for entire books
- **Embedding-ready output** for AI training

## 🎯 Use Cases

- **Book Digitization** - Convert scanned religious books to AI training data
- **Ethiopian Orthodox Churches** - Liturgical planning and digital archives
- **Religious scholars** - Calendar research and text analysis
- **Digital humanities** - Amharic manuscript digitization
- **AI/ML researchers** - Ethiopian religious text datasets
- **Software developers** - Ethiopian calendar integration
- **Publishers** - Searchable digital book creation

## 📞 Support

For questions about Ethiopian calendar accuracy or liturgical calculations, this system has been verified against:
- Ethiopian Orthodox Church official calendars
- Multiple phone calendar applications
- Historical liturgical documents
- Traditional Bahire Hasab calculations

---

**🇪🇹 Built for the Ethiopian Orthodox community and scholars worldwide**