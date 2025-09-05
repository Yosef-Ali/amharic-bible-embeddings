# Standalone Ethiopian Calendar System

Complete Ethiopian calendar conversion system with no dependencies on embeddings or external libraries.

## Features

✅ **Complete Calendar Conversion**
- Gregorian to Ethiopian date conversion
- Ethiopian to Gregorian date conversion
- Accurate New Year (Enkutatash) calculations

✅ **Ethiopian Orthodox Features**
- Major feast days (Enkutatash, Meskel, Genna, Timket)
- Liturgical seasons
- Fasting periods and rules
- Weekly fasting days (Wednesday, Friday)

✅ **Easy to Use Functions**
- `convert_to_ethiopian(year, month, day)` - Convert any Gregorian date
- `convert_to_gregorian(eth_year, eth_month, eth_day)` - Reverse conversion
- `get_today_ethiopian()` - Get today's Ethiopian date
- `get_ethiopian_new_year(year)` - Get Enkutatash date

## Usage

```python
from ethiopian_calendar import EthiopianCalendar, convert_to_ethiopian, get_today_ethiopian

# Convert a specific date
result = convert_to_ethiopian(2025, 10, 11)
print(result['formatted'])  # ጥቅምት 1, 2018 ዓ.ም.

# Get today's Ethiopian date
today = get_today_ethiopian()
print(f"Today: {today['ethiopian_date']['formatted']}")
print(f"Season: {today['liturgical_season']}")
print(f"Fasting: {today['fasting_info']['type']}")

# Get complete information
info = EthiopianCalendar.get_complete_info(datetime.date(2025, 10, 11))
```

## Ethiopian Months

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

## Installation

No installation required! Just copy `ethiopian_calendar.py` to your project.

```bash
# Copy the standalone file
cp ethiopian_calendar.py /path/to/your/project/

# Or run directly
python ethiopian_calendar.py
```

## Testing

Run the built-in test:

```bash
python ethiopian_calendar.py
```

## No Dependencies

This system requires only Python standard library:
- `datetime` - For date handling
- `typing` - For type hints

No external packages, no embeddings, completely standalone!

## Accuracy

- ✅ Tested against official Ethiopian Orthodox calendars
- ✅ Matches phone calendar applications
- ✅ Accurate feast days and fasting periods
- ✅ Proper leap year calculations
- ✅ Bidirectional conversion verification

## Examples

```python
import datetime
from ethiopian_calendar import EthiopianCalendar

# Example 1: Convert today's date
today = datetime.date.today()
eth_today = EthiopianCalendar.gregorian_to_ethiopian(today)
print(f"Today is {eth_today['formatted']}")

# Example 2: Check if it's a fasting day
fasting = EthiopianCalendar.is_fasting_day(today, eth_today)
if fasting['is_fasting']:
    print(f"Today is a fasting day: {fasting['type']}")
    print(f"Rules: {', '.join(fasting['rules'])}")

# Example 3: Find Ethiopian New Year
ny_2025 = get_ethiopian_new_year(2025)
print(f"Ethiopian New Year 2025: {ny_2025['gregorian_formatted']}")

# Example 4: Get feast day information
feast = EthiopianCalendar.get_feast_info(1, 1)  # መስከረም 1
if feast:
    print(f"Feast: {feast['name_english']} ({feast['name_amharic']})")
```

## License

Free to use for any purpose. Copied from working liturgical-calendar-embeddings implementation.