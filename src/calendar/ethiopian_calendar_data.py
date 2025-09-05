"""
Ethiopian Calendar Conversion System

Implements precise Gregorian ↔ Ethiopian calendar conversion
with support for Ethiopian Orthodox liturgical calculations.
"""

import datetime
from typing import Dict, Any

class EthiopianCalendarData:
    """Core Ethiopian calendar conversion and liturgical calculations."""
    
    # Ethiopian month names in Amharic
    ETHIOPIAN_MONTHS = [
        "መስከረም",    # Meskerem (September)
        "ጥቅምት",    # Tikimit (October)
        "ኅዳር",     # Hedar (November)
        "ታኅሳስ",    # Tahsas (December)
        "ጥር",       # Tir (January)
        "የካቲት",    # Yekatit (February)
        "መጋቢት",    # Megabit (March)
        "ሚያዝያ",    # Miyazya (April)
        "ግንቦት",    # Ginbot (May)
        "ሰኔ",       # Sene (June)
        "ሐምሌ",      # Hamle (July)
        "ነሐሴ",      # Nehasse (August)
        "ጳጉሜ"       # Pagume (leap month)
    ]
    
    # Ethiopian month names in English for reference
    ETHIOPIAN_MONTHS_EN = [
        "Meskerem", "Tikimit", "Hedar", "Tahsas", "Tir", "Yekatit",
        "Megabit", "Miyazya", "Ginbot", "Sene", "Hamle", "Nehasse", "Pagume"
    ]
    
    # Gregorian start dates for Ethiopian months
    # Ethiopian year starts on September 11/12 (Gregorian)
    ETHIOPIAN_NEW_YEAR = {
        'day': 11,
        'month': 9  # September
    }
    
    @staticmethod
    def gregorian_to_ethiopian_precise(greg_date: datetime.date) -> Dict[str, Any]:
        """
        Convert Gregorian date to Ethiopian date with precise calculation.
        
        Args:
            greg_date: Gregorian date to convert
            
        Returns:
            Dictionary with Ethiopian date components
        """
        # Ethiopian calendar is 7 years and 8 months behind Gregorian
        # Ethiopian New Year is on September 11 (or 12 in leap years)
        
        # Calculate Ethiopian year
        # For Gregorian dates from January to August: Ethiopian year = Gregorian year - 8
        # For Gregorian dates from September to December: Ethiopian year = Gregorian year - 7
        # But Ethiopian New Year is September 11, so we need precise calculation
        
        if greg_date.month > 9 or (greg_date.month == 9 and greg_date.day >= 11):
            # After Ethiopian New Year (Sept 11)
            eth_year = greg_date.year - 7
        else:
            # Before Ethiopian New Year
            eth_year = greg_date.year - 8
        
        # Calculate days since Ethiopian New Year (September 11/12)
        # Ethiopian New Year is on September 11 (or 12 in leap years)
        # For dates before Sept 11, use previous year's New Year
        
        if greg_date.month > 9 or (greg_date.month == 9 and greg_date.day >= 11):
            # After Ethiopian New Year - use current year's New Year
            # Adjust for leap years: Ethiopian New Year is Sept 12 in Gregorian leap years
            if EthiopianCalendarData.is_gregorian_leap_year(greg_date.year):
                eth_new_year = datetime.date(greg_date.year, 9, 12)
            else:
                eth_new_year = datetime.date(greg_date.year, 9, 11)
        else:
            # Before Ethiopian New Year - use previous year's New Year
            if EthiopianCalendarData.is_gregorian_leap_year(greg_date.year - 1):
                eth_new_year = datetime.date(greg_date.year - 1, 9, 12)
            else:
                eth_new_year = datetime.date(greg_date.year - 1, 9, 11)
        
        days_since_new_year = (greg_date - eth_new_year).days
        
        # Calculate Ethiopian month (1-13) and day (1-30)
        # Ethiopian months have 30 days each, except Pagume (5-6 days)
        eth_month = min((days_since_new_year // 30) + 1, 13)
        eth_day = (days_since_new_year % 30) + 1
        
        # Handle Pagume (leap month) - the 13th month
        if days_since_new_year >= 360:
            eth_month = 13
            eth_day = days_since_new_year - 359  # Days in Pagume (1-6)
        
        # Get Amharic month name
        month_name = EthiopianCalendarData.ETHIOPIAN_MONTHS[eth_month - 1]
        
        return {
            'year': eth_year,
            'month': eth_month,
            'day': eth_day,
            'month_name': month_name,
            'formatted': f'{month_name} {eth_day}, {eth_year} ዓ.ም.',
            'accuracy': 'calculated'
        }
    
    @staticmethod
    def ethiopian_to_gregorian_precise(eth_year: int, eth_month: int, eth_day: int) -> datetime.date:
        """
        Convert Ethiopian date to Gregorian date.
        
        Args:
            eth_year: Ethiopian year
            eth_month: Ethiopian month (1-13)
            eth_day: Ethiopian day (1-30, 1-5/6 for Pagume)
            
        Returns:
            Gregorian date
        """
        # Calculate Gregorian year
        greg_year = eth_year + 8
        
        # Calculate days since Ethiopian New Year
        days_since_new_year = (eth_month - 1) * 30 + (eth_day - 1)
        
        # Ethiopian New Year in Gregorian calendar
        eth_new_year = datetime.date(greg_year, 9, 11)
        
        # Calculate Gregorian date
        greg_date = eth_new_year + datetime.timedelta(days=days_since_new_year)
        
        # Adjust for year boundary
        if greg_date.month < 9:
            greg_date = datetime.date(greg_year + 1, greg_date.month, greg_date.day)
        
        return greg_date
    
    @staticmethod
    def get_current_ethiopian_date() -> Dict[str, Any]:
        """Get current date in Ethiopian calendar."""
        return EthiopianCalendarData.gregorian_to_ethiopian_precise(datetime.date.today())
    
    @staticmethod
    def is_leap_year_ethiopian(year: int) -> bool:
        """Check if an Ethiopian year is a leap year."""
        # Ethiopian leap years occur every 4 years
        # The Ethiopian calendar follows a similar pattern to Gregorian
        return year % 4 == 3  # Ethiopian leap years are every 4 years, offset by 1
    
    @staticmethod
    def validate_ethiopian_date(year: int, month: int, day: int) -> bool:
        """Validate if an Ethiopian date is valid."""
        if month < 1 or month > 13:
            return False
        if day < 1:
            return False
        
        # Regular months have 30 days
        if month <= 12:
            return day <= 30
        
        # Pagume month (month 13) has 5 or 6 days
        max_days = 6 if EthiopianCalendarData.is_leap_year_ethiopian(year) else 5
        return day <= max_days

    @staticmethod
    def calculate_easter(year: int) -> datetime.date:
        """
        Calculate Easter date for a given Gregorian year using Metonic cycle.
        Ethiopian Orthodox Easter (Fasika) is calculated using the same method
        as Western Easter but may differ by 1-2 weeks due to calendar differences.
        
        Args:
            year: Gregorian year
            
        Returns:
            Gregorian date of Easter Sunday
        """
        # Metonic cycle calculation (standard algorithm)
        # Based on the Computus algorithm for calculating Easter
        
        # Golden number - position in the 19-year Metonic cycle
        golden_number = year % 19 + 1
        
        # Century term
        century = year // 100 + 1
        
        # Corrections for Gregorian calendar
        # Number of years leap years have been introduced
        skipped_leap_years = (3 * century) // 4 - 12
        # Correction for Metonic cycle inaccuracy
        lunar_correction = (8 * century + 5) // 25 - 5
        
        # Find Sunday
        # First calculate the 'epact' (age of moon on January 1)
        epact = (11 * golden_number + 20 + lunar_correction - skipped_leap_years) % 30
        if epact < 0:
            epact += 30
        
        # Adjust epact
        if (epact == 25 and golden_number > 11) or epact == 24:
            epact += 1
        
        # Find full moon
        # March 21 is the ecclesiastical vernal equinox
        days_after_equinox = 44 - epact
        if days_after_equinox < 21:
            days_after_equinox += 30
        
        # Find Sunday after full moon
        # Advance to Sunday
        weekday = (days_after_equinox + 7) - (
            (year + year // 4 + days_after_equinox + 2 - century + century // 4) % 7
        )
        
        # Get month and day
        if weekday > 31:
            month = 4
            day = weekday - 31
        else:
            month = 3
            day = weekday
        
        return datetime.date(year, month, day)
    
    @staticmethod
    def calculate_ethiopian_easter(year: int) -> Dict[str, Any]:
        """
        Calculate Ethiopian Orthodox Easter (Fasika) for a given Gregorian year.
        Ethiopian Easter is typically 1-2 weeks after Western Easter.
        
        Args:
            year: Gregorian year
            
        Returns:
            Dictionary with both Gregorian and Ethiopian Easter dates
        """
        # Calculate Western Easter first
        western_easter = EthiopianCalendarData.calculate_easter(year)
        
        # Ethiopian Orthodox Easter is typically 1-2 weeks after Western Easter
        # This is an approximation - actual calculation may vary by tradition
        ethiopian_easter_greg = western_easter + datetime.timedelta(days=7)
        
        # Convert to Ethiopian calendar
        eth_easter = EthiopianCalendarData.gregorian_to_ethiopian_precise(ethiopian_easter_greg)
        
        return {
            'western_easter_gregorian': western_easter,
            'ethiopian_easter_gregorian': ethiopian_easter_greg,
            'ethiopian_easter': eth_easter,
            'gregorian_year': year,
            'ethiopian_year': eth_easter['year']
        }