#!/usr/bin/env python3
"""
Test script for Unified Liturgical Reading Agent
"""

import sys
import datetime
from pathlib import Path

# Add the necessary paths
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "liturgical-calendar-embeddings" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "orthodox-reading-agent" / "src"))

def test_individual_components():
    """Test individual components first"""
    
    print("🧪 Testing Individual Components")
    print("=" * 40)
    
    # Test Ethiopian calendar
    try:
        from calendar_calculator import LiturgicalCalendarManager
        calendar_manager = LiturgicalCalendarManager()
        
        today = datetime.date.today()
        info = calendar_manager.get_daily_info(today)
        
        print("✅ Ethiopian Calendar: Working")
        print(f"   Ethiopian Date: {info['ethiopian']['date']['formatted']}")
        print(f"   Ethiopian Season: {info['ethiopian']['season']}")
        print(f"   Fasting: {info['ethiopian']['is_fasting_day']['is_fasting']}")
        
    except Exception as e:
        print(f"❌ Ethiopian Calendar: Failed - {e}")
    
    # Test Western fetcher
    try:
        from western_fetcher import WesternCatholicReadingFetcher
        western_fetcher = WesternCatholicReadingFetcher()
        
        readings = western_fetcher.get_daily_readings(today)
        
        if readings:
            print("✅ Western Catholic Fetcher: Working")
            print(f"   Source: {readings.get('source', 'Unknown')}")
            print(f"   Gospel: {readings.get('gospel', 'Not found')}")
        else:
            print("⚠️  Western Catholic Fetcher: No readings returned (might be network issue)")
            
    except Exception as e:
        print(f"❌ Western Catholic Fetcher: Failed - {e}")

def test_unified_agent():
    """Test the main unified agent"""
    
    print("\n🕊️ Testing Unified Agent")
    print("=" * 40)
    
    try:
        from unified_agent import LiturgicalReadingAgent
        
        agent = LiturgicalReadingAgent()
        
        # Test Ethiopian readings only (local calculation)
        print("\n⛪ Testing Ethiopian Orthodox Readings...")
        ethiopian_readings = agent.get_ethiopian_readings()
        
        if ethiopian_readings:
            print("✅ Ethiopian readings calculated successfully")
            
            if 'gospel' in ethiopian_readings:
                gospel = ethiopian_readings['gospel']
                print(f"   Gospel: {gospel.reference}")
            
            if 'epistle' in ethiopian_readings:
                epistle = ethiopian_readings['epistle']
                print(f"   Epistle: {epistle.reference}")
                
            if 'old_testament' in ethiopian_readings:
                ot = ethiopian_readings['old_testament']
                print(f"   Old Testament: {ot.reference}")
        
        # Test Western readings only (online)
        print("\n🌍 Testing Western Catholic Readings...")
        western_readings = agent.get_western_readings()
        
        if western_readings:
            print("✅ Western readings fetched successfully")
            print(f"   Source: {western_readings.get('source', 'Unknown')}")
            print(f"   Gospel: {western_readings.get('gospel', 'Not found')}")
            print(f"   First Reading: {western_readings.get('first_reading', 'Not found')}")
        else:
            print("⚠️  Western readings failed (network/parsing issue)")
        
        # Test unified readings
        print("\n🔄 Testing Unified Readings...")
        unified = agent.get_daily_readings()
        
        print(f"✅ Unified readings generated")
        print(f"   Date: {unified.date}")
        print(f"   Ethiopian Date: {unified.ethiopian_date.get('formatted', 'N/A')}")
        
        if unified.western_gospel:
            print(f"   Western Gospel: {unified.western_gospel.reference}")
        
        if unified.ethiopian_gospel:
            print(f"   Ethiopian Gospel: {unified.ethiopian_gospel.reference}")
        
        if unified.fasting_info:
            is_fasting = unified.fasting_info.get('is_fasting', False)
            print(f"   Ethiopian Fasting: {'Yes' if is_fasting else 'No'}")
        
        # Test comparison
        print("\n🔄 Testing Reading Comparison...")
        comparison = agent.compare_readings()
        
        print(f"   Gospel books match: {comparison.get('gospel_match', False)}")
        print(f"   Western season: {comparison['season_comparison'].get('western_season', 'N/A')}")
        print(f"   Ethiopian season: {comparison['season_comparison'].get('ethiopian_season', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified Agent Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_interface():
    """Test CLI commands"""
    
    print("\n💻 Testing CLI Interface")
    print("=" * 40)
    
    import subprocess
    import os
    
    # Change to the correct directory
    agent_dir = Path(__file__).parent
    
    try:
        # Test help command
        result = subprocess.run([
            sys.executable, "cli.py", "--help"
        ], cwd=agent_dir, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI Help: Working")
        else:
            print(f"❌ CLI Help: Failed - {result.stderr}")
    
    except Exception as e:
        print(f"❌ CLI Test: Failed - {e}")

def main():
    """Run all tests"""
    
    print("🧪 UNIFIED LITURGICAL AGENT TEST SUITE")
    print("=" * 50)
    
    # Test individual components
    test_individual_components()
    
    # Test unified agent
    success = test_unified_agent()
    
    # Test CLI (optional)
    # test_cli_interface()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OVERALL STATUS: Tests completed successfully!")
        print("\n📝 Usage Instructions:")
        print("   python cli.py                    # Today's unified readings")
        print("   python cli.py -d 2025-01-07     # Specific date")
        print("   python cli.py --western-only     # Western Catholic only")
        print("   python cli.py --ethiopian-only   # Ethiopian Orthodox only")
        print("   python cli.py --compare          # Compare traditions")
    else:
        print("⚠️  OVERALL STATUS: Some tests failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)