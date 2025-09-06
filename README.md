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

### 🔤 Amharic OCR (New!)
- **Optical Character Recognition** for Amharic text
- **Biblical document processing** specialization
- **Fidel script recognition** framework
- **Ethiopian numeral conversion**

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

### Amharic OCR
```python
from src.ocr.amharic_ocr import AmharicOCR

ocr = AmharicOCR()
result = ocr.extract_text_from_image('path/to/amharic_document.jpg')
print(f"Extracted text: {result['processed_text']}")
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

### Document Types
- **Biblical manuscripts**
- **Liturgical texts**
- **Calendar documents**
- **Religious inscriptions**

## 🎯 Use Cases

- **Ethiopian Orthodox Churches** - Liturgical planning
- **Religious scholars** - Calendar research  
- **Software developers** - Ethiopian calendar integration
- **Digital humanities** - Amharic text digitization
- **AI systems** - Ethiopian religious knowledge

## 📞 Support

For questions about Ethiopian calendar accuracy or liturgical calculations, this system has been verified against:
- Ethiopian Orthodox Church official calendars
- Multiple phone calendar applications
- Historical liturgical documents
- Traditional Bahire Hasab calculations

---

**🇪🇹 Built for the Ethiopian Orthodox community and scholars worldwide**