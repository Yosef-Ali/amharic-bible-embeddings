#!/usr/bin/env python3
import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from calendar.ethiopian_calendar_data import EthiopianCalendarData

def main():
    # Test with the CORRECT Gregorian dates you provided
    test_dates = [
        (datetime.date(2028, 4, 16), 'ሚያዝያ 8, 2020 ዓ.ም.'),
        (datetime.date(2030, 4, 28), 'ሚያዝያ 20, 2022 ዓ.ም.'),  # Corrected: April 28, not 26
        (datetime.date(2033, 4, 16), 'ሚያዝያ 16, 2025 ዓ.ም.'),   # Corrected: April 16, not 24
    ]

    print('Testing Ethiopian Calendar with CORRECT Gregorian Dates:')
    print('=' * 55)

    all_correct = True
    for greg_date, expected in test_dates:
        eth_date = EthiopianCalendarData.gregorian_to_ethiopian_precise(greg_date)
        actual = f'{eth_date["month_name"]} {eth_date["day"]}, {eth_date["year"]} ዓ.ም.'
        match = '✅' if actual == expected else '❌'
        
        if actual != expected:
            all_correct = False
        
        print(f'{match} {greg_date}:')
        print(f'   Expected: {expected}')
        print(f'   Actual:   {actual}')
        print()

    if all_correct:
        print('🎉 All dates now correct with proper Gregorian dates!')
    else:
        print('❌ Need to fix algorithm for correct Gregorian dates')
    
    return all_correct

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)