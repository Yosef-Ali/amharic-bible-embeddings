#!/usr/bin/env python3
"""
Build comprehensive liturgical database with embeddings
"""

import json
import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add project to path
sys.path.append(str(Path(__file__).parent.parent))

from src.calendar_calculator import liturgical_manager
from sentence_transformers import SentenceTransformer

class LiturgicalDatabaseBuilder:
    """
    Builds searchable database of liturgical readings
    """
    
    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
        self.readings_db = []
    
    def generate_year_calendar(self, year: int = 2025) -> List[Dict[str, Any]]:
        """Generate complete liturgical calendar for a year"""
        
        calendar_data = []
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        
        current_date = start_date
        while current_date <= end_date:
            daily_info = liturgical_manager.get_daily_info(current_date)
            calendar_data.append(daily_info)
            current_date += datetime.timedelta(days=1)
        
        return calendar_data
    
    def load_reading_templates(self, readings_file: str) -> List[Dict[str, Any]]:
        """Load reading templates to populate the calendar"""
        
        with open(readings_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_searchable_readings(self, calendar_data: List[Dict[str, Any]], 
                                  reading_templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create searchable reading entries with embeddings"""
        
        searchable_entries = []
        
        for day_info in calendar_data:
            # Create entries for both Western and Eastern readings
            
            # Western readings
            western_entry = self._create_reading_entry(
                day_info, "western", reading_templates
            )
            if western_entry:
                searchable_entries.append(western_entry)
            
            # Eastern readings  
            eastern_entry = self._create_reading_entry(
                day_info, "eastern", reading_templates
            )
            if eastern_entry:
                searchable_entries.append(eastern_entry)
        
        # Generate embeddings for all entries
        texts_to_embed = [entry["searchable_text"] for entry in searchable_entries]
        embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True)
        
        # Add embeddings to entries
        for i, entry in enumerate(searchable_entries):
            entry["embedding"] = embeddings[i].tolist()
            entry["embedding_dim"] = len(embeddings[i])
        
        return searchable_entries
    
    def _create_reading_entry(self, day_info: Dict[str, Any], 
                            tradition: str, templates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create searchable entry for specific tradition"""
        
        if tradition not in day_info:
            return None
        
        tradition_data = day_info[tradition]
        
        # Find matching template (simplified - would be more sophisticated)
        template = None
        for tmpl in templates:
            if tmpl.get(f"{tradition}_calendar") and tmpl["date"] == day_info["gregorian_date"]:
                template = tmpl[f"{tradition}_calendar"]
                break
        
        if not template:
            # Create basic entry even without template
            template = self._generate_basic_template(tradition_data, tradition)
        
        # Create searchable text
        searchable_parts = [
            f"Date: {day_info['gregorian_date']}",
            f"Tradition: {tradition}",
            f"Season: {tradition_data.get('season', 'Unknown')}"
        ]
        
        if tradition == "western":
            searchable_parts.extend([
                f"Liturgical Year: {tradition_data.get('liturgical_year', 'Unknown')}",
                f"Color: {tradition_data.get('season_info', {}).get('liturgical_color', 'Unknown')}"
            ])
        elif tradition == "ethiopian":
            eth_date = tradition_data.get('date', {})
            searchable_parts.extend([
                f"Ethiopian Date: {eth_date.get('formatted', 'Unknown')}",
                f"Fasting: {'Yes' if tradition_data.get('is_fasting_day', {}).get('is_fasting') else 'No'}"
            ])
        
        # Add reading information
        for reading_type in ["first_reading", "epistle", "gospel", "old_testament"]:
            if reading_type in template:
                reading = template[reading_type]
                searchable_parts.extend([
                    f"{reading_type}: {reading.get('reference', '')}",
                    f"Theme: {reading.get('theme', '')}"
                ])
        
        return {
            "entry_id": f"{tradition}_{day_info['gregorian_date']}",
            "date": day_info["gregorian_date"],
            "tradition": tradition,
            "day_info": day_info,
            "readings": template,
            "searchable_text": " | ".join(searchable_parts)
        }
    
    def _generate_basic_template(self, tradition_data: Dict[str, Any], tradition: str) -> Dict[str, Any]:
        """Generate basic template when no specific readings available"""
        
        if tradition == "western":
            return {
                "first_reading": {"reference": "TBD", "theme": "To be added"},
                "gospel": {"reference": "TBD", "theme": "To be added"},
                "saints": []
            }
        else:  # ethiopian
            return {
                "old_testament": {"reference": "TBD", "theme": "To be added"},
                "epistle": {"reference": "TBD", "theme": "To be added"},
                "gospel": {"reference": "TBD", "theme": "To be added"},
                "saints": []
            }

def main():
    """Build the complete liturgical database"""
    
    print("🗓️ Building Liturgical Calendar Database")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    # Initialize builder
    builder = LiturgicalDatabaseBuilder()
    
    # Generate calendar for 2025
    print("📅 Generating 2025 liturgical calendar...")
    calendar_2025 = builder.generate_year_calendar(2025)
    
    # Load reading templates
    templates_file = project_root / "data/sample_liturgical_readings.json"
    reading_templates = builder.load_reading_templates(str(templates_file))
    
    # Create searchable readings database
    print("🔍 Creating searchable readings with embeddings...")
    searchable_readings = builder.create_searchable_readings(calendar_2025, reading_templates)
    
    # Save results
    output_data = {
        "year": 2025,
        "total_days": len(calendar_2025),
        "total_readings": len(searchable_readings),
        "western_entries": len([r for r in searchable_readings if r["tradition"] == "western"]),
        "eastern_entries": len([r for r in searchable_readings if r["tradition"] == "ethiopian"]),
        "readings": searchable_readings,
        "calendar": calendar_2025
    }
    
    # Save to file
    output_file = project_root / "data/liturgical_database_2025.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Database created: {len(searchable_readings)} searchable readings")
    print(f"📊 Western entries: {output_data['western_entries']}")
    print(f"📊 Eastern entries: {output_data['eastern_entries']}")
    print(f"💾 Saved to: {output_file}")
    print("\n🚀 Run 'streamlit run app.py' to explore the calendar!")

if __name__ == "__main__":
    main()
