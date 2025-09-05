#!/usr/bin/env python3
"""
Example usage of the Standalone Ethiopian Calendar System
Demonstrates various features and functions
"""

import datetime
from ethiopian_calendar import (
    EthiopianCalendar, 
    convert_to_ethiopian, 
    convert_to_gregorian,
    get_today_ethiopian, 
    get_ethiopian_new_year
)

def main():
    print("🇪🇹 Ethiopian Calendar Examples")
    print("=" * 40)
    
    # Example 1: Convert specific dates
    print("📅 Date Conversions:")
    dates_to_test = [
        (2025, 10, 11),  # Your test date
        (2025, 9, 11),   # Ethiopian New Year
        (2025, 1, 7),    # Ethiopian Christmas (Gregorian)
        (2024, 5, 4),    # Ethiopian Easter 2016
    ]
    
    for year, month, day in dates_to_test:
        result = convert_to_ethiopian(year, month, day)
        greg_date = datetime.date(year, month, day)
        print(f"  {greg_date.strftime('%B %d, %Y')} = {result['formatted']}")
    
    print()
    
    # Example 2: Today's information
    print("📍 Today's Ethiopian Calendar:")
    today = get_today_ethiopian()
    print(f"  Gregorian: {today['gregorian_formatted']}")
    print(f"  Ethiopian: {today['ethiopian_date']['formatted']}")
    print(f"  Season: {today['liturgical_season']}")
    print(f"  Fasting: {today['fasting_info']['type']}")
    if today['fasting_info']['is_fasting']:
        print(f"  Rules: {', '.join(today['fasting_info']['rules'])}")
    
    print()
    
    # Example 3: Ethiopian New Year dates
    print("🎉 Ethiopian New Year (Enkutatash) Dates:")
    for year in range(2024, 2027):
        ny_info = get_ethiopian_new_year(year)
        print(f"  {year}: {ny_info['gregorian_formatted']}")
    
    print()
    
    # Example 4: Reverse conversion
    print("🔄 Reverse Conversions (Ethiopian → Gregorian):")
    ethiopian_dates = [
        (2018, 1, 1),   # መስከረም 1, 2018 (New Year)
        (2016, 8, 27),  # ሚያዝያ 27, 2016 (Easter)
        (2018, 2, 1),   # ጥቅምት 1, 2018 (Your test)
    ]
    
    for eth_year, eth_month, eth_day in ethiopian_dates:
        greg_date = convert_to_gregorian(eth_year, eth_month, eth_day)
        eth_month_name = EthiopianCalendar.MONTH_NAMES[eth_month - 1]
        print(f"  {eth_month_name} {eth_day}, {eth_year} ዓ.ም. = {greg_date.strftime('%B %d, %Y')}")
    
    print()
    
    # Example 5: Feast days
    print("⛪ Major Feast Days:")
    feast_dates = [
        (1, 1),   # Enkutatash
        (1, 17),  # Meskel
        (4, 29),  # Genna
        (5, 11),  # Timket
    ]
    
    for month, day in feast_dates:
        feast = EthiopianCalendar.get_feast_info(month, day)
        if feast:
            month_name = EthiopianCalendar.MONTH_NAMES[month - 1]
            print(f"  {month_name} {day}: {feast['name_english']} ({feast['name_amharic']})")
    
    print()
    
    # Example 6: Liturgical seasons
    print("📆 Liturgical Seasons by Month:")
    for i, month_name in enumerate(EthiopianCalendar.MONTH_NAMES, 1):
        season = EthiopianCalendar.get_liturgical_season(i, 15)  # Mid-month
        print(f"  {month_name}: {season}")
    
    print()
    
    # Example 7: Fasting calendar
    print("🍃 Fasting Example (This Week):")
    today = datetime.date.today()
    for i in range(7):
        date = today + datetime.timedelta(days=i)
        eth_date = EthiopianCalendar.gregorian_to_ethiopian(date)
        fasting = EthiopianCalendar.is_fasting_day(date, eth_date)
        
        status = "Fasting" if fasting['is_fasting'] else "Non-Fasting"
        print(f"  {date.strftime('%A, %b %d')}: {status} ({fasting['type']})")
    
    print()
    
    # Example 8: Accuracy verification
    print("✅ Accuracy Test:")
    test_cases = [
        # (Gregorian date, Expected Ethiopian result)
        (datetime.date(2025, 10, 11), "ጥቅምት 1, 2018"),
        (datetime.date(2025, 9, 11), "መስከረም 1, 2018"),
        (datetime.date(2024, 5, 4), "ሚያዝያ 27, 2016"),
    ]
    
    all_correct = True
    for greg_date, expected in test_cases:
        result = EthiopianCalendar.gregorian_to_ethiopian(greg_date)
        actual = f"{result['month_name']} {result['day']}, {result['year']}"
        correct = actual == expected
        if not correct:
            all_correct = False
        
        status = "✅" if correct else "❌"
        print(f"  {status} {greg_date} = {actual}")
    
    print(f"\n🎯 Overall Accuracy: {'Perfect!' if all_correct else 'Issues found'}")
    print("\n" + "=" * 40)
    print("🎉 Standalone Ethiopian Calendar System Ready!")

if __name__ == "__main__":
    main()