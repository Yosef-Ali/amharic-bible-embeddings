#!/usr/bin/env python3
"""
Integrated Liturgical Reading System for Amharic Bible Embeddings
Combines Ethiopian calendar with Amharic biblical text retrieval
"""

import datetime
import sys
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .ethiopian_calendar_data import EthiopianCalendarData
from .calendar_calculator import LiturgicalCalendarManager

# Import Bible search if available
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
    from src.vector_db.chroma_manager import ChromaManager
    from src.qa.bible_qa_system import BibleQASystem
    HAS_BIBLE_SEARCH = True
except ImportError:
    HAS_BIBLE_SEARCH = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LiturgicalReading:
    """Structure for liturgical readings with Amharic text support"""
    reference: str
    amharic_text: str = ""
    english_reference: str = ""
    feast_day: str = ""
    source: str = ""
    confidence: float = 0.0

@dataclass  
class DailyLiturgicalInfo:
    """Complete daily liturgical information"""
    gregorian_date: str
    ethiopian_date: Dict[str, Any]
    
    # Readings
    old_testament: Optional[LiturgicalReading] = None
    psalm: Optional[LiturgicalReading] = None
    epistle: Optional[LiturgicalReading] = None
    gospel: Optional[LiturgicalReading] = None
    
    # Liturgical info
    liturgical_season: str = ""
    feast_info: Optional[Dict[str, Any]] = None
    fasting_info: Optional[Dict[str, Any]] = None
    
    # Colors and metadata
    liturgical_color: str = "green"
    saints_commemorations: List[str] = None

