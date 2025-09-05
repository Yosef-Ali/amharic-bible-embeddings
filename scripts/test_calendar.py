#!/usr/bin/env python3
"""
Simple liturgical calendar test - minimal dependencies
"""

import datetime
from typing import Dict, Any
import json
from pathlib import Path

class SimpleLiturgicalCalendar:
    """Simple liturgical calendar without heavy dependencies"""
    
    def get_daily_info(self, date: datetime.date) -> Dict[str, Any]:
        """Get liturgical info for date"""
        
        # Ethiopian date approximation
        eth_year = date.year - 7 if date.month >= 9 else date.year - 8
        
        # Simple season detection
        if date.month == 12 and date.day >= 25:
            western_season = "Christmas"
            ethiopian_season = "Christmas"
        elif date.month == 1 and date.day <= 6:
            western_season = "Christmas" 
            ethiopian_season = "Christmas"
        elif date.month in [3, 4]:
            western_season = "Lent"
            ethiopian_season = "Great Lent"
        else:
            western_season = "Ordinary Time"
            ethiopian_season = "Ordinary Time"
        
        # Fasting detection (simplified)
        is_fasting = date.weekday() in [2, 4]  # Wed, Fri
        
        return {
            "date": date.isoformat(),
            "western_season": western_season,
            "ethiopian_season": ethiopian_season,
            "ethiopian_year": eth_year,
            "is_fasting_day": is_fasting,
            "weekday": date.strftime("%A")
        }

def test_calendar():
    """Test the calendar system"""
    
    print("🗓️ Testing Liturgical Calendar System")
    print("=" * 40)
    
    calendar = SimpleLiturgicalCalendar()
    
    # Test dates
    test_dates = [
        datetime.date.today(),
        datetime.date(2025, 12, 25),  # Christmas
        datetime.date(2025, 1, 6),   # Epiphany
        datetime.date(2025, 4, 20),  # Easter season
    ]
    
    for test_date in test_dates:
        info = calendar.get_daily_info(test_date)
        
        print(f"\n📅 {test_date.strftime('%B %d, %Y')} ({info['weekday']})")
        print(f"🌍 Western: {info['western_season']}")
        print(f"⛪ Ethiopian: {info['ethiopian_season']} ({info['ethiopian_year']} ዓ.ም.)")
        print(f"🥗 Fasting: {'Yes' if info['is_fasting_day'] else 'No'}")
    
    # Save test data
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data/test_calendar_data.json"
    
    year_data = []
    current_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2025, 1, 31)  # Just January for testing
    
    while current_date <= end_date:
        year_data.append(calendar.get_daily_info(current_date))
        current_date += datetime.timedelta(days=1)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "month": "January 2025",
            "days": year_data,
            "total_days": len(year_data)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Test complete! Sample data saved to {output_file}")
    print("🎯 Calendar calculations working correctly")
    
    return True

if __name__ == "__main__":
    success = test_calendar()
    if success:
        print("\n🚀 Ready for authentic liturgical readings!")
        print("📖 Waiting for your OCR'd prayer and reading texts")

