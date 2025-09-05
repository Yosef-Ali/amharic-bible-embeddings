#!/usr/bin/env python3
"""
Display Fasika (Ethiopian Easter) dates for the next 5 years
"""

import sys
import os
import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calendar.ethiopian_calendar_data import EthiopianCalendarData

def main():
    print('🌟 Fasika (Ethiopian Easter) Dates for Next 5 Years')
    print('=' * 55)
    print()
    
    current_year = datetime.date.today().year
    
    for year in range(current_year, current_year + 6):
        easter_info = EthiopianCalendarData.calculate_ethiopian_easter(year)
        
        western_easter = easter_info['western_easter_gregorian']
        eth_easter_greg = easter_info['ethiopian_easter_gregorian']
        eth_easter = easter_info['ethiopian_easter']
        
        print(f'📅 {year}:')
        print(f'   🟦 Western Easter:      {western_easter}')
        print(f'   🟨 Ethiopian Easter:    {eth_easter_greg} (Gregorian)')
        print(f'   🇪🇹 Ethiopian Calendar:  {eth_easter["month_name"]} {eth_easter["day"]}, {eth_easter["year"]} ዓ.ም.')
        print()
    
    print('=' * 55)
    print('📝 Note: Ethiopian Orthodox Easter is typically celebrated')
    print('       1-2 weeks after Western Easter, following the same')
    print('       astronomical calculations but with calendar differences.')

if __name__ == "__main__":
    main()