class AmharicLiturgicalSystem:
    """
    Integrated liturgical system combining Ethiopian calendar with Amharic Bible embeddings
    """
    
    def __init__(self, use_embeddings: bool = True):
        self.calendar_manager = LiturgicalCalendarManager()
        self.use_embeddings = use_embeddings and HAS_BIBLE_SEARCH
        
        # Initialize Bible search system if available
        if self.use_embeddings:
            try:
                self.bible_qa = BibleQASystem()
                logger.info("✅ Amharic Bible embeddings integrated")
            except Exception as e:
                logger.warning(f"⚠️ Bible embeddings not available: {e}")
                self.use_embeddings = False
        
        # Ethiopian Orthodox reading patterns
        self.reading_patterns = {
            "ordinary_time": {
                "old_testament": [
                    "ዘፍጥረት 1:1-31", "ዘፍጥረት 2:4-25", "ዘፍጥረት 3:1-24",
                    "ዘኅልቀት 3:1-22", "ዘኅልቀት 14:10-31", "ዘኅልቀት 19:1-25",
                    "የዕሳይያስ 6:1-13", "የዕሳይያስ 40:1-31", "የዕሳይያስ 55:1-11"
                ],
                "epistles": [
                    "ወደ ሮሜ ሰዎች 1:1-17", "ወደ ሮሜ ሰዎች 8:1-39", "ወደ ሮሜ ሰዎች 12:1-21",
                    "1ኛ ወደ ቆሮንቶስ ሰዎች 1:1-31", "1ኛ ወደ ቆሮንቶስ ሰዎች 13:1-13",
                    "ወደ ኤፌሶን ሰዎች 1:1-23", "ወደ ኤፌሶን ሰዎች 4:1-32"
                ],
                "gospels": [
                    "የማቴዎስ ወንጌል 5:1-16", "የማቴዎስ ወንጌል 6:9-15", "የማቴዎስ ወንጌል 25:31-46",
                    "የማርቆስ ወንጌል 1:14-20", "የማርቆስ ወንጌል 10:13-16",
                    "የሉቃስ ወንጌል 2:1-20", "የሉቃስ ወንጌል 4:16-21", "የሉቃስ ወንጌል 15:11-32",
                    "የዮሐንስ ወንጌል 1:1-18", "የዮሐንስ ወንጌል 3:16-21", "የዮሐንስ ወንጌል 14:1-14"
                ]
            },
            "feast_days": {
                "enkutatash": {
                    "old_testament": "የተዋሕዶ 3:1-22",
                    "epistle": "2ኛ ወደ ቆሮንቶስ ሰዎች 5:17-21", 
                    "gospel": "የማቴዎስ ወንጌል 6:25-34"
                },
                "genna": {
                    "old_testament": "የዕሳይያስ 9:2-7",
                    "epistle": "ወደ ቲቶ 2:11-14",
                    "gospel": "የሉቃስ ወንጌል 2:1-20"
                },
                "timkat": {
                    "old_testament": "የዕሳይያስ 60:1-6",
                    "epistle": "የሐዋርያት ሥራ 8:14-17",
                    "gospel": "የማቴዎስ ወንጌል 3:13-17"
                }
            }
        }
    
    def get_daily_readings(self, date: datetime.date = None) -> DailyLiturgicalInfo:
        """Get complete daily liturgical information with Amharic texts"""
        
        if date is None:
            date = datetime.date.today()
        
        logger.info(f"📅 Getting liturgical info for {date}")
        
        # Get calendar information
        calendar_info = self.calendar_manager.get_daily_info(date)
        eth_date = calendar_info['ethiopian']['date']
        
        # Check for feast days
        feast_info = EthiopianCalendarData.get_feast_day(eth_date['year'], eth_date['month'], eth_date['day'])
        
        # Get appropriate readings
        readings = self._get_readings_for_date(date, eth_date, feast_info)
        
        # Get fasting information
        fasting_info = EthiopianCalendarData.is_fasting_day(date, eth_date)
        
        # Get enhanced liturgical season with Easter awareness
        liturgical_season = EthiopianCalendarData.get_liturgical_season(
            eth_date['month'], eth_date['day'], date
        )
        
        # Get Easter information if available
        easter_info = EthiopianCalendarData.get_easter_info(date)
        
        return DailyLiturgicalInfo(
            gregorian_date=date.isoformat(),
            ethiopian_date=eth_date,
            old_testament=readings.get('old_testament'),
            psalm=readings.get('psalm'),
            epistle=readings.get('epistle'),
            gospel=readings.get('gospel'),
            liturgical_season=liturgical_season,
            feast_info=feast_info,
            fasting_info=fasting_info,
            liturgical_color=self._get_liturgical_color(date, feast_info, fasting_info, easter_info),
            saints_commemorations=[]
        )
    
    def _get_readings_for_date(self, date: datetime.date, eth_date: Dict[str, Any], feast_info: Optional[Dict[str, Any]]) -> Dict[str, LiturgicalReading]:
        """Get readings for specific date with Amharic text retrieval"""
        
        readings = {}
        
        if feast_info:
            # Get feast-specific readings
            feast_key = self._get_feast_key(feast_info['name_english'])
            if feast_key in self.reading_patterns['feast_days']:
                feast_readings = self.reading_patterns['feast_days'][feast_key]
                
                readings['old_testament'] = self._create_reading(
                    feast_readings['old_testament'], 
                    feast_info['name_english']
                )
                readings['epistle'] = self._create_reading(
                    feast_readings['epistle'], 
                    feast_info['name_english']
                )
                readings['gospel'] = self._create_reading(
                    feast_readings['gospel'], 
                    feast_info['name_english']
                )
        else:
            # Get ordinary time readings
            day_of_year = date.timetuple().tm_yday
            patterns = self.reading_patterns['ordinary_time']
            
            readings['old_testament'] = self._create_reading(
                patterns['old_testament'][day_of_year % len(patterns['old_testament'])],
                "Ordinary Time"
            )
            readings['epistle'] = self._create_reading(
                patterns['epistles'][day_of_year % len(patterns['epistles'])],
                "Ordinary Time"
            )
            readings['gospel'] = self._create_reading(
                patterns['gospels'][day_of_year % len(patterns['gospels'])],
                "Ordinary Time"
            )
        
        # Add psalm (always)
        psalm_number = (date.timetuple().tm_yday % 150) + 1
        readings['psalm'] = self._create_reading(f"መዝሙረ ዳዊት {psalm_number}:1-12", "Daily Psalm")
        
        return readings
    
    def _create_reading(self, reference: str, source: str) -> LiturgicalReading:
        """Create a reading with Amharic text if available"""
        
        # Try to get Amharic text from embeddings
        amharic_text = ""
        confidence = 0.0
        
        if self.use_embeddings:
            try:
                # Search for the biblical reference in Amharic Bible
                search_result = self.bible_qa.search_verses(reference, max_results=1)
                if search_result and len(search_result) > 0:
                    amharic_text = search_result[0].get('content', '')
                    confidence = search_result[0].get('score', 0.0)
                    logger.info(f"✅ Found Amharic text for {reference} (confidence: {confidence:.2f})")
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve Amharic text for {reference}: {e}")
        
        return LiturgicalReading(
            reference=reference,
            amharic_text=amharic_text,
            english_reference=self._translate_reference_to_english(reference),
            feast_day=source,
            source="ethiopian_orthodox_with_embeddings" if self.use_embeddings else "ethiopian_orthodox",
            confidence=confidence
        )
    
    def _get_feast_key(self, feast_name: str) -> str:
        """Map feast names to reading keys"""
        
        name_lower = feast_name.lower()
        
        if 'enkutatash' in name_lower or 'new year' in name_lower:
            return 'enkutatash'
        elif 'genna' in name_lower or 'christmas' in name_lower:
            return 'genna'  
        elif 'timkat' in name_lower or 'epiphany' in name_lower:
            return 'timkat'
        else:
            return 'general_feast'
    
    def _translate_reference_to_english(self, amharic_ref: str) -> str:
        """Translate Amharic biblical references to English"""
        
        translations = {
            'ዘፍጥረት': 'Genesis',
            'ዘኅልቀት': 'Exodus', 
            'የዕሳይያስ': 'Isaiah',
            'የተዋሕዶ': 'Ecclesiastes',
            'ወደ ሮሜ ሰዎች': 'Romans',
            '1ኛ ወደ ቆሮንቶስ ሰዎች': '1 Corinthians',
            '2ኛ ወደ ቆሮንቶስ ሰዎች': '2 Corinthians',
            'ወደ ኤፌሶን ሰዎች': 'Ephesians',
            'ወደ ቲቶ': 'Titus',
            'የሐዋርያት ሥራ': 'Acts',
            'የማቴዎስ ወንጌል': 'Matthew',
            'የማርቆስ ወንጌል': 'Mark', 
            'የሉቃስ ወንጌል': 'Luke',
            'የዮሐንስ ወንጌል': 'John',
            'መዝሙረ ዳዊት': 'Psalm'
        }
        
        english_ref = amharic_ref
        for amharic, english in translations.items():
            english_ref = english_ref.replace(amharic, english)
        
        return english_ref
    
    def _get_liturgical_color(self, date: datetime.date, feast_info: Optional[Dict[str, Any]], fasting_info: Dict[str, Any], easter_info: Optional[Dict[str, Any]] = None) -> str:
        """Get liturgical color for the day with Easter season awareness"""

        # Easter season colors (highest priority)
        if easter_info:
            ethiopian_easter = easter_info.get('ethiopian_easter')
            if ethiopian_easter:
                # Great Lent
                nenewe_start = ethiopian_easter - datetime.timedelta(days=69)
                abiy_tsome_start = nenewe_start + datetime.timedelta(days=14)
                if abiy_tsome_start <= date < ethiopian_easter:
                    return "purple"  # ወይን ጠጅ - Lent

                # Easter Season
                easter_end = ethiopian_easter + datetime.timedelta(days=49)
                if ethiopian_easter <= date <= easter_end:
                    return "white"  # ነጭ - Easter season

        # Major feast colors
        if feast_info and feast_info['type'] == 'major':
            return "white"  # ነጭ - Major feasts

        # Fasting colors
        elif fasting_info['is_fasting']:
            return "purple"  # ወይን ጠጅ - Fasting periods

        # Ordinary time
        else:
            return "green"  # አረንጓዴ - Ordinary time
    
    def search_readings_by_theme(self, theme: str, max_results: int = 5) -> List[LiturgicalReading]:
        """Search for readings by spiritual theme using embeddings"""
        
        if not self.use_embeddings:
            logger.warning("⚠️ Embeddings not available for thematic search")
            return []
        
        try:
            results = self.bible_qa.search_verses(theme, max_results=max_results)
            
            readings = []
            for result in results:
                reading = LiturgicalReading(
                    reference=result.get('reference', 'Unknown'),
                    amharic_text=result.get('content', ''),
                    english_reference=result.get('reference', 'Unknown'),
                    source="thematic_search",
                    confidence=result.get('score', 0.0)
                )
                readings.append(reading)
            
            return readings
            
        except Exception as e:
            logger.error(f"❌ Thematic search failed: {e}")
            return []

