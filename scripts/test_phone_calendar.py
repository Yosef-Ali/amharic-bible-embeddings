#!/usr/bin/env python3
import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from calendar.ethiopian_calendar_data import EthiopianCalendarData

def main():
    # Test the dates from your phone calendar
    phone_dates = [
        (datetime.date(2027, 5, 2), 'ሚያዝያ 24, 2019 ዓ.ም.'),
        (datetime.date(2031, 4, 13), 'ሚያዝያ 5, 2023 ዓ.ም.'),
        (datetime.date(2035, 4, 1), 'ሚያዝያ 23, 2027 ዓ.ም.'),
    ]

    print('Testing Our System Against Your Phone Calendar:')
    print('=' * 50)

    all_match = True
    for greg_date, expected in phone_dates:
        eth_date = EthiopianCalendarData.gregorian_to_ethiopian_precise(greg_date)
        actual = f'{eth_date["month_name"]} {eth_date["day"]}, {eth_date["year"]} ዓ.ም.'
        match = '✅' if actual == expected else '❌'
        
        if actual != expected:
            all_match = False
        
        print(f'{match} {greg_date}:')
        print(f'   Phone shows: {expected}')
        print(f'   Our system:  {actual}')
        print()

    if all_match:
        print('🎉 Perfect match with your phone calendar!')
    else:
        print('❌ Our system needs adjustment to match your phone calendar')
    
    return all_match

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)