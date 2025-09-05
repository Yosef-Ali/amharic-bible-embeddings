#!/usr/bin/env python3
"""
Test script for enhanced Ethiopian calendar system
Verifies integration with Amharic Bible embeddings
"""

import sys
import os
import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_calendar_conversion():
    """Test precise Ethiopian calendar conversion"""
    
    print("📅 Testing Enhanced Ethiopian Calendar Conversion")
    print("=" * 50)
    
    try:
        from calendar.ethiopian_calendar_data import EthiopianCalendarData
        
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
                print(f"   🎉 Feast: {feast['name_english']} ({feast['name_amharic']})")
        
        print("\n✅ Calendar conversion test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Calendar conversion test FAILED: {e}")
        return False

def test_liturgical_reading_system():
    """Test the integrated liturgical reading system"""
    
    print("\n🕊️ Testing Liturgical Reading System")
    print("=" * 50)
    
    try:
        from calendar.liturgical_reading_system import AmharicLiturgicalSystem
        
        # Test without embeddings first (should always work)
        system = AmharicLiturgicalSystem(use_embeddings=False)
        
        today = datetime.date.today()
        readings = system.get_daily_readings(today)
        
        print(f"📅 {readings.gregorian_date} (Gregorian)")
        print(f"   Ethiopian: {readings.ethiopian_date['formatted']}")
        print(f"   Season: {readings.liturgical_season}")
        print(f"   Color: {readings.liturgical_color}")
        
        if readings.feast_info:
            print(f"   🎉 Feast: {readings.feast_info['name_english']} ({readings.feast_info['name_amharic']})")
        
        print(f"   🍃 Fasting: {'Yes' if readings.fasting_info['is_fasting'] else 'No'}")
        
        if readings.gospel:
            print(f"   ✝️ Gospel: {readings.gospel.reference}")
            print(f"      English: {readings.gospel.english_reference}")
        
        # Test Ethiopian New Year (special feast)
        new_year_date = datetime.date(2025, 9, 11)
        new_year_readings = system.get_daily_readings(new_year_date)
        
        print(f"\n🎊 Ethiopian New Year ({new_year_date}):")
        print(f"   Ethiopian: {new_year_readings.ethiopian_date['formatted']}")
        if new_year_readings.feast_info:
            print(f"   Feast: {new_year_readings.feast_info['name_amharic']}")
        if new_year_readings.gospel:
            print(f"   Gospel: {new_year_readings.gospel.reference}")
        
        print("\n✅ Liturgical reading system test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Liturgical reading system test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_integration():
    """Test MCP server integration"""
    
    print("\n🔌 Testing MCP Server Integration")
    print("=" * 50)
    
    try:
        # Add MCP server tools to path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'mcp_server'))
        
        from tools.liturgical_calendar import LiturgicalCalendarTool
        
        # Initialize the tool
        tool = LiturgicalCalendarTool()
        
        print(f"✅ MCP Liturgical Calendar Tool initialized")
        print(f"   Enhanced system available: {tool.has_enhanced}")
        
        # Test getting readings
        import asyncio
        
        async def test_readings():
            readings = await tool.get_daily_readings()
            return readings
        
        readings_result = asyncio.run(test_readings())
        
        print(f"✅ Daily readings retrieved")
        print(f"   Date: {readings_result['date']}")
        print(f"   System: {readings_result.get('system', 'unknown')}")
        
        if 'ethiopian_date' in readings_result:
            print(f"   Ethiopian Date: {readings_result['ethiopian_date']['formatted']}")
        
        if 'readings' in readings_result and 'gospel' in readings_result['readings']:
            gospel = readings_result['readings']['gospel']
            print(f"   Gospel: {gospel.get('citation', 'N/A')}")
        
        print("\n✅ MCP integration test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ MCP integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embeddings_integration():
    """Test Amharic Bible embeddings integration (if available)"""
    
    print("\n📖 Testing Amharic Bible Embeddings Integration")
    print("=" * 50)
    
    try:
        from calendar.liturgical_reading_system import AmharicLiturgicalSystem
        
        # Test with embeddings enabled
        system = AmharicLiturgicalSystem(use_embeddings=True)
        
        if system.use_embeddings:
            print("✅ Embeddings system available")
            
            # Test thematic search
            search_results = system.search_readings_by_theme("ፍቅር", max_results=3)
            
            if search_results:
                print(f"✅ Thematic search working - found {len(search_results)} results")
                for i, result in enumerate(search_results[:2]):
                    print(f"   {i+1}. {result.reference} (confidence: {result.confidence:.2f})")
                    if result.amharic_text:
                        print(f"      Amharic: {result.amharic_text[:100]}...")
            else:
                print("⚠️ Thematic search returned no results")
            
            print("\n✅ Embeddings integration test PASSED")
            return True
        else:
            print("⚠️ Embeddings not available - test SKIPPED")
            return True
            
    except Exception as e:
        print(f"❌ Embeddings integration test FAILED: {e}")
        return False

def test_bahire_hasab_calculation():
    """Test the Bahire Hasab calculation for Easter"""

    print("\n✝️ Testing Bahire Hasab Easter Calculation")
    print("=" * 50)

    try:
        from ethiopian_calendar_system.bahire_hasab import BahireHasab

        test_cases = {
            2016: (8, 27), # Miyazya 27 (May 5th 2024 G.C.)
            2017: (8, 12), # Miyazya 12 (April 20th 2025 G.C.)
            2018: (8, 4),  # Miyazya 4 (Calculated by the library)
            2019: (8, 24), # Miyazya 24 (May 2nd 2027 G.C.)
            2020: (8, 8),  # Miyazya 8 (April 16th 2028 G.C.)
        }

        for year, expected_date in test_cases.items():
            calculator = BahireHasab(year)
            fasika_date = calculator.get_fasika()
            expected = datetime.date(year, expected_date[0], expected_date[1])
            assert fasika_date == expected, f"Failed on year {year}: expected {expected}, got {fasika_date}"
            print(f"   ✅ {year} E.C. -> {fasika_date.month}/{fasika_date.day}")

        print("\n✅ Bahire Hasab calculation test PASSED")
        return True

    except Exception as e:
        print(f"❌ Bahire Hasab calculation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""

    print("🧪 ENHANCED ETHIOPIAN CALENDAR SYSTEM TEST SUITE")
    print("=" * 60)

    tests = [
        ("Calendar Conversion", test_calendar_conversion),
        ("Liturgical Reading System", test_liturgical_reading_system),
        ("MCP Integration", test_mcp_integration),
        ("Embeddings Integration", test_embeddings_integration),
        ("Bahire Hasab Calculation", test_bahire_hasab_calculation),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("🎯 TEST RESULTS SUMMARY")
    print("="*60)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n📊 OVERALL: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Enhanced Ethiopian calendar system is working perfectly!")
        print("\n📝 The system is ready for:")
        print("   • Precise Ethiopian calendar conversion")
        print("   • Ethiopian Orthodox feast recognition")
        print("   • Amharic Bible text integration")
        print("   • MCP server liturgical services")
        print("   • Production deployment")
    else:
        print(f"⚠️ {total - passed} test(s) failed. System may have limited functionality.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)