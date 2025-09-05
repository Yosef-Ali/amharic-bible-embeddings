#!/usr/bin/env python3
"""
Command Line Interface for Unified Liturgical Reading Agent
"""

import argparse
import datetime
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unified_agent import LiturgicalReadingAgent

def format_reading_output(unified_readings):
    """Format readings for clean CLI output"""
    
    output = []
    output.append("=" * 60)
    output.append(f"📅 LITURGICAL READINGS FOR {unified_readings.date}")
    output.append("=" * 60)
    
    # Date information
    output.append(f"\n🗓️  DATE INFORMATION")
    output.append(f"   Gregorian: {unified_readings.gregorian_date}")
    ethiopian_date = unified_readings.ethiopian_date
    if ethiopian_date:
        output.append(f"   Ethiopian: {ethiopian_date.get('formatted', 'N/A')}")
        output.append(f"   Weekday: {datetime.datetime.fromisoformat(unified_readings.date).strftime('%A')}")
    
    # Western Catholic readings
    output.append(f"\n🌍 WESTERN CATHOLIC READINGS")
    
    if unified_readings.western_first_reading:
        output.append(f"   📖 First Reading: {unified_readings.western_first_reading.reference}")
    
    if unified_readings.western_psalm:
        output.append(f"   🎵 Responsorial Psalm: {unified_readings.western_psalm.reference}")
    
    if unified_readings.western_second_reading:
        output.append(f"   📜 Second Reading: {unified_readings.western_second_reading.reference}")
    
    if unified_readings.western_gospel:
        output.append(f"   ✝️  Gospel: {unified_readings.western_gospel.reference}")
        if unified_readings.western_gospel.liturgical_season:
            output.append(f"   🕯️  Season: {unified_readings.western_gospel.liturgical_season}")
    
    if unified_readings.western_liturgical_info:
        year_cycle = unified_readings.western_liturgical_info.get('liturgical_year', 'Unknown')
        output.append(f"   📆 Liturgical Year: {year_cycle}")
    
    # Ethiopian Orthodox readings
    output.append(f"\n⛪ ETHIOPIAN ORTHODOX READINGS")
    
    if unified_readings.ethiopian_old_testament:
        output.append(f"   📖 Old Testament: {unified_readings.ethiopian_old_testament.reference}")
    
    if unified_readings.ethiopian_psalm:
        output.append(f"   🎵 Psalm: {unified_readings.ethiopian_psalm.reference}")
    
    if unified_readings.ethiopian_epistle:
        output.append(f"   📜 Epistle: {unified_readings.ethiopian_epistle.reference}")
    
    if unified_readings.ethiopian_gospel:
        output.append(f"   ✝️  Gospel: {unified_readings.ethiopian_gospel.reference}")
    
    if unified_readings.ethiopian_liturgical_info:
        eth_season = unified_readings.ethiopian_liturgical_info.get('season', 'Unknown')
        output.append(f"   🕯️  Ethiopian Season: {eth_season}")
    
    # Fasting information
    if unified_readings.fasting_info:
        output.append(f"\n🍃 FASTING INFORMATION")
        is_fasting = unified_readings.fasting_info.get('is_fasting', False)
        fasting_type = unified_readings.fasting_info.get('fasting_type', 'none')
        
        if is_fasting:
            output.append(f"   🚫 Ethiopian Orthodox Fasting: YES ({fasting_type})")
            rules = unified_readings.fasting_info.get('fasting_rules', [])
            for rule in rules:
                output.append(f"      • {rule}")
        else:
            output.append(f"   ✅ Ethiopian Orthodox Fasting: No")
    
    # Source information
    output.append(f"\n📚 SOURCES")
    if unified_readings.western_first_reading:
        output.append(f"   Western: {unified_readings.western_first_reading.source}")
    if unified_readings.ethiopian_gospel:
        output.append(f"   Ethiopian: {unified_readings.ethiopian_gospel.source}")
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)

