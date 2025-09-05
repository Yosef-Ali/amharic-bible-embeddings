#!/usr/bin/env python3
"""
Ethiopian Calendar Conversion Data
Based on precise conversion table for accurate Ethiopian-Gregorian calendar mapping
"""

import datetime
from typing import Dict, Tuple, Optional
import os
import sys

# Import Easter correlation data
try:
    from ethiopian_calendar_system.bahire_hasab import BahireHasab
    from ethiopian_date_converter.ethiopian_date_convertor import to_ethiopian
    HAS_BAHIRE_HASAB = True
    HAS_ETHIOPIAN_DATE_CONVERTER = True
except ImportError:
    HAS_BAHIRE_HASAB = False
    HAS_ETHIOPIAN_DATE_CONVERTER = False

class EthiopianCalendarData:
    """
    Precise Ethiopian calendar conversion data extracted from official conversion tables
    """
    
    # Ethiopian month names
    MONTH_NAMES = [
        "መስከረም", "ጥቅምት", "ኅዳር", "ታኅሣሥ", "ጥር", "የካቲት",
        "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜን"
    ]
    
    # Base conversion data - Ethiopian New Year typically starts September 11 (or 12 in leap years)
    # This data is extracted from the conversion table provided
    NEW_YEAR_DATES = {
        # Year: (Month, Day) for Ethiopian New Year in Gregorian calendar
        2015: (9, 11),  # መስከረም 1, 2008 ዓ.ም.
        2016: (9, 11),  # መስከረም 1, 2009 ዓ.ም. 
        2017: (9, 11),  # መስከረም 1, 2010 ዓ.ም.
        2018: (9, 11),  # መስከረም 1, 2011 ዓ.ም.
        2019: (9, 11),  # መስከረም 1, 2012 ዓ.ም.
        2020: (9, 11),  # መስከረም 1, 2013 ዓ.ም. (leap year)
        2021: (9, 11),  # መስከረም 1, 2014 ዓ.ም.
        2022: (9, 11),  # መስከረም 1, 2015 ዓ.ም.
        2023: (9, 11),  # መስከረም 1, 2016 ዓ.ም.
        2024: (9, 11),  # መስከረም 1, 2017 ዓ.ም. (leap year)
        2025: (9, 11),  # መስከረም 1, 2018 ዓ.ም.
        2026: (9, 11),  # መስከረም 1, 2019 ዓ.ం.
        2027: (9, 11),  # መስከረም 1, 2020 ዓ.ም.
        2028: (9, 11),  # መስከረም 1, 2021 ዓ.ም. (leap year)
    }
    
    # Month start dates for a typical year (days from Ethiopian New Year)
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
        360   # ጳጉሜን (13th month)
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
        (4, 28): { # Corrected Christmas date
            "name_amharic": "ገና", 
            "name_english": "Genna (Ethiopian Christmas)",
            "type": "major",
            "commemoration": "Nativity of Jesus Christ"
        },
        (5, 11): {
            "name_amharic": "ጥምቀት", 
            "name_english": "Timkat (Ethiopian Epiphany)",
            "type": "major",
            "commemoration": "Baptism of Jesus Christ"
        },
        (6, 23): {
            "name_amharic": "የአድዋ ድል በዓል",
            "name_english": "Adwa Victory Day",
            "type": "public",
            "commemoration": "Commemoration of the Battle of Adwa"
        },
        (8, 23): {
            "name_amharic": "የሰራተኞች ቀን",
            "name_english": "Labour Day",
            "type": "public",
            "commemoration": "International Workers' Day"
        },
        (8, 27): {
            "name_amharic": "የአርበኞች ቀን",
            "name_english": "Patriots' Victory Day",
            "type": "public",
            "commemoration": "Commemoration of Ethiopian patriots"
        },
        (9, 20): {
            "name_amharic": "ደርግ የወደቀበት ቀን",
            "name_english": "Downfall of the Derg",
            "type": "public",
            "commemoration": "End of the Derg regime"
        },
    }
    
    # Fasting periods in Ethiopian Orthodox tradition
    FASTING_PERIODS = {
        "great_lent": {
            "duration_days": 55,
            "description": "ዐቢይ ጾም (Great Lent)",
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
                "No animal products",
                "Preparation for Christmas"
            ]
        },
        "assumption_fast": {
            "duration_days": 15,
            "description": "የፍልሰታ ጾም (Assumption Fast)", 
            "rules": [
                "Vegan diet", 
                "Honoring the Virgin Mary"
            ]
        },
        "apostles_fast": {
            "description": "የሐዋርያት ጾም (Apostles Fast)",
            "rules": [
                "Vegan diet",
                "Fish allowed on weekends",
                "Honoring the Apostles"
            ]
        },
        "weekly_fast": {
            "days": [2, 4],  # Wednesday and Friday (0=Monday)
            "description": "ሳንብት እና ዓርብ ጾም (Wednesday and Friday Fast)",
            "rules": [
                "No meat products",
                "No dairy products",
                "Simple foods preferred"
            ]
        }
    }
    
    @classmethod
    def gregorian_to_ethiopian_fallback(cls, greg_date: datetime.date) -> Dict:
        """
        Fallback method for Gregorian to Ethiopian conversion
        """
        greg_year = greg_date.year
        greg_ordinal = greg_date.toordinal()

        current_ny = datetime.date(greg_year, 9, 11)

        if greg_date >= current_ny:
            eth_year = greg_year - 7
            eth_ny_ordinal = current_ny.toordinal()
        else:
            eth_year = greg_year - 8
            prev_ny = datetime.date(greg_year - 1, 9, 11)
            eth_ny_ordinal = prev_ny.toordinal()

        days_since_ny = greg_ordinal - eth_ny_ordinal

        if days_since_ny < 360:
            eth_month = (days_since_ny // 30) + 1
            eth_day = (days_since_ny % 30) + 1
        else:
            eth_month = 13
            eth_day = (days_since_ny - 360) + 1

        return {
            "year": eth_year,
            "month": eth_month,
            "day": eth_day,
            "month_name": cls.MONTH_NAMES[eth_month - 1],
            "formatted": f"{cls.MONTH_NAMES[eth_month - 1]} {eth_day}, {eth_year} ዓ.ም.",
            "conversion_method": "fallback_algorithm"
        }

    @classmethod
    def gregorian_to_ethiopian_precise(cls, greg_date: datetime.date) -> Dict:
        """
        Convert Gregorian date to Ethiopian calendar using the py-ethiopian-date-converter library
        """
        if HAS_ETHIOPIAN_DATE_CONVERTER:
            greg_datetime = datetime.datetime.combine(greg_date, datetime.time.min)
            eth_date = to_ethiopian(greg_datetime)
            return {
                "year": eth_date.year,
                "month": eth_date.month,
                "day": eth_date.day,
                "month_name": cls.MONTH_NAMES[eth_date.month - 1],
                "formatted": f"{cls.MONTH_NAMES[eth_date.month - 1]} {eth_date.day}, {eth_date.year} ዓ.ም.",
                "conversion_method": "py-ethiopian-date-converter"
            }
        else:
            # Fallback to the old implementation if the library is not available
            return cls.gregorian_to_ethiopian_fallback(greg_date)
    
    @classmethod
    def is_ethiopian_leap_year(cls, eth_year: int) -> bool:
        """
        Determine if an Ethiopian year is a leap year
        Ethiopian leap year pattern is every 4 years, similar to Gregorian
        """
        return eth_year % 4 == 3  # Ethiopian leap year pattern
    
    @classmethod
    def get_feast_day(cls, eth_year: int, eth_month: int, eth_day: int) -> Optional[Dict]:
        """
        Get feast day information for Ethiopian calendar date
        """
        feast_key = (eth_month, eth_day)
        if feast_key in cls.MAJOR_FEAST_DAYS:
            return cls.MAJOR_FEAST_DAYS[feast_key]

        # Check for movable holidays
        if HAS_BAHIRE_HASAB:
            calculator = BahireHasab(eth_year)
            fasika_date = calculator.get_fasika()
            good_friday = fasika_date - datetime.timedelta(days=2)

            if eth_month == fasika_date.month and eth_day == fasika_date.day:
                return {
                    "name_amharic": "ትንሳኤ",
                    "name_english": "Easter",
                    "type": "major",
                    "commemoration": "Resurrection of Jesus Christ"
                }
            if eth_month == good_friday.month and eth_day == good_friday.day:
                return {
                    "name_amharic": "ስቅለት",
                    "name_english": "Good Friday",
                    "type": "major",
                    "commemoration": "Crucifixion of Jesus Christ"
                }
        return None
    
    @classmethod
    def is_fasting_day(cls, greg_date: datetime.date, eth_date: Dict) -> Dict:
        """
        Determine fasting status for a given date
        """
        weekday = greg_date.weekday()  # 0 = Monday, 6 = Sunday
        eth_month = eth_date['month']
        eth_day = eth_date['day']
        
        # Check for major feast day exemption
        feast = cls.get_feast_day(eth_date['year'], eth_month, eth_day)
        if feast and feast['type'] == 'major':
            return {
                'is_fasting': False,
                'type': 'feast_exemption',
                'reason': f"Major feast: {feast['name_english']}",
                'rules': ['No fasting on major feast days']
            }
        
        # Weekly fasting (Wednesday and Friday)
        if weekday in [2, 4]:  # Wednesday and Friday
            return {
                'is_fasting': True,
                'type': 'weekly',
                'reason': 'Weekly Wednesday/Friday fast',
                'rules': cls.FASTING_PERIODS['weekly_fast']['rules']
            }
        
        # Advent fast (Christmas preparation)
        if eth_month in [3, 4]:  # ኅዳር, ታኅሣሥ
            return {
                'is_fasting': True,
                'type': 'advent',
                'reason': 'Christmas preparation fast',
                'rules': cls.FASTING_PERIODS['advent_fast']['rules']
            }
        
        # Assumption fast (before August 22 Gregorian ≈ ሐምሌ 16 Ethiopian)
        if eth_month == 12 and eth_day <= 16:  # First half of ሐምሌ
            return {
                'is_fasting': True,
                'type': 'assumption',
                'reason': 'Assumption of Mary fast',
                'rules': cls.FASTING_PERIODS['assumption_fast']['rules']
            }
        
        # No fasting
        return {
            'is_fasting': False,
            'type': 'none',
            'reason': 'Regular day',
            'rules': ['No fasting requirements']
        }
    
    @classmethod
    def get_liturgical_season(cls, eth_month: int, eth_day: int, greg_date: datetime.date = None) -> str:
        """
        Determine Ethiopian Orthodox liturgical season with Easter awareness
        """

        # Enhanced season calculation using Bahire Hasab data if available
        if HAS_BAHIRE_HASAB and greg_date:
            eth_year = cls.gregorian_to_ethiopian_precise(greg_date)['year']
            calculator = BahireHasab(eth_year)
            fasika_date = calculator.get_fasika()

            # Great Lent
            nenewe_start = fasika_date - datetime.timedelta(days=69)
            abiy_tsome_start = nenewe_start + datetime.timedelta(days=14)
            if abiy_tsome_start <= greg_date < fasika_date:
                return "Great Lent"

            # Easter Season
            easter_end = fasika_date + datetime.timedelta(days=49)
            if fasika_date <= greg_date <= easter_end:
                return "Easter Season"

        # Standard season calculation (fallback)
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
            if eth_month == 4 and eth_day >= 25:
                return "Christmas Season (Genna)"
            else:
                return "Advent (Christmas preparation)"

        elif eth_month == 5:  # ጥር
            if eth_day <= 15:
                return "Christmas Season"
            else:
                return "Epiphany Season (Timkat preparation)"

        elif eth_month in [6, 7]:  # የካቲት, መጋቢት
            return "Epiphany Season"

        elif eth_month in [8, 9]:  # ሚያዝያ, ግንቦት
            return "Great Lent / Easter Season"

        elif eth_month in [10, 11, 12]:  # ሰኔ, ሐምሌ, ነሐሴ
            return "Ordinary Time"

        else:  # ጳጉሜን
            return "Pagume (End of Year)"
    
    @classmethod
    def get_easter_info(cls, greg_date: datetime.date) -> Optional[Dict]:
        """
        Get Easter-related information for a given date
        """
        if not HAS_BAHIRE_HASAB:
            return None

        eth_year = cls.gregorian_to_ethiopian_precise(greg_date)['year']
        calculator = BahireHasab(eth_year)
        fasika_date = calculator.get_fasika()

        return {
            "ethiopian_easter": fasika_date,
        }

# Test function
def test_precise_conversion():
    """Test the precise Ethiopian calendar conversion"""
    
    test_dates = [
        datetime.date(2025, 9, 5),   # Today
        datetime.date(2025, 9, 11),  # Ethiopian New Year
        datetime.date(2026, 1, 7),   # Ethiopian Christmas
        datetime.date(2025, 1, 19),  # Ethiopian Epiphany
    ]
    
    for date in test_dates:
        eth_date = EthiopianCalendarData.gregorian_to_ethiopian_precise(date)
        fasting = EthiopianCalendarData.is_fasting_day(date, eth_date)
        feast = EthiopianCalendarData.get_feast_day(eth_date['year'], eth_date['month'], eth_date['day'])
        season = EthiopianCalendarData.get_liturgical_season(eth_date['month'], eth_date['day'])
        
        print(f"\n📅 {date} (Gregorian)")
        print(f"   Ethiopian: {eth_date['formatted']}")
        print(f"   Season: {season}")
        print(f"   Fasting: {'Yes' if fasting['is_fasting'] else 'No'} ({fasting['type']})")
        if feast:
            print(f"   Feast: {feast['name_english']} ({feast['name_amharic']})")

if __name__ == "__main__":
    test_precise_conversion()