#!/usr/bin/env python3
"""
Unified Liturgical Reading Agent
Combines Western Catholic (online) and Ethiopian Orthodox (local) readings
"""

import datetime
import sys
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../liturgical-calendar-embeddings/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../orthodox-reading-agent/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../amharic-bible-embeddings/src'))

from calendar_calculator import LiturgicalCalendarManager
from western_fetcher import WesternCatholicReadingFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EthiopianReading:
    """Ethiopian Orthodox reading structure"""
    reference: str
    amharic_text: str = ""
    english_reference: str = ""
    feast_day: str = ""
    source: str = "ethiopian_orthodox"

@dataclass
class WesternReading:
    """Western Catholic reading structure"""
    reference: str
    source: str = "western_catholic"
    liturgical_season: str = ""
    year_cycle: str = ""

@dataclass
class UnifiedReadings:
    """Combined reading response"""
    date: str
    gregorian_date: str
    ethiopian_date: Dict[str, Any]
    
    # Western readings
    western_first_reading: Optional[WesternReading] = None
    western_psalm: Optional[WesternReading] = None
    western_second_reading: Optional[WesternReading] = None
    western_gospel: Optional[WesternReading] = None
    western_liturgical_info: Optional[Dict] = None
    
    # Ethiopian readings
    ethiopian_old_testament: Optional[EthiopianReading] = None
    ethiopian_epistle: Optional[EthiopianReading] = None
    ethiopian_gospel: Optional[EthiopianReading] = None
    ethiopian_psalm: Optional[EthiopianReading] = None
    ethiopian_liturgical_info: Optional[Dict] = None
    
    # Combined metadata
    fasting_info: Optional[Dict] = None
    saints_commemorations: List[str] = None

