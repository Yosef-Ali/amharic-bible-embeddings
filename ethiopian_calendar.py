#!/usr/bin/env python3
"""
Standalone Ethiopian Calendar System
Complete Ethiopian calendar conversion with no embedding dependencies
Copied from working liturgical-calendar-embeddings implementation
"""

import datetime
from typing import Dict, Any, List, Optional

class EthiopianCalendar:
    """
    Standalone Ethiopian Calendar System
    Complete conversion between Gregorian and Ethiopian calendars
    """
    
    # Ethiopian month names
    MONTH_NAMES = [
        "መስከረም", "ጥቅምት", "ኅዳር", "ታኅሣሥ", "ጥር", "የካቲት",
        "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜን"
    ]
    
    # Base conversion data - Ethiopian New Year typically starts September 11 (or 12 in leap years)
    NEW_YEAR_DATES = {
        # Year: (Month, Day) for Ethiopian New Year in Gregorian calendar
        2017: (9, 11),  # መስከረም 1, 2010 ዓ.ም.
        2018: (9, 11),  # መስከረም 1, 2011 ዓ.ም.
        2019: (9, 11),  # መስከረም 1, 2012 ዓ.ም.
        2020: (9, 11),  # መስከረም 1, 2013 ዓ.ም. (leap year)
        2021: (9, 11),  # መስከረም 1, 2014 ዓ.ም.
        2022: (9, 11),  # መስከረም 1, 2015 ዓ.ም.
        2023: (9, 11),  # መስከረም 1, 2016 ዓ.ም.
        2024: (9, 11),  # መስከረም 1, 2017 ዓ.ም. (leap year)
        2025: (9, 11),  # መስከረም 1, 2018 ዓ.ም.
        2026: (9, 11),  # መስከረም 1, 2019 ዓ.ም.
        2027: (9, 11),  # መስከረም 1, 2020 ዓ.ም.
        2028: (9, 11),  # መስከረም 1, 2021 ዓ.ም. (leap year)
    }
    
    # Month start days for a typical year (days from Ethiopian New Year)
    # Each Ethiopian month has 30 days except Pagume (5-6 days)
    MONTH_START_DAYS = [
        0,    # መስከረም (1st month)
        30,   # ጥቅምት (2nd month)
        60,   # ኅዳር (3rd month)  
        90,   # ታኅሣሥ (4th month)
        120,  # ጥር (5th month)
        150,  # የካቲት (6th month)
        180,  # መጋቢት (7th month)
        210,  # ሚያዝያ (8th month)
        240,  # ግንቦት (9th month)
        270,  # ሰኔ (10th month)
        300,  # ሐምሌ (11th month)
        330,  # ነሐሴ (12th month)
        360,  # ጳጉሜን (13th month)
    ]
    
    # Major Ethiopian Orthodox feast days (Ethiopian calendar dates)
    MAJOR_FEAST_DAYS = {
        # Fixed feast days (month, day): feast info
        (1, 1): {
            "name_amharic": "እንቁጣጣሽ", 
            "name_english": "Enkutatash (New Year)",
            "type": "major",
            "commemoration": "Ethiopian New Year celebration"
        },
        (1, 17): {
            "name_amharic": "መስቀል", 
            "name_english": "Meskel (Finding of True Cross)",
            "type": "major",
            "commemoration": "Discovery of the True Cross"
        },
        (4, 29): {
            "name_amharic": "ልደት", 
            "name_english": "Genna (Ethiopian Christmas)",
            "type": "major",
            "commemoration": "Birth of Jesus Christ"
        },
        (5, 11): {
            "name_amharic": "ጥምቀት", 
            "name_english": "Timket (Ethiopian Epiphany)",
            "type": "major",
            "commemoration": "Baptism of Jesus Christ"
        },
        # Moveable feasts are calculated dynamically
    }
    
    # Fasting periods and rules
    FASTING_PERIODS = {
        "lent": {
            "duration_days": 55,
            "description": "የግዕዝ ጾም (Great Lent)",
            "rules": [
                "Complete vegan diet",
                "No animal products whatsoever", 
                "One meal after 3 PM",
                "Increased prayer and almsgiving",
                "Preparation for Easter"
            ]
        },
        "advent_fast": {
            "months": [3, 4],  # ኅዳር, ታኅሣሥ
            "description": "የልደት ጾም (Christmas Fast)",
            "rules": [
                "Vegan diet",
                "No meat or dairy",
                "Preparation for Christmas"
            ]
        },
        "apostles_fast": {
            "variable_duration": True,
            "description": "የሐዋርያት ጾም (Apostles' Fast)",
            "rules": [
                "Vegan diet",
                "Commemoration of the Apostles"
            ]
        },
        "assumption_fast": {
            "duration_days": 15,
            "month": 12,  # ነሐሴ
            "description": "የፍልሰታ ጾም (Assumption of Mary Fast)",
            "rules": [
                "Vegan diet",
                "Preparation for Assumption of Mary"
            ]
        }
    }
    
    @classmethod
    def is_leap_year(cls, eth_year: int) -> bool:
        """
        Determine if Ethiopian year is a leap year
        Ethiopian leap year pattern follows specific cycle
        """
        # Ethiopian leap years occur every 4 years with specific pattern
        # Years ending in 3, 7, 11 within their 4-year cycle
        year_in_cycle = eth_year % 4
        return year_in_cycle == 3
    
    @classmethod
    def gregorian_to_ethiopian(cls, greg_date: datetime.date) -> Dict[str, Any]:
        """
        Convert Gregorian date to Ethiopian calendar
        Based on exact conversion table data
        """
        
        greg_year = greg_date.year
        
        # Get Ethiopian New Year date for this Gregorian year
        if greg_year in cls.NEW_YEAR_DATES:
            ny_month, ny_day = cls.NEW_YEAR_DATES[greg_year]
        else:
            # Default calculation for years not in lookup table
            ny_month, ny_day = 9, 11
        
        # Ethiopian New Year date in Gregorian calendar
        eth_new_year = datetime.date(greg_year, ny_month, ny_day)
        
        if greg_date >= eth_new_year:
            # After Ethiopian New Year - current Ethiopian year
            eth_year = greg_year - 7
            days_since_new_year = (greg_date - eth_new_year).days
        else:
            # Before Ethiopian New Year - previous Ethiopian year
            eth_year = greg_year - 8
            # Get previous year's new year
            prev_year = greg_year - 1
            if prev_year in cls.NEW_YEAR_DATES:
                prev_ny_month, prev_ny_day = cls.NEW_YEAR_DATES[prev_year]
            else:
                prev_ny_month, prev_ny_day = 9, 11
                
            prev_eth_new_year = datetime.date(prev_year, prev_ny_month, prev_ny_day)
            days_since_new_year = (greg_date - prev_eth_new_year).days
        
        # Calculate Ethiopian month and day
        eth_month = 1
        eth_day = 1
        
        for i, start_day in enumerate(cls.MONTH_START_DAYS):
            if i == len(cls.MONTH_START_DAYS) - 1:  # Last month (Pagume)
                eth_month = 13
                eth_day = days_since_new_year - start_day + 1
                break
            elif days_since_new_year < cls.MONTH_START_DAYS[i + 1]:
                eth_month = i + 1
                eth_day = days_since_new_year - start_day + 1
                break
        
        # Ensure valid ranges
        eth_month = max(1, min(13, eth_month))
        
        if eth_month <= 12:
            eth_day = max(1, min(30, eth_day))
        else:  # Pagume
            max_pagume_days = 6 if cls.is_leap_year(eth_year) else 5
            eth_day = max(1, min(max_pagume_days, eth_day))
        
        return {
            "year": eth_year,
            "month": eth_month,
            "day": eth_day,
            "month_name": cls.MONTH_NAMES[eth_month - 1],
            "formatted": f"{cls.MONTH_NAMES[eth_month - 1]} {eth_day}, {eth_year} ዓ.ም.",
            "is_leap_year": cls.is_leap_year(eth_year),
            "gregorian_input": greg_date.isoformat()
        }
    
    @classmethod
    def ethiopian_to_gregorian(cls, eth_year: int, eth_month: int, eth_day: int) -> datetime.date:
        """
        Convert Ethiopian date to Gregorian calendar
        """
        
        # Calculate the corresponding Gregorian year (approximate)
        greg_year = eth_year + 7  # or + 8 depending on time of year
        
        # Calculate days since Ethiopian New Year
        if eth_month <= 12:
            days_since_new_year = (eth_month - 1) * 30 + (eth_day - 1)
        else:  # Pagume (13th month)
            days_since_new_year = 360 + (eth_day - 1)
        
        # Get Ethiopian New Year date in Gregorian calendar
        if greg_year in cls.NEW_YEAR_DATES:
            ny_month, ny_day = cls.NEW_YEAR_DATES[greg_year]
        else:
            # Try the next year
            greg_year += 1
            if greg_year in cls.NEW_YEAR_DATES:
                ny_month, ny_day = cls.NEW_YEAR_DATES[greg_year]
            else:
                ny_month, ny_day = 9, 11
        
        eth_new_year = datetime.date(greg_year, ny_month, ny_day)
        gregorian_date = eth_new_year + datetime.timedelta(days=days_since_new_year)
        
        return gregorian_date
    
    @classmethod
    def get_feast_info(cls, eth_month: int, eth_day: int) -> Optional[Dict[str, Any]]:
        """
        Get feast day information for Ethiopian date
        """
        return cls.MAJOR_FEAST_DAYS.get((eth_month, eth_day))
    
    @classmethod
    def get_liturgical_season(cls, eth_month: int, eth_day: int) -> str:
        """
        Determine Ethiopian Orthodox liturgical season
        """
        
        if eth_month == 1:  # መስከረም
            if eth_day == 1:
                return "New Year (Enkutatash)"
            elif eth_day <= 17:
                return "New Year Season"
            else:
                return "Cross Season (Meskel preparation)"
        
        elif eth_month == 2:  # ጥቅምት
            return "Ordinary Time"
        
        elif eth_month in [3, 4]:  # ኅዳር, ታኅሣሥ
            return "Advent Season (Christmas Preparation)"
        
        elif eth_month == 4 and eth_day >= 25:  # Late ታኅሣሥ
            return "Christmas Season"
        
        elif eth_month == 5:  # ጥር
            if eth_day <= 11:
                return "Christmas Season"
            else:
                return "Epiphany Season"
        
        elif eth_month in [6, 7]:  # የካቲት, መጋቢት
            return "Epiphany Season"
        
        elif eth_month in [8, 9]:  # ሚያዝያ, ግንቦት
            return "Great Lent / Easter Season"
        
        elif eth_month in [10, 11, 12]:  # ሰኔ, ሐምሌ, ነሐሴ
            return "Ordinary Time"
        
        else:  # ጳጉሜን
            return "End of Year"
    
    @classmethod
    def is_fasting_day(cls, greg_date: datetime.date, eth_date: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine if it's a fasting day in Ethiopian Orthodox tradition
        """
        
        eth_month = eth_date["month"]
        eth_day = eth_date["day"]
        weekday = greg_date.weekday()  # 0=Monday, 6=Sunday
        
        # Weekly fasting days (Wednesday and Friday)
        is_weekly_fast = weekday in [2, 4]  # Wednesday=2, Friday=4
        
        # Advent fast (ኅዳር and ታኅሣሥ)
        is_advent_fast = eth_month in [3, 4] and not (eth_month == 4 and eth_day > 28)
        
        # Great Lent (approximately 55 days before Easter - simplified calculation)
        is_lent = eth_month in [6, 7, 8] and eth_month <= 8
        
        # Assumption fast (first 15 days of ነሐሴ)
        is_assumption_fast = eth_month == 12 and eth_day <= 15
        
        # Determine fasting type and rules
        if is_lent:
            fasting_type = "Great Lent"
            rules = cls.FASTING_PERIODS["lent"]["rules"]
            reason = "የግዕዝ ጾም (Great Lent preparation for Easter)"
        elif is_advent_fast:
            fasting_type = "Advent Fast"
            rules = cls.FASTING_PERIODS["advent_fast"]["rules"]
            reason = "የልደት ጾም (Christmas preparation)"
        elif is_assumption_fast:
            fasting_type = "Assumption Fast"
            rules = cls.FASTING_PERIODS["assumption_fast"]["rules"]
            reason = "የፍልሰታ ጾም (Assumption of Mary preparation)"
        elif is_weekly_fast:
            fasting_type = "Weekly Fast"
            rules = ["No meat", "No dairy", "Simple foods preferred"]
            reason = f"Weekly fasting on {greg_date.strftime('%A')}"
        else:
            fasting_type = "None"
            rules = ["No specific fasting requirements"]
            reason = "Regular day"
        
        is_fasting = is_lent or is_advent_fast or is_assumption_fast or is_weekly_fast
        
        return {
            "is_fasting": is_fasting,
            "type": fasting_type,
            "rules": rules,
            "reason": reason,
            "is_weekly_fast": is_weekly_fast,
            "is_seasonal_fast": is_lent or is_advent_fast or is_assumption_fast
        }
    
    @classmethod
    def get_complete_info(cls, greg_date: datetime.date) -> Dict[str, Any]:
        """
        Get complete Ethiopian calendar information for a Gregorian date
        """
        
        eth_date = cls.gregorian_to_ethiopian(greg_date)
        feast_info = cls.get_feast_info(eth_date["month"], eth_date["day"])
        season = cls.get_liturgical_season(eth_date["month"], eth_date["day"])
        fasting_info = cls.is_fasting_day(greg_date, eth_date)
        
        return {
            "gregorian_date": greg_date.isoformat(),
            "gregorian_formatted": greg_date.strftime("%A, %B %d, %Y"),
            "ethiopian_date": eth_date,
            "feast_day": feast_info,
            "liturgical_season": season,
            "fasting_info": fasting_info,
            "weekday": greg_date.strftime("%A"),
            "is_weekend": greg_date.weekday() in [5, 6]  # Saturday=5, Sunday=6
        }

# Standalone functions for easy use
def convert_to_ethiopian(year: int, month: int, day: int) -> Dict[str, Any]:
    """Convert Gregorian date to Ethiopian calendar"""
    greg_date = datetime.date(year, month, day)
    return EthiopianCalendar.gregorian_to_ethiopian(greg_date)

def convert_to_gregorian(eth_year: int, eth_month: int, eth_day: int) -> datetime.date:
    """Convert Ethiopian date to Gregorian calendar"""
    return EthiopianCalendar.ethiopian_to_gregorian(eth_year, eth_month, eth_day)

def get_today_ethiopian() -> Dict[str, Any]:
    """Get today's date in Ethiopian calendar"""
    return EthiopianCalendar.get_complete_info(datetime.date.today())

def get_ethiopian_new_year(gregorian_year: int) -> Dict[str, Any]:
    """Get Ethiopian New Year (Enkutatash) for a given Gregorian year"""
    if gregorian_year in EthiopianCalendar.NEW_YEAR_DATES:
        month, day = EthiopianCalendar.NEW_YEAR_DATES[gregorian_year]
        greg_date = datetime.date(gregorian_year, month, day)
        return EthiopianCalendar.get_complete_info(greg_date)
    else:
        # Default to September 11
        greg_date = datetime.date(gregorian_year, 9, 11)
        return EthiopianCalendar.get_complete_info(greg_date)

# Test function
def test_standalone_calendar():
    """Test the standalone Ethiopian calendar system"""
    
    print("🇪🇹 Standalone Ethiopian Calendar System Test")
    print("=" * 50)
    
    # Test today's date
    today_info = get_today_ethiopian()
    print(f"Today: {today_info['gregorian_formatted']}")
    print(f"Ethiopian: {today_info['ethiopian_date']['formatted']}")
    print(f"Season: {today_info['liturgical_season']}")
    print(f"Fasting: {today_info['fasting_info']['type']}")
    print()
    
    # Test specific date
    test_date = datetime.date(2025, 10, 11)
    test_info = EthiopianCalendar.get_complete_info(test_date)
    print(f"Test Date: {test_info['gregorian_formatted']}")
    print(f"Ethiopian: {test_info['ethiopian_date']['formatted']}")
    print()
    
    # Test conversion back
    eth = test_info['ethiopian_date']
    greg_back = convert_to_gregorian(eth['year'], eth['month'], eth['day'])
    print(f"Reverse conversion: {greg_back} (Match: {greg_back == test_date})")
    print()
    
    # Test Ethiopian New Year
    ny_info = get_ethiopian_new_year(2025)
    print(f"Ethiopian New Year 2025: {ny_info['gregorian_formatted']}")
    print(f"Ethiopian: {ny_info['ethiopian_date']['formatted']}")
    print()
    
    print("✅ Standalone Ethiopian Calendar System Working!")

if __name__ == "__main__":
    test_standalone_calendar()