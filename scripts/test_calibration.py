#!/usr/bin/env python3
import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from calendar.ethiopian_calendar_data import EthiopianCalendarData

# Test both reference dates
test_dates = [
    (datetime.date(2028, 4, 16), 'ሚያዝያ 8, 2020 ዓ.ም.'),
    (datetime.date(2030, 4, 26), 'ሚያዝያ 20, 2022 ዓ.ም.'),
]

print('Testing Ethiopian Calendar Calibration:')
print('=' * 40)

for greg_date, expected in test_dates:
    eth_date = EthiopianCalendarData.gregorian_to_ethiopian_precise(greg_date)
    actual = f'{eth_date["month_name"]} {eth_date["day"]}, {eth_date["year"]} ዓ.ም.'
    match = '✅' if actual == expected else '❌'
    
    print(f'{match} {greg_date} = {actual}')
    if actual != expected:
        print(f'     Expected: {expected}')