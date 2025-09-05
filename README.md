# Unified Liturgical Reading Agent

🎯 **Western Catholic + Ethiopian Orthodox** liturgical readings system

## Architecture

### Western Readings (Online)
- **USCCB**: Primary Catholic source
- **Vatican News**: Secondary Catholic source  
- **Catholic Calendar**: Fallback source

### Ethiopian Orthodox Readings (Local)
- **Ethiopian Calendar**: Local calendar calculations
- **Amharic Bible**: Your OCR biblical text database
- **Ethiopian Lectionary**: Calculated reading cycles

## Features

1. **Daily Readings**: Both traditions for any date
2. **Calendar Integration**: Ethiopian + Gregorian calendars
3. **Fasting Information**: Ethiopian Orthodox fasting rules
4. **Cross-Reference**: Find parallel readings between traditions
5. **Local Processing**: No API restrictions on Ethiopian content

## Usage

```python
from src.unified_agent import LiturgicalReadingAgent

agent = LiturgicalReadingAgent()

# Get both Western and Ethiopian readings for today
readings = agent.get_daily_readings()

# Get readings for specific date
readings = agent.get_daily_readings(date="2025-01-07")

# Get only Western readings
western = agent.get_western_readings()

# Get only Ethiopian Orthodox readings
ethiopian = agent.get_ethiopian_readings()
```

## Data Flow

```
Date Input
    ↓
Western (Online) ← → Agent ← → Ethiopian (Local)
    ↓                            ↓
USCCB/Vatican           Ethiopian Calendar
    ↓                            ↓
Reading References      Amharic Bible Text
    ↓                            ↓
    └─────── Combined ──────────┘
              Output
```