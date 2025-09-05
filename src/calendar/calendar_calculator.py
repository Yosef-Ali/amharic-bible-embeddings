#!/usr/bin/env python3
"""
Ethiopian and Western Liturgical Calendar Calculator
Handles both calendar systems with proper date conversions
Enhanced with precise Ethiopian calendar data
"""

import datetime
from typing import Dict, Any, List, Optional
from dateutil.easter import easter
import calendar
import os
import sys

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from ethiopian_calendar_data import EthiopianCalendarData

class EthiopianCalendar:
    """
    Ethiopian calendar calculations and conversions
    """
    
    MONTH_NAMES = [
        "መስከረም", "ጥቅምት", "ኅዳር", "ታኅሣሥ", "ጥር", "የካቲት",
        "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜን"
    ]
    
    @staticmethod
    def gregorian_to_ethiopian(greg_date: datetime.date) -> Dict[str, Any]:
        """Convert Gregorian date to Ethiopian calendar using precise lookup data"""
        
        # Use the precise conversion system
        return EthiopianCalendarData.gregorian_to_ethiopian_precise(greg_date)
    
    @staticmethod
    def get_ethiopian_season(eth_date: Dict[str, Any]) -> str:
        """Determine Ethiopian liturgical season using precise data"""
        
        month = eth_date["month"]
        day = eth_date["day"]
        
        # Use the precise liturgical season calculation
        return EthiopianCalendarData.get_liturgical_season(month, day)

class WesternLiturgicalCalendar:
    """
    Western (Roman Catholic) liturgical calendar calculations
    """
    
    @staticmethod
    def get_liturgical_year(date: datetime.date) -> str:
        """Determine liturgical year cycle (A, B, C)"""
        
        # Liturgical year starts on First Sunday of Advent
        advent_start = WesternLiturgicalCalendar.get_advent_start(date.year)
        
        if date >= advent_start:
            cycle_year = date.year + 1
        else:
            cycle_year = date.year
        
        # Year A: years divisible by 3
        # Year B: years with remainder 1 when divided by 3  
        # Year C: years with remainder 2 when divided by 3
        remainder = cycle_year % 3
        
        if remainder == 0:
            return "A"
        elif remainder == 1:
            return "B" 
        else:
            return "C"
    
    @staticmethod
    def get_advent_start(year: int) -> datetime.date:
        """Get First Sunday of Advent"""
        
        # Advent starts on the Sunday closest to November 30
        # (between November 27 and December 3)
        
        christmas = datetime.date(year, 12, 25)
        # Count back 4 Sundays before Christmas
        advent_start = christmas - datetime.timedelta(days=christmas.weekday() + 22)
        
        return advent_start
    
    @staticmethod
    def get_liturgical_season(date: datetime.date) -> Dict[str, Any]:
        """Determine current liturgical season"""
        
        year = date.year
        
        # Calculate key dates
        easter_date = easter(year)
        advent_start = WesternLiturgicalCalendar.get_advent_start(year)
        
        # Christmas season
        christmas = datetime.date(year, 12, 25)
        epiphany = datetime.date(year + 1, 1, 6) if date.month == 12 else datetime.date(year, 1, 6)
        
        # Lent and Easter calculations
        ash_wednesday = easter_date - datetime.timedelta(days=46)
        palm_sunday = easter_date - datetime.timedelta(days=7)
        pentecost = easter_date + datetime.timedelta(days=49)
        
        # Determine season
        if advent_start <= date < christmas:
            season = "Advent"
            color = "Purple"
        elif christmas <= date <= epiphany or (date.month == 12 and date >= christmas):
            season = "Christmas"
            color = "White"
        elif date < ash_wednesday:
            season = "Ordinary Time (Winter)"
            color = "Green"
        elif ash_wednesday <= date < easter_date:
            if date < palm_sunday:
                season = "Lent"
            else:
                season = "Holy Week"
            color = "Purple"
        elif easter_date <= date < pentecost:
            season = "Easter"
            color = "White"
        elif date == pentecost:
            season = "Pentecost"
            color = "Red"
        else:
            season = "Ordinary Time (Summer)"
            color = "Green"
        
        return {
            "season": season,
            "liturgical_color": color,
            "easter_date": easter_date.isoformat(),
            "days_from_easter": (date - easter_date).days
        }

class LiturgicalCalendarManager:
    """
    Manages both Western and Eastern Orthodox liturgical calendars
    """
    
    def __init__(self):
        self.western = WesternLiturgicalCalendar()
        self.ethiopian = EthiopianCalendar()
    
    def get_daily_info(self, date: datetime.date) -> Dict[str, Any]:
        """Get complete liturgical information for a given date"""
        
        # Western calendar info
        western_season = self.western.get_liturgical_season(date)
        liturgical_year = self.western.get_liturgical_year(date)
        
        # Ethiopian calendar info
        eth_date = self.ethiopian.gregorian_to_ethiopian(date)
        eth_season = self.ethiopian.get_ethiopian_season(eth_date)
        
        return {
            "gregorian_date": date.isoformat(),
            "weekday": date.strftime("%A"),
            "western": {
                "liturgical_year": liturgical_year,
                "season_info": western_season,
                "week_number": date.isocalendar()[1]
            },
            "ethiopian": {
                "date": eth_date,
                "season": eth_season,
                "is_fasting_day": self._is_ethiopian_fasting_day(date, eth_date)
            }
        }
    
    def _is_ethiopian_fasting_day(self, greg_date: datetime.date, eth_date: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if it's a fasting day in Ethiopian Orthodox tradition using precise data"""
        
        # Use the precise fasting calculation
        fasting_info = EthiopianCalendarData.is_fasting_day(greg_date, eth_date)
        
        return {
            "is_fasting": fasting_info['is_fasting'],
            "fasting_type": fasting_info['type'],
            "fasting_rules": fasting_info['rules'],
            "reason": fasting_info['reason']
        }
    
    def _get_fasting_rules(self, is_weekly: bool, is_strict: bool) -> List[str]:
        """Get appropriate fasting rules"""
        
        if is_strict:
            return [
                "No animal products",
                "No dairy products", 
                "No eggs",
                "One meal after 3 PM",
                "Prayer and meditation"
            ]
        elif is_weekly:
            return [
                "No meat",
                "No dairy", 
                "Simple foods preferred"
            ]
        else:
            return ["No specific fasting requirements"]

# Global calendar manager
liturgical_manager = LiturgicalCalendarManager()
