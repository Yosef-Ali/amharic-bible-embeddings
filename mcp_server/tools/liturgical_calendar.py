"""
Enhanced Liturgical Calendar Tool for Catholic Teaching Assistant
Provides daily readings and liturgical information with precise Ethiopian calendar
"""

from datetime import datetime, date
from typing import Dict, Any, Optional, List
import json
import sys
import os

# Add src directory to path for enhanced calendar imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from calendar.liturgical_reading_system import AmharicLiturgicalSystem
    from calendar.ethiopian_calendar_data import EthiopianCalendarData
    HAS_ENHANCED_CALENDAR = True
except ImportError:
    HAS_ENHANCED_CALENDAR = False

class LiturgicalCalendarTool:
    """Enhanced tool for liturgical calendar and daily readings"""
    
    def __init__(self):
        self.liturgical_data = self._load_basic_calendar()
        self.daily_readings = self._load_basic_readings()
        
        # Initialize enhanced calendar system if available
        if HAS_ENHANCED_CALENDAR:
            try:
                self.enhanced_system = AmharicLiturgicalSystem(use_embeddings=True)
                self.has_enhanced = True
                print("✅ Enhanced Ethiopian calendar system initialized with Amharic embeddings")
            except Exception as e:
                print(f"⚠️ Enhanced calendar available but embeddings failed: {e}")
                self.enhanced_system = AmharicLiturgicalSystem(use_embeddings=False)
                self.has_enhanced = True
        else:
            self.enhanced_system = None
            self.has_enhanced = False
            print("⚠️ Enhanced calendar system not available - using basic implementation")
    
    def _load_basic_calendar(self) -> Dict[str, Any]:
        """Load basic liturgical calendar data"""
        
        # Sample liturgical seasons and major feasts
        return {
            "seasons": {
                "advent": {"start": "11-27", "end": "12-24", "name_amharic": "መጽአተ ገና"},
                "christmas": {"start": "12-25", "end": "01-13", "name_amharic": "የገና ወቅት"},
                "lent": {"start": "02-14", "end": "03-30", "name_amharic": "ጾመ ፋሲካ"},
                "easter": {"start": "03-31", "end": "05-19", "name_amharic": "የፋሲካ ወቅት"},
                "ordinary_time": {"name_amharic": "መደበኛ ጊዜ"}
            },
            "major_feasts": {
                "01-01": {"name": "የእግዚአብሔር እናት ቅዱስ ማርያም", "rank": "solemnity"},
                "01-06": "የመስጠት ሰንበት (ኤጲፋንያ)",
                "03-19": "ቅዱስ ዮሴፍ",
                "03-25": "የእመቤታችን ምልክተ ታላቅ",
                "08-15": "የእመቤታችን መነሳሳት", 
                "11-01": "የሁሉም ቅዱሳን በዓል",
                "12-08": "የእመቤታችን ንጽሐና ርምሮት",
                "12-25": "የእመቤታችን ልደት (ገና)"
            }
        }
    
    def _load_basic_readings(self) -> Dict[str, Any]:
        """Load basic daily readings structure"""
        
        # This would integrate with actual lectionary
        return {
            "sunday_cycle": ["A", "B", "C"],  # 3-year cycle
            "weekday_cycle": ["I", "II"],     # 2-year cycle
            "readings_structure": [
                "first_reading",   # Old Testament
                "psalm",          # Responsorial Psalm  
                "second_reading", # New Testament (Sundays/feasts)
                "gospel"          # Gospel reading
            ]
        }
    
    async def get_daily_readings(self, date_str: Optional[str] = None, language: str = "amharic") -> Dict[str, Any]:
        """Get daily liturgical readings with enhanced Ethiopian calendar support"""
        
        # Parse date
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return {"error": f"Invalid date format: {date_str}. Use YYYY-MM-DD"}
        else:
            target_date = date.today()
        
        # Use enhanced system if available
        if self.has_enhanced:
            try:
                return await self._get_enhanced_readings(target_date, language)
            except Exception as e:
                print(f"⚠️ Enhanced readings failed, falling back to basic: {e}")
                # Fall through to basic implementation
        
        # Basic implementation (fallback)
        liturgical_season = self._get_liturgical_season(target_date)
        feast_info = self._get_feast_info(target_date)
        readings = await self._get_readings_for_date(target_date, language)
        
        return {
            "date": target_date.isoformat(),
            "liturgical_season": liturgical_season,
            "feast_or_memorial": feast_info,
            "readings": readings,
            "liturgical_color": self._get_liturgical_color(liturgical_season, feast_info),
            "language": language,
            "system": "basic"
        }
    
    async def _get_enhanced_readings(self, target_date: date, language: str) -> Dict[str, Any]:
        """Get readings using enhanced Ethiopian calendar system"""
        
        # Get comprehensive liturgical info
        liturgical_info = self.enhanced_system.get_daily_readings(target_date)
        
        # Format for MCP response
        readings = {}
        
        if liturgical_info.gospel:
            readings["gospel"] = {
                "citation": liturgical_info.gospel.reference,
                "citation_english": liturgical_info.gospel.english_reference,
                "text": liturgical_info.gospel.amharic_text if language == "amharic" else "",
                "confidence": liturgical_info.gospel.confidence,
                "source": liturgical_info.gospel.source
            }
        
        if liturgical_info.epistle:
            readings["epistle"] = {
                "citation": liturgical_info.epistle.reference,
                "citation_english": liturgical_info.epistle.english_reference,
                "text": liturgical_info.epistle.amharic_text if language == "amharic" else "",
                "confidence": liturgical_info.epistle.confidence
            }
        
        if liturgical_info.old_testament:
            readings["first_reading"] = {
                "citation": liturgical_info.old_testament.reference,
                "citation_english": liturgical_info.old_testament.english_reference,
                "text": liturgical_info.old_testament.amharic_text if language == "amharic" else "",
                "confidence": liturgical_info.old_testament.confidence
            }
        
        if liturgical_info.psalm:
            readings["psalm"] = {
                "citation": liturgical_info.psalm.reference,
                "citation_english": liturgical_info.psalm.english_reference,
                "text": liturgical_info.psalm.amharic_text if language == "amharic" else "",
                "response": "ጌታ የእኔ ረዓይ ነው" if language == "amharic" else "The Lord is my shepherd"
            }
        
        return {
            "date": target_date.isoformat(),
            "gregorian_date": liturgical_info.gregorian_date,
            "ethiopian_date": liturgical_info.ethiopian_date,
            "liturgical_season": {
                "name": liturgical_info.liturgical_season,
                "amharic": liturgical_info.liturgical_season
            },
            "feast_or_memorial": liturgical_info.feast_info,
            "fasting_info": liturgical_info.fasting_info,
            "readings": readings,
            "liturgical_color": liturgical_info.liturgical_color,
            "saints_commemorations": liturgical_info.saints_commemorations or [],
            "language": language,
            "system": "enhanced_ethiopian"
        }
    
    async def search_readings_by_theme(self, theme: str, language: str = "amharic", max_results: int = 5) -> Dict[str, Any]:
        """Search for readings by spiritual theme (enhanced system only)"""
        
        if not self.has_enhanced:
            return {
                "error": "Thematic search requires enhanced system with embeddings",
                "available": False
            }
        
        try:
            readings = self.enhanced_system.search_readings_by_theme(theme, max_results)
            
            results = []
            for reading in readings:
                results.append({
                    "reference": reading.reference,
                    "english_reference": reading.english_reference,
                    "amharic_text": reading.amharic_text if language == "amharic" else "",
                    "confidence": reading.confidence,
                    "source": reading.source
                })
            
            return {
                "theme": theme,
                "results_count": len(results),
                "readings": results,
                "language": language
            }
            
        except Exception as e:
            return {
                "error": f"Thematic search failed: {e}",
                "theme": theme
            }
    
    def _get_liturgical_season(self, target_date: date) -> Dict[str, str]:
        """Determine the liturgical season for a given date"""
        
        month_day = f"{target_date.month:02d}-{target_date.day:02d}"
        
        seasons = self.liturgical_data["seasons"]
        
        # Check major seasons (simplified logic)
        if "11-27" <= month_day <= "12-24":
            return {"name": "advent", "amharic": seasons["advent"]["name_amharic"]}
        elif "12-25" <= month_day or month_day <= "01-13":
            return {"name": "christmas", "amharic": seasons["christmas"]["name_amharic"]}
        elif "02-14" <= month_day <= "03-30":  # Simplified Lent dates
            return {"name": "lent", "amharic": seasons["lent"]["name_amharic"]}
        elif "03-31" <= month_day <= "05-19":  # Simplified Easter dates
            return {"name": "easter", "amharic": seasons["easter"]["name_amharic"]}
        else:
            return {"name": "ordinary_time", "amharic": seasons["ordinary_time"]["name_amharic"]}
    
    def _get_feast_info(self, target_date: date) -> Optional[Dict[str, str]]:
        """Check if date is a special feast or memorial"""
        
        month_day = f"{target_date.month:02d}-{target_date.day:02d}"
        
        feasts = self.liturgical_data["major_feasts"]
        
        if month_day in feasts:
            feast_data = feasts[month_day]
            if isinstance(feast_data, dict):
                return feast_data
            else:
                return {"name": feast_data, "rank": "feast"}
        
        return None
    
    def _get_liturgical_color(self, season: Dict[str, str], feast: Optional[Dict[str, str]]) -> str:
        """Get liturgical color for vestments"""
        
        if feast:
            rank = feast.get("rank", "memorial")
            if rank == "solemnity":
                return "white"  # ነጭ
            elif "mary" in feast.get("name", "").lower():
                return "white"  # ነጭ - for Marian feasts
        
        season_name = season.get("name", "ordinary_time")
        
        color_map = {
            "advent": "purple",     # ወይን ጠጅ
            "lent": "purple",       # ወይን ጠጅ  
            "christmas": "white",   # ነጭ
            "easter": "white",      # ነጭ
            "ordinary_time": "green" # አረንጓዴ
        }
        
        return color_map.get(season_name, "green")
    
    async def _get_readings_for_date(self, target_date: date, language: str) -> Dict[str, str]:
        """Get actual readings for the date (placeholder)"""
        
        # This would integrate with actual lectionary database
        # For now, return sample structure
        
        if language == "amharic":
            return {
                "first_reading": {
                    "citation": "ዘፍጥረት 1፦1-5",
                    "text": "በመጀመርያ እግዚአብሔር ሰማይንና ምድርን ፈጠረ...",
                    "note": "ናሙና ንባብ - ዕለታዊ ንባብ ተዋህቷል"
                },
                "psalm": {
                    "citation": "መዝሙር 23",
                    "response": "ጌታ የእኔ ረዓይ ነው",
                    "text": "ጌታ የእኔ ረዓይ ነው፤ ምንም አልጎድልኝም..."
                },
                "gospel": {
                    "citation": "ማቴዎስ 5፦1-12",
                    "text": "ኢየሱስ ሕዝቡን ሲያይ ወደ ተራራ ወጣ...",
                    "note": "የተከበሩት ነገሮች"
                }
            }
        else:  # English
            return {
                "first_reading": {
                    "citation": "Genesis 1:1-5", 
                    "text": "In the beginning, God created the heavens and the earth...",
                    "note": "Sample reading - daily lectionary integration needed"
                },
                "psalm": {
                    "citation": "Psalm 23",
                    "response": "The Lord is my shepherd",
                    "text": "The Lord is my shepherd; there is nothing I lack..."
                },
                "gospel": {
                    "citation": "Matthew 5:1-12",
                    "text": "When Jesus saw the crowds, he went up the mountain...",
                    "note": "The Beatitudes"
                }
            }
    
    async def get_liturgical_year_info(self) -> Dict[str, Any]:
        """Get information about the current liturgical year"""
        
        current_date = date.today()
        season = self._get_liturgical_season(current_date)
        
        return {
            "current_season": season,
            "liturgical_color": self._get_liturgical_color(season, None),
            "season_description": self._get_season_description(season["name"]),
            "upcoming_feasts": self._get_upcoming_feasts(current_date)
        }
    
    def _get_season_description(self, season_name: str) -> str:
        """Get description of liturgical season"""
        
        descriptions = {
            "advent": "መጽአተ ገና የኢየሱስ ክርስቶስ ልደትን የምንጠብቅበት ወቅት ነው። ለ4 ሳምንታት የሚቆይ ሲሆን በንስሐ እና በተስፋ የተሞላ ጊዜ ነው።",
            "christmas": "የገና ወቅት የኢየሱስ ክርስቶስ ልደትን የምናከብርበት ደስታ ያለበት ጊዜ ነው።",
            "lent": "ጾመ ፋሲካ ለ40 ቀናት የሚቆይ የንስሐ፣ ጸሎት እና ምግብ ሰጪነት ወቅት ነው።",
            "easter": "የፋሲካ ወቅት የኢየሱስ ትንሣኤን የምናከብርበት ትልቁ የክርስትና በዓል ነው።",
            "ordinary_time": "መደበኛ ጊዜ የኢየሱስን ህይወት እና ትምህርት የምንማርበት ወቅት ነው።"
        }
        
        return descriptions.get(season_name, "የተለመደ የመንፈሳዊ እድገት ጊዜ")
    
    def _get_upcoming_feasts(self, from_date: date) -> List[str]:
        """Get upcoming feasts from given date"""
        
        # Simplified - would calculate actual upcoming feasts
        return [
            "ቅዱስ ኦገስጢኖስ (ኦገስት 28)",
            "የመስቀል ፈልጎ ማግኘት (ሴፕቴምበር 14)",
            "ቅዱስ ተሪዛ (ኦክቶበር 1)"
        ]