# Test function
def test_amharic_liturgical_system():
    """Test the integrated Amharic liturgical system"""
    
    print("🕊️ Testing Amharic Liturgical System")
    print("=" * 50)
    
    system = AmharicLiturgicalSystem()
    
    # Test today's readings
    today = datetime.date.today()
    readings = system.get_daily_readings(today)
    
    print(f"📅 {readings.gregorian_date} (Gregorian)")
    print(f"   Ethiopian: {readings.ethiopian_date['formatted']}")
    print(f"   Season: {readings.liturgical_season}")
    print(f"   Color: {readings.liturgical_color}")
    
    if readings.feast_info:
        print(f"   🎉 Feast: {readings.feast_info['name_english']} ({readings.feast_info['name_amharic']})")
    
    print(f"   🍃 Fasting: {'Yes' if readings.fasting_info['is_fasting'] else 'No'}")
    
    print("\n📖 Readings:")
    if readings.gospel:
        print(f"   ✝️ Gospel: {readings.gospel.reference}")
        if readings.gospel.amharic_text:
            print(f"      Amharic: {readings.gospel.amharic_text[:100]}...")
    
    if readings.epistle:
        print(f"   📜 Epistle: {readings.epistle.reference}")
    
    if readings.old_testament:
        print(f"   📖 OT: {readings.old_testament.reference}")
    
    # Test Ethiopian New Year
    new_year_date = datetime.date(2025, 9, 11)
    new_year_readings = system.get_daily_readings(new_year_date)
    
    print(f"\n🎊 Ethiopian New Year ({new_year_date}):")
    print(f"   Ethiopian: {new_year_readings.ethiopian_date['formatted']}")
    if new_year_readings.feast_info:
        print(f"   Feast: {new_year_readings.feast_info['name_amharic']}")
    if new_year_readings.gospel:
        print(f"   Gospel: {new_year_readings.gospel.reference}")

if __name__ == "__main__":
    test_amharic_liturgical_system()