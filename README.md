# Ethiopian Liturgical Calendar & Readings Database

🗓️ **Comprehensive liturgical system supporting both Western Catholic and Eastern Orthodox (Ethiopian) traditions**

## Why This Project is Valuable

### 📚 **Real-World Utility**
- **Daily liturgical planning** for priests and faithful
- **Cross-tradition comparison** for theological study
- **Semantic search** through readings by theme
- **Ethiopian calendar integration** with fasting rules
- **Local processing** (no API content filtering issues)

### 🎯 **Target Users**
- Ethiopian Orthodox clergy
- Catholic priests serving Ethiopian communities
- Theologians studying comparative liturgy
- Faithful planning daily spiritual reading
- Religious educators

## Project Structure

```
liturgical-calendar-embeddings/
├── data/
│   ├── sample_liturgical_readings.json    # Template readings
│   ├── western_lectionary/                # Roman Catholic readings
│   ├── ethiopian_readings/                # Ethiopian Orthodox readings
│   └── saints_calendar/                   # Saints and commemorations
├── src/
│   ├── calendar_calculator.py             # Date and season calculations
│   ├── reading_processor.py               # Process liturgical texts
│   └── ethiopian_calendar.py              # Ethiopian calendar logic
├── scripts/
│   ├── build_liturgical_db.py            # Build searchable database
│   └── import_readings.py                # Import from various sources
└── app.py                                 # Streamlit interface
```

## Features

### 🌍 **Western Liturgical System**
- **3-Year Cycle**: Years A, B, C with proper Gospel rotation
- **Liturgical Seasons**: Advent, Christmas, Lent, Easter, Ordinary Time
- **Daily Readings**: First Reading, Responsorial Psalm, Gospel
- **Saint Commemorations**: Major and optional memorials
- **Proper vs Common**: Feast-specific vs seasonal readings

### ⛪ **Ethiopian Orthodox System** 
- **Ethiopian Calendar**: 13-month system with proper date conversion
- **Liturgical Seasons**: Aligned with Ethiopian Orthodox tradition
- **Fasting Calendar**: Wednesday/Friday fasts, Great Lent, Advent fast
- **Reading Cycle**: Old Testament, Epistle, Gospel structure  
- **Saints' Days**: Ethiopian Orthodox saint commemorations
- **Feast Integration**: Timkat, Meskel, Genna, etc.

## Data Integration Points

### 📖 **Reading Sources** (To Be Added)
1. **Western**: 
   - Roman Lectionary texts
   - USCCB daily readings
   - Liturgy of the Hours

2. **Ethiopian Orthodox**:
   - **Your OCR project**: Amharic biblical texts
   - Ethiopian Orthodox lectionary
   - Traditional feast day readings

### 🔗 **Cross-References**
- Parallel readings between traditions
- Thematic connections across calendars  
- Saint commemorations in both systems
- Seasonal alignment analysis

## Quick Start

```bash
cd /Users/mekdesyared/Embedding/liturgical-calendar-embeddings

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build database
python scripts/build_liturgical_db.py

# Launch interface
streamlit run app.py
```

## Search Capabilities

### 🔍 **Semantic Search Examples**
- **Thematic**: "forgiveness readings", "healing miracles"
- **Seasonal**: "Advent prophecies", "Easter resurrection"
- **Cross-tradition**: "Christmas readings both calendars"
- **Saints**: "readings for Saint Mary", "Ethiopian martyrs"
- **Practical**: "readings for wedding", "funeral liturgy"

### 📅 **Calendar Navigation**
- Jump to any date in 2025
- View liturgical season information
- See fasting requirements (Ethiopian)
- Compare traditions side-by-side

## Integration with Your OCR Project

This liturgical calendar system **perfectly complements** your prayer book OCR:

1. **Prayers Database** ← Your OCR project
2. **Liturgical Readings** ← This project
3. **Combined Search** → Find prayers AND readings for any occasion
4. **Complete Spiritual Resource** → Everything needed for Ethiopian Orthodox worship

## Data Schema Ready For:

- **Authentic Amharic readings** from your OCR
- **Proper liturgical translations**
- **Ethiopian Orthodox lectionary**
- **Cross-references between prayer books and biblical readings**

---

**This gives you a complete liturgical ecosystem: daily prayers + daily readings + calendar system, all locally processed without API restrictions!** 🙏

Ready to build this comprehensive liturgical resource?