class EthiopianReadingCalculator:
    """Calculates Ethiopian Orthodox readings using local calendar and biblical texts"""
    
    def __init__(self):
        self.calendar_manager = LiturgicalCalendarManager()
        
        # Ethiopian Orthodox reading cycle patterns with liturgically appropriate readings
        self.reading_cycles = {
            "ordinary_time": {
                "old_testament_cycle": [
                    ("Genesis", [(1, "1-31"), (2, "4-25"), (3, "1-24"), (4, "1-26"), (9, "8-17")]),
                    ("Exodus", [(3, "1-22"), (14, "10-31"), (19, "1-25"), (20, "1-17")]),
                    ("Isaiah", [(6, "1-13"), (40, "1-31"), (55, "1-11"), (61, "1-11"), (62, "1-12")]),
                    ("Proverbs", [(1, "1-33"), (3, "1-35"), (8, "1-36"), (31, "10-31")]),
                    ("Ecclesiastes", [(3, "1-22"), (12, "1-14")]),
                    ("1 Kings", [(3, "5-28"), (17, "8-24"), (18, "20-39")]),
                    ("2 Kings", [(4, "1-37"), (5, "1-19")]),
                    ("Daniel", [(1, "1-21"), (3, "1-30"), (6, "1-28")])
                ],
                "epistle_cycle": [
                    ("Romans", [(1, "1-17"), (8, "1-39"), (12, "1-21"), (15, "1-33")]),
                    ("1 Corinthians", [(1, "1-31"), (13, "1-13"), (15, "1-58"), (2, "6-16")]),
                    ("2 Corinthians", [(4, "1-18"), (5, "14-21"), (9, "6-15")]),
                    ("Ephesians", [(1, "1-23"), (2, "1-22"), (4, "1-32"), (6, "10-24")]),
                    ("Philippians", [(2, "1-18"), (4, "4-13")]),
                    ("Colossians", [(1, "1-20"), (3, "1-17")]),
                    ("Hebrews", [(1, "1-14"), (11, "1-40"), (12, "1-29"), (13, "1-25")]),
                    ("James", [(1, "2-18"), (2, "14-26"), (3, "1-18")]),
                    ("1 Peter", [(1, "3-25"), (2, "1-25"), (4, "7-19")]),
                    ("1 John", [(3, "1-24"), (4, "7-21"), (5, "1-13")])
                ],
                "gospel_cycle": [
                    ("Matthew", [(5, "1-16"), (6, "9-15"), (11, "25-30"), (25, "31-46"), (28, "16-20")]),
                    ("Mark", [(1, "14-20"), (4, "1-20"), (10, "13-16"), (12, "28-34"), (16, "15-20")]),
                    ("Luke", [(2, "1-20"), (4, "16-21"), (6, "20-26"), (10, "25-37"), (15, "11-32"), (24, "13-35")]),
                    ("John", [(1, "1-18"), (3, "16-21"), (6, "35-51"), (10, "1-18"), (14, "1-14"), (15, "1-17"), (20, "19-31")])
                ]
            },
            "christmas_season": {
                "old_testament": [("Isaiah", 9, "2-7"), ("Isaiah", 7, "10-16"), ("Micah", 5, "1-5"), ("Isaiah", 62, "6-12"), ("Jeremiah", 31, "7-14")],
                "epistle": [("Titus", 2, "11-14"), ("Titus", 3, "4-7"), ("Hebrews", 1, "1-6"), ("Galatians", 4, "4-7"), ("1 John", 4, "7-14")],
                "gospel": [("Luke", 2, "1-20"), ("Matthew", 2, "1-12"), ("Luke", 2, "22-40"), ("Matthew", 2, "13-23"), ("John", 1, "1-18")]
            },
            "epiphany_season": {
                "old_testament": [("Isaiah", 42, "1-9"), ("Isaiah", 49, "1-7"), ("Isaiah", 60, "1-6"), ("Isaiah", 43, "1-7"), ("1 Samuel", 16, "1-13")],
                "epistle": [("Acts", 8, "14-17"), ("1 Corinthians", 1, "1-9"), ("Ephesians", 3, "1-12"), ("Romans", 6, "1-11"), ("Acts", 10, "34-43")],
                "gospel": [("Matthew", 3, "13-17"), ("Mark", 1, "7-11"), ("John", 1, "29-34"), ("Luke", 3, "15-22"), ("Mark", 9, "2-9")]
            },
            "lent_season": {
                "old_testament": [("Joel", 2, "1-17"), ("Isaiah", 58, "1-12"), ("Jeremiah", 1, "4-10"), ("Ezekiel", 36, "24-28"), ("Deuteronomy", 26, "4-10")],
                "epistle": [("2 Corinthians", 5, "20-6:10"), ("Romans", 10, "8-13"), ("Hebrews", 4, "14-16"), ("Romans", 8, "31-39"), ("2 Corinthians", 6, "1-10")],
                "gospel": [("Matthew", 4, "1-11"), ("Mark", 1, "12-15"), ("Luke", 4, "1-13"), ("John", 4, "5-42"), ("Matthew", 17, "1-9")]
            },
            "easter_season": {
                "old_testament": [("Acts", 10, "34-43"), ("Acts", 2, "14-36"), ("Acts", 3, "13-19"), ("Acts", 5, "27-33"), ("Acts", 13, "26-33")],
                "epistle": [("Colossians", 3, "1-4"), ("1 Peter", 1, "3-9"), ("1 Corinthians", 5, "6-8"), ("1 John", 5, "1-6"), ("Revelation", 1, "9-19")],
                "gospel": [("John", 20, "1-18"), ("Matthew", 28, "1-10"), ("Mark", 16, "1-8"), ("Luke", 24, "13-35"), ("John", 21, "1-14")]
            }
        }
        
        # Major Ethiopian Orthodox Feast Days
        self.major_feasts = {
            # Fixed date feasts (Ethiopian calendar)
            (1, 1): {"name": "Enkutatash (New Year)", "type": "major", "readings": "new_year"},
            (4, 29): {"name": "Genna (Christmas)", "type": "major", "readings": "christmas_season"},
            (5, 11): {"name": "Timkat (Epiphany)", "type": "major", "readings": "epiphany_season"},
            (2, 27): {"name": "Kidus Yohannes (St. John Baptist)", "type": "saint", "readings": "saint_john"},
            (8, 16): {"name": "Mariam (Assumption of Mary)", "type": "major", "readings": "assumption"},
            (1, 17): {"name": "Meskel (Finding of True Cross)", "type": "major", "readings": "cross_exaltation"},
            (12, 12): {"name": "Archangel Michael", "type": "archangel", "readings": "archangel"},
            (3, 21): {"name": "Kidus Giorgis (St. George)", "type": "saint", "readings": "saint_george"},
            
            # Moveable feasts (calculated based on Easter)
            "palm_sunday": {"name": "Hosanna (Palm Sunday)", "type": "major", "readings": "palm_sunday"},
            "good_friday": {"name": "Siklet (Good Friday)", "type": "major", "readings": "good_friday"}, 
            "easter": {"name": "Fasika (Easter)", "type": "major", "readings": "easter_season"},
            "ascension": {"name": "Erget (Ascension)", "type": "major", "readings": "ascension"},
            "pentecost": {"name": "Parakletos (Pentecost)", "type": "major", "readings": "pentecost"}
        }
    
    def get_ethiopian_readings(self, date: datetime.date) -> Dict[str, Any]:
        """Get Ethiopian Orthodox readings for date"""
        
        try:
            # Get Ethiopian calendar information
            daily_info = self.calendar_manager.get_daily_info(date)
            eth_info = daily_info['ethiopian']
            eth_date = eth_info['date']
            
            # Check for major feast days first
            feast_info = self._check_feast_day(date, eth_date)
            
            # Calculate reading cycle position
            day_of_year = date.timetuple().tm_yday
            
            # Determine liturgical season and appropriate readings
            season = eth_info['season']
            
            if feast_info:
                # Use feast readings for major celebrations
                readings = self._get_feast_readings(feast_info, day_of_year)
                season = f"{season} - {feast_info['name']}"
            elif self._is_fasting_period(eth_info):
                readings = self._get_fasting_readings(day_of_year, season)
            else:
                # Use seasonal readings for special seasons, ordinary for regular time
                readings = self._get_seasonal_readings(day_of_year, season)
            
            # Add Ethiopian calendar information
            readings['ethiopian_date'] = eth_date
            readings['ethiopian_season'] = season
            readings['fasting_info'] = self._get_enhanced_fasting_info(date, eth_info, feast_info)
            readings['feast_day'] = feast_info['name'] if feast_info else None
            
            return readings
            
        except Exception as e:
            logger.error(f"Error calculating Ethiopian readings: {e}")
            return self._get_fallback_ethiopian_readings(date)
    
    def _check_feast_day(self, greg_date: datetime.date, eth_date: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if date is a major Ethiopian Orthodox feast day"""
        
        eth_month = eth_date['month']
        eth_day = eth_date['day']
        
        # Check fixed date feasts
        feast_key = (eth_month, eth_day)
        if feast_key in self.major_feasts:
            return self.major_feasts[feast_key]
        
        # TODO: Add moveable feast calculations (Easter-based)
        # For now, return None for moveable feasts
        
        return None
    
    def _get_feast_readings(self, feast_info: Dict[str, Any], day_of_year: int) -> Dict[str, EthiopianReading]:
        """Get readings for major feast days"""
        
        feast_type = feast_info['type']
        feast_name = feast_info['name']
        
        # Special readings for major feasts
        if "Christmas" in feast_name or "Genna" in feast_name:
            return {
                'old_testament': EthiopianReading(
                    reference="Isaiah 9:2-7",
                    english_reference="Isaiah 9:2-7",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'epistle': EthiopianReading(
                    reference="Titus 2:11-14",
                    english_reference="Titus 2:11-14",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'gospel': EthiopianReading(
                    reference="Luke 2:1-20",
                    english_reference="Luke 2:1-20",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'psalm': EthiopianReading(
                    reference="Psalm 96:1-13",
                    english_reference="Psalm 96:1-13",
                    source="ethiopian_orthodox_feast"
                )
            }
        
        elif "Epiphany" in feast_name or "Timkat" in feast_name:
            return {
                'old_testament': EthiopianReading(
                    reference="Isaiah 60:1-6",
                    english_reference="Isaiah 60:1-6",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'epistle': EthiopianReading(
                    reference="Acts 8:14-17",
                    english_reference="Acts 8:14-17",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'gospel': EthiopianReading(
                    reference="Matthew 3:13-17",
                    english_reference="Matthew 3:13-17",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'psalm': EthiopianReading(
                    reference="Psalm 29:1-11",
                    english_reference="Psalm 29:1-11",
                    source="ethiopian_orthodox_feast"
                )
            }
        
        elif "New Year" in feast_name or "Enkutatash" in feast_name:
            return {
                'old_testament': EthiopianReading(
                    reference="Ecclesiastes 3:1-22",
                    english_reference="Ecclesiastes 3:1-22",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'epistle': EthiopianReading(
                    reference="2 Corinthians 5:17-21",
                    english_reference="2 Corinthians 5:17-21",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'gospel': EthiopianReading(
                    reference="Matthew 6:25-34",
                    english_reference="Matthew 6:25-34",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'psalm': EthiopianReading(
                    reference="Psalm 65:1-13",
                    english_reference="Psalm 65:1-13",
                    source="ethiopian_orthodox_feast"
                )
            }
        
        elif "Meskel" in feast_name or "Cross" in feast_name:
            return {
                'old_testament': EthiopianReading(
                    reference="1 Kings 8:22-30",
                    english_reference="1 Kings 8:22-30",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'epistle': EthiopianReading(
                    reference="1 Corinthians 1:18-25",
                    english_reference="1 Corinthians 1:18-25",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'gospel': EthiopianReading(
                    reference="John 3:13-17",
                    english_reference="John 3:13-17",
                    feast_day=feast_name,
                    source="ethiopian_orthodox_feast"
                ),
                'psalm': EthiopianReading(
                    reference="Psalm 98:1-9",
                    english_reference="Psalm 98:1-9",
                    source="ethiopian_orthodox_feast"
                )
            }
        
        else:
            # Default feast readings
            return self._get_seasonal_readings(day_of_year, "Feast Day")
    
    def _get_enhanced_fasting_info(self, greg_date: datetime.date, eth_info: Dict[str, Any], feast_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get enhanced fasting information with more detail"""
        
        weekday = greg_date.weekday()  # 0 = Monday, 6 = Sunday
        eth_month = eth_info['date']['month']
        
        # No fasting on major feast days
        if feast_info and feast_info['type'] == 'major':
            return {
                'is_fasting': False,
                'fasting_type': 'feast_dispensation',
                'fasting_rules': ['No fasting - Major feast day'],
                'feast_day': feast_info['name']
            }
        
        # Weekly fasting days (Wednesday and Friday)
        wednesday_friday = weekday in [2, 4]  # Wednesday and Friday
        
        # Major fasting periods
        is_great_lent = eth_info['season'] == "Great Lent / Easter"
        is_advent_fast = eth_month in [3, 4]  # ኅዳር and ታኅሣሥ (pre-Christmas)
        is_assumption_fast = eth_month == 12 and greg_date.day <= 22  # Before August 22
        is_apostles_fast = eth_month in [9, 10]  # After Pentecost
        
        # Determine fasting status
        if is_great_lent:
            fasting_type = "great_lent"
            is_fasting = True
            rules = [
                "Complete abstinence from animal products",
                "No dairy, eggs, or meat",
                "One meal after 3 PM",
                "Increased prayer and almsgiving",
                "Spiritual preparation for Easter"
            ]
        elif is_advent_fast:
            fasting_type = "advent_fast"
            is_fasting = True
            rules = [
                "No animal products",
                "No dairy products",
                "Simple plant-based foods only",
                "Preparation for Christmas celebration"
            ]
        elif is_assumption_fast:
            fasting_type = "assumption_fast"
            is_fasting = True
            rules = [
                "Vegan diet only",
                "No animal products",
                "Honoring the Virgin Mary"
            ]
        elif is_apostles_fast:
            fasting_type = "apostles_fast"
            is_fasting = True
            rules = [
                "Vegan diet",
                "No animal products except fish on weekends",
                "Honoring the Apostles"
            ]
        elif wednesday_friday:
            fasting_type = "weekly"
            is_fasting = True
            rules = [
                "No meat products",
                "No dairy products",
                "Simple foods preferred",
                "Weekly spiritual discipline"
            ]
        else:
            fasting_type = "none"
            is_fasting = False
            rules = ["No specific fasting requirements"]
        
        return {
            'is_fasting': is_fasting,
            'fasting_type': fasting_type,
            'fasting_rules': rules,
            'weekly_fast_day': wednesday_friday,
            'seasonal_fast': fasting_type not in ['weekly', 'none']
        }
    
    def _is_fasting_period(self, eth_info: Dict) -> bool:
        """Check if date falls in major fasting period"""
        season = eth_info['season']
        fasting_info = eth_info.get('is_fasting_day', {})
        
        return (season == "Great Lent / Easter" or 
                fasting_info.get('fasting_type') == 'seasonal')
    
    def _get_ordinary_readings(self, day_of_year: int, season: str) -> Dict[str, EthiopianReading]:
        """Calculate readings for ordinary time"""
        
        cycles = self.reading_cycles["ordinary_time"]
        
        # Cycle through readings based on day of year
        ot_books = cycles["old_testament_cycle"]
        epistle_books = cycles["epistle_cycle"] 
        gospel_books = cycles["gospel_cycle"]
        
        ot_index = day_of_year % len(ot_books)
        epistle_index = day_of_year % len(epistle_books)
        gospel_index = day_of_year % len(gospel_books)
        
        # Get specific readings from cycles
        ot_book, ot_readings = ot_books[ot_index]
        ot_reading_index = day_of_year % len(ot_readings)
        ot_chapter, ot_verses = ot_readings[ot_reading_index]
        
        epistle_book, epistle_readings = epistle_books[epistle_index]
        epistle_reading_index = day_of_year % len(epistle_readings)
        epistle_chapter, epistle_verses = epistle_readings[epistle_reading_index]
        
        gospel_book, gospel_readings = gospel_books[gospel_index]
        gospel_reading_index = day_of_year % len(gospel_readings)
        gospel_chapter, gospel_verses = gospel_readings[gospel_reading_index]
        
        return {
            'old_testament': EthiopianReading(
                reference=f"{ot_book} {ot_chapter}:{ot_verses}",
                english_reference=f"{ot_book} {ot_chapter}:{ot_verses}",
                source="ethiopian_orthodox_ordinary"
            ),
            'epistle': EthiopianReading(
                reference=f"{epistle_book} {epistle_chapter}:{epistle_verses}",
                english_reference=f"{epistle_book} {epistle_chapter}:{epistle_verses}", 
                source="ethiopian_orthodox_ordinary"
            ),
            'gospel': EthiopianReading(
                reference=f"{gospel_book} {gospel_chapter}:{gospel_verses}",
                english_reference=f"{gospel_book} {gospel_chapter}:{gospel_verses}",
                source="ethiopian_orthodox_ordinary"
            ),
            'psalm': EthiopianReading(
                reference=f"Psalm {(day_of_year % 150) + 1}:1-12",
                english_reference=f"Psalm {(day_of_year % 150) + 1}:1-12",
                source="ethiopian_orthodox_ordinary"
            )
        }
    
    def _get_seasonal_readings(self, day_of_year: int, season: str) -> Dict[str, EthiopianReading]:
        """Get readings for specific liturgical seasons"""
        
        # Map Ethiopian seasons to reading cycles
        if "Christmas" in season:
            cycle_key = "christmas_season"
        elif "Epiphany" in season:
            cycle_key = "epiphany_season"
        elif "Lent" in season or "Easter" in season:
            cycle_key = "lent_season"
        else:
            return self._get_ordinary_readings(day_of_year, season)
        
        if cycle_key in self.reading_cycles:
            readings_cycle = self.reading_cycles[cycle_key]
            
            # Select readings based on day
            ot_readings = readings_cycle["old_testament"]
            epistle_readings = readings_cycle["epistle"]
            gospel_readings = readings_cycle["gospel"]
            
            ot_index = day_of_year % len(ot_readings)
            epistle_index = day_of_year % len(epistle_readings)
            gospel_index = day_of_year % len(gospel_readings)
            
            ot_book, ot_chapter, ot_verses = ot_readings[ot_index]
            epistle_book, epistle_chapter, epistle_verses = epistle_readings[epistle_index]
            gospel_book, gospel_chapter, gospel_verses = gospel_readings[gospel_index]
            
            return {
                'old_testament': EthiopianReading(
                    reference=f"{ot_book} {ot_chapter}:{ot_verses}",
                    english_reference=f"{ot_book} {ot_chapter}:{ot_verses}",
                    feast_day=season,
                    source=f"ethiopian_orthodox_{cycle_key}"
                ),
                'epistle': EthiopianReading(
                    reference=f"{epistle_book} {epistle_chapter}:{epistle_verses}",
                    english_reference=f"{epistle_book} {epistle_chapter}:{epistle_verses}",
                    feast_day=season,
                    source=f"ethiopian_orthodox_{cycle_key}"
                ),
                'gospel': EthiopianReading(
                    reference=f"{gospel_book} {gospel_chapter}:{gospel_verses}",
                    english_reference=f"{gospel_book} {gospel_chapter}:{gospel_verses}",
                    feast_day=season,
                    source=f"ethiopian_orthodox_{cycle_key}"
                ),
                'psalm': EthiopianReading(
                    reference=f"Psalm {(day_of_year % 150) + 1}:1-12",
                    english_reference=f"Psalm {(day_of_year % 150) + 1}:1-12",
                    source=f"ethiopian_orthodox_{cycle_key}"
                )
            }
        
        return self._get_ordinary_readings(day_of_year, season)
    
    def _get_fasting_readings(self, day_of_year: int, season: str) -> Dict[str, EthiopianReading]:
        """Calculate readings for fasting periods"""
        
        # Use seasonal readings for fasting periods
        return self._get_seasonal_readings(day_of_year, season)
    
    def _get_fallback_ethiopian_readings(self, date: datetime.date) -> Dict[str, Any]:
        """Provide fallback readings when calculation fails"""
        
        day_of_year = date.timetuple().tm_yday
        
        return {
            'old_testament': EthiopianReading(
                reference=f"Isaiah {(day_of_year % 66) + 1}:1-10",
                source="ethiopian_orthodox_fallback"
            ),
            'epistle': EthiopianReading(
                reference=f"Romans {(day_of_year % 16) + 1}:1-15",
                source="ethiopian_orthodox_fallback"
            ),
            'gospel': EthiopianReading(
                reference=f"Matthew {(day_of_year % 28) + 1}:1-20",
                source="ethiopian_orthodox_fallback"
            ),
            'ethiopian_date': {'formatted': f'Ethiopian date calculation failed for {date}'},
            'fasting_info': {'is_fasting': False, 'note': 'Calculation unavailable'}
        }

class LiturgicalReadingAgent:
    """
    Unified agent for Western Catholic and Ethiopian Orthodox readings
    """
    
    def __init__(self):
        self.western_fetcher = WesternCatholicReadingFetcher()
        self.ethiopian_calculator = EthiopianReadingCalculator()
        self.calendar_manager = LiturgicalCalendarManager()
        
        logger.info("🕊️ Liturgical Reading Agent initialized")
    
    def get_daily_readings(self, date: datetime.date = None) -> UnifiedReadings:
        """Get comprehensive readings for both traditions"""
        
        if date is None:
            date = datetime.date.today()
        
        logger.info(f"📅 Getting unified readings for {date}")
        
        try:
            # Get calendar information
            calendar_info = self.calendar_manager.get_daily_info(date)
            
            # Get Western readings (online)
            western_readings = self.get_western_readings(date)
            
            # Get Ethiopian readings (calculated locally)
            ethiopian_readings = self.get_ethiopian_readings(date)
            
            # Combine into unified response
            unified = UnifiedReadings(
                date=date.isoformat(),
                gregorian_date=calendar_info['gregorian_date'],
                ethiopian_date=calendar_info['ethiopian']['date'],
                fasting_info=calendar_info['ethiopian']['is_fasting_day'],
                saints_commemorations=[]
            )
            
            # Add Western readings
            if western_readings:
                unified.western_first_reading = WesternReading(
                    reference=western_readings.get('first_reading', 'Not available'),
                    source=western_readings.get('source', 'unknown'),
                    liturgical_season=western_readings.get('liturgical_season', 'Unknown')
                )
                
                unified.western_psalm = WesternReading(
                    reference=western_readings.get('psalm', 'Not available'),
                    source=western_readings.get('source', 'unknown')
                )
                
                unified.western_gospel = WesternReading(
                    reference=western_readings.get('gospel', 'Not available'),
                    source=western_readings.get('source', 'unknown'),
                    liturgical_season=western_readings.get('liturgical_season', 'Unknown')
                )
                
                if 'second_reading' in western_readings:
                    unified.western_second_reading = WesternReading(
                        reference=western_readings['second_reading'],
                        source=western_readings.get('source', 'unknown')
                    )
                
                unified.western_liturgical_info = calendar_info['western']
            
            # Add Ethiopian readings
            if ethiopian_readings:
                if 'old_testament' in ethiopian_readings:
                    unified.ethiopian_old_testament = ethiopian_readings['old_testament']
                if 'epistle' in ethiopian_readings:
                    unified.ethiopian_epistle = ethiopian_readings['epistle']
                if 'gospel' in ethiopian_readings:
                    unified.ethiopian_gospel = ethiopian_readings['gospel']
                if 'psalm' in ethiopian_readings:
                    unified.ethiopian_psalm = ethiopian_readings['psalm']
                
                unified.ethiopian_liturgical_info = calendar_info['ethiopian']
            
            logger.info("✅ Successfully combined Western + Ethiopian readings")
            return unified
            
        except Exception as e:
            logger.error(f"Error getting unified readings: {e}")
            return self._get_fallback_unified_readings(date)
    
    def get_western_readings(self, date: datetime.date = None) -> Optional[Dict]:
        """Get Western Catholic readings only"""
        
        if date is None:
            date = datetime.date.today()
        
        logger.info(f"🌍 Getting Western Catholic readings for {date}")
        
        try:
            return self.western_fetcher.get_daily_readings(date)
        except Exception as e:
            logger.error(f"Error fetching Western readings: {e}")
            return None
    
    def get_ethiopian_readings(self, date: datetime.date = None) -> Optional[Dict]:
        """Get Ethiopian Orthodox readings only"""
        
        if date is None:
            date = datetime.date.today()
        
        logger.info(f"⛪ Getting Ethiopian Orthodox readings for {date}")
        
        try:
            return self.ethiopian_calculator.get_ethiopian_readings(date)
        except Exception as e:
            logger.error(f"Error calculating Ethiopian readings: {e}")
            return None
    
    def compare_readings(self, date: datetime.date = None) -> Dict[str, Any]:
        """Compare readings between Western and Ethiopian traditions"""
        
        unified = self.get_daily_readings(date)
        
        comparison = {
            'date': unified.date,
            'western_gospel': unified.western_gospel.reference if unified.western_gospel else None,
            'ethiopian_gospel': unified.ethiopian_gospel.reference if unified.ethiopian_gospel else None,
            'gospel_match': False,
            'season_comparison': {
                'western_season': unified.western_liturgical_info.get('season_info', {}).get('season') if unified.western_liturgical_info else None,
                'ethiopian_season': unified.ethiopian_liturgical_info.get('season') if unified.ethiopian_liturgical_info else None
            },
            'fasting_status': {
                'western_fasting': 'Lent' in str(unified.western_liturgical_info.get('season_info', {}).get('season', '')) if unified.western_liturgical_info else False,
                'ethiopian_fasting': unified.fasting_info.get('is_fasting', False) if unified.fasting_info else False
            }
        }
        
        # Check for Gospel similarities
        if (unified.western_gospel and unified.ethiopian_gospel and 
            unified.western_gospel.reference and unified.ethiopian_gospel.reference):
            
            western_ref = unified.western_gospel.reference.lower()
            ethiopian_ref = unified.ethiopian_gospel.reference.lower()
            
            # Simple matching - same book
            western_book = western_ref.split()[0] if western_ref else ""
            ethiopian_book = ethiopian_ref.split()[0] if ethiopian_ref else ""
            
            comparison['gospel_match'] = western_book == ethiopian_book
        
        return comparison
    
    def _get_fallback_unified_readings(self, date: datetime.date) -> UnifiedReadings:
        """Provide fallback readings when both systems fail"""
        
        return UnifiedReadings(
            date=date.isoformat(),
            gregorian_date=date.isoformat(),
            ethiopian_date={'formatted': 'Calculation unavailable'},
            western_first_reading=WesternReading(
                reference="Fallback reading - service unavailable",
                source="fallback"
            ),
            western_gospel=WesternReading(
                reference="Fallback Gospel - service unavailable", 
                source="fallback"
            ),
            ethiopian_gospel=EthiopianReading(
                reference="Fallback Ethiopian Gospel - calculation unavailable",
                source="fallback"
            ),
            fasting_info={'is_fasting': False, 'note': 'Information unavailable'},
            saints_commemorations=[]
        )

# Test function
def test_unified_agent():
    """Test the unified reading agent"""
    
    print("🕊️ Testing Unified Liturgical Reading Agent")
    print("=" * 50)
    
    agent = LiturgicalReadingAgent()
    
    # Test unified readings for today
    today = datetime.date.today()
    print(f"📅 Getting readings for {today}")
    
    unified = agent.get_daily_readings(today)
    
    print(f"\n🗓️ Date Information:")
    print(f"   Gregorian: {unified.gregorian_date}")
    print(f"   Ethiopian: {unified.ethiopian_date.get('formatted', 'N/A')}")
    
    print(f"\n🌍 Western Catholic Readings:")
    if unified.western_first_reading:
        print(f"   First Reading: {unified.western_first_reading.reference}")
    if unified.western_psalm:
        print(f"   Psalm: {unified.western_psalm.reference}")
    if unified.western_second_reading:
        print(f"   Second Reading: {unified.western_second_reading.reference}")
    if unified.western_gospel:
        print(f"   Gospel: {unified.western_gospel.reference}")
        print(f"   Season: {unified.western_gospel.liturgical_season}")
    
    print(f"\n⛪ Ethiopian Orthodox Readings:")
    if unified.ethiopian_old_testament:
        print(f"   Old Testament: {unified.ethiopian_old_testament.reference}")
    if unified.ethiopian_epistle:
        print(f"   Epistle: {unified.ethiopian_epistle.reference}")
    if unified.ethiopian_gospel:
        print(f"   Gospel: {unified.ethiopian_gospel.reference}")
    if unified.ethiopian_psalm:
        print(f"   Psalm: {unified.ethiopian_psalm.reference}")
    
    print(f"\n🍃 Fasting Information:")
    if unified.fasting_info:
        is_fasting = unified.fasting_info.get('is_fasting', False)
        fasting_type = unified.fasting_info.get('fasting_type', 'none')
        print(f"   Ethiopian Fasting: {'Yes' if is_fasting else 'No'} ({fasting_type})")
    
    # Test comparison
    print(f"\n🔄 Tradition Comparison:")
    comparison = agent.compare_readings(today)
    print(f"   Gospel books match: {comparison['gospel_match']}")
    print(f"   Western season: {comparison['season_comparison']['western_season']}")
    print(f"   Ethiopian season: {comparison['season_comparison']['ethiopian_season']}")
    
    return unified

if __name__ == "__main__":
    test_unified_agent()