#!/usr/bin/env python3
"""
Bahire Hasab - Ethiopian Orthodox Calendar Calculation System
ባሕረ ሃሳብ - "Sea of Ideas"

This module uses the 'bahire-hasab' library to calculate Ethiopian Orthodox Easter (Fasika).
"""

import datetime
from bahire_hasab import BahireHasab as BahireHasabCalculator

class BahireHasab:
    """
    A wrapper class for the bahire-hasab library to calculate Ethiopian Orthodox Easter (Fasika).
    """

    ETHIOPIAN_MONTHS = {
        "መስከረም": 1,
        "ጥቅምት": 2,
        "ኅዳር": 3,
        "ታኅሣሥ": 4,
        "ጥር": 5,
        "የካቲት": 6,
        "መጋቢት": 7,
        "ሚያዝያ": 8,
        "ግንቦት": 9,
        "ሰኔ": 10,
        "ሐምሌ": 11,
        "ነሐሴ": 12,
        "ጳጉሜን": 13,
    }

    def __init__(self, ethiopian_year: int):
        self.calculator = BahireHasabCalculator(year=ethiopian_year)

    def get_fasika(self) -> datetime.date:
        """
        Calculates the date of Ethiopian Orthodox Easter (Fasika).
        """
        tnsae_date_str = self.calculator.tnsae
        # The date is in "month_name day" format, e.g., "ሚያዝያ 27"
        month_name, day_str = tnsae_date_str.split(' ')
        month = self.ETHIOPIAN_MONTHS[month_name]
        day = int(day_str)
        return datetime.date(self.calculator.year, month, day)