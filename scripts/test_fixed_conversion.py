#!/usr/bin/env python3
import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from calendar.ethiopian_calendar_data import EthiopianCalendarData

def main():
    # Test all our reference dates
    test_dates = [
        (datetime.date(2028, 4, 16), 'ሚያዝያ 8, 2020 ዓ.ም.'),
        (datetime.date(2030, 4, 26), 'ሚያዝያ 20, 2022 ዓ.ም.'),
        (datetime.date(2033, 4, 24), 'ሚያዝያ 16, 2025 ዓ.ም.'),
    ]

    print('Testing Fixed Ethiopian Calendar Conversion:')
    print('=' * 50)

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
        print('🎉 All dates now correct!')
    else:
        print('❌ Still need adjustments')
    
    return all_correct

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)