def format_comparison_output(comparison):
    """Format comparison for CLI output"""
    
    output = []
    output.append("\n🔄 TRADITION COMPARISON")
    output.append("-" * 30)
    
    output.append(f"📖 Gospel Readings:")
    output.append(f"   Western: {comparison.get('western_gospel', 'N/A')}")
    output.append(f"   Ethiopian: {comparison.get('ethiopian_gospel', 'N/A')}")
    output.append(f"   Same Book: {'✅ Yes' if comparison.get('gospel_match') else '❌ No'}")
    
    season_comp = comparison.get('season_comparison', {})
    output.append(f"\n🕯️  Liturgical Seasons:")
    output.append(f"   Western: {season_comp.get('western_season', 'N/A')}")
    output.append(f"   Ethiopian: {season_comp.get('ethiopian_season', 'N/A')}")
    
    fasting_comp = comparison.get('fasting_status', {})
    output.append(f"\n🍃 Fasting Status:")
    output.append(f"   Western: {'🚫 Lent/Fasting' if fasting_comp.get('western_fasting') else '✅ No Special Fasting'}")
    output.append(f"   Ethiopian: {'🚫 Fasting Day' if fasting_comp.get('ethiopian_fasting') else '✅ No Fasting'}")
    
    return "\n".join(output)

def main():
    """Main CLI function"""
    
    parser = argparse.ArgumentParser(
        description="Unified Liturgical Reading Agent - Western + Ethiopian Orthodox"
    )
    
    parser.add_argument(
        "--date", "-d",
        help="Date for readings (YYYY-MM-DD format). Defaults to today.",
        default=None
    )
    
    parser.add_argument(
        "--western-only", "-w",
        action="store_true",
        help="Get only Western Catholic readings"
    )
    
    parser.add_argument(
        "--ethiopian-only", "-e", 
        action="store_true",
        help="Get only Ethiopian Orthodox readings"
    )
    
    parser.add_argument(
        "--compare", "-c",
        action="store_true", 
        help="Compare readings between traditions"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output with debug information"
    )
    
    args = parser.parse_args()
    
    # Parse date
    target_date = None
    if args.date:
        try:
            target_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD format.")
            sys.exit(1)
    else:
        target_date = datetime.date.today()
    
    # Initialize agent
    print("🕊️ Initializing Liturgical Reading Agent...")
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    try:
        agent = LiturgicalReadingAgent()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)
    
    # Execute based on arguments
    try:
        if args.western_only:
            print("🌍 Fetching Western Catholic readings...")
            readings = agent.get_western_readings(target_date)
            
            if readings:
                print(f"\n📅 Western Catholic Readings for {target_date}")
                print("-" * 40)
                for reading_type, reference in readings.items():
                    if reading_type not in ['source', 'date', 'note']:
                        print(f"📜 {reading_type.replace('_', ' ').title()}: {reference}")
                print(f"📚 Source: {readings.get('source', 'Unknown')}")
            else:
                print("❌ Failed to fetch Western readings")
        
        elif args.ethiopian_only:
            print("⛪ Calculating Ethiopian Orthodox readings...")
            readings = agent.get_ethiopian_readings(target_date)
            
            if readings:
                print(f"\n📅 Ethiopian Orthodox Readings for {target_date}")
                print("-" * 40)
                for reading_type, reading_obj in readings.items():
                    if hasattr(reading_obj, 'reference'):
                        print(f"📜 {reading_type.replace('_', ' ').title()}: {reading_obj.reference}")
                
                eth_date = readings.get('ethiopian_date', {})
                if eth_date:
                    print(f"🗓️ Ethiopian Date: {eth_date.get('formatted', 'N/A')}")
            else:
                print("❌ Failed to calculate Ethiopian readings")
        
        else:
            print("🔄 Getting unified readings from both traditions...")
            unified = agent.get_daily_readings(target_date)
            
            print(format_reading_output(unified))
            
            if args.compare:
                comparison = agent.compare_readings(target_date)
                print(format_comparison_output(comparison))
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()