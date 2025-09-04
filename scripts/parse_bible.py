#!/usr/bin/env python3
"""
Parses the raw Amharic Bible text into a structured format.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.preprocessing.amharic_cleaner import amharic_cleaner
from src.preprocessing.final_biblical_parser import CatholicAmharicBibleParser
from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR

def main():
    """
    Main function to clean and parse the Amharic Bible.
    """
    print("Starting Bible parsing process...")

    # Define file paths
    raw_bible_path = RAW_DATA_DIR / "amharic_bible_raw.txt"
    cleaned_bible_path = PROCESSED_DATA_DIR / "amharic_bible_cleaned.txt"
    
    # 1. Clean the raw text
    print(f"Cleaning raw Bible text from {raw_bible_path}...")
    with open(raw_bible_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    cleaned_text = amharic_cleaner.clean_text(raw_text)
    
    with open(cleaned_bible_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    print(f"Cleaned Bible text saved to {cleaned_bible_path}")

    # 2. Parse the cleaned text
    print("Parsing the cleaned Bible text...")
    parser = CatholicAmharicBibleParser()
    parsed_data = parser.parse_catholic_bible(str(cleaned_bible_path))
    
    # 3. Save the parsed data
    print("Saving parsed data...")
    output_files = parser.save_results(parsed_data, str(PROCESSED_DATA_DIR))
    
    print("\nParsing complete!")
    print(f"  - Books parsed: {parsed_data['total_books']}/73")
    print(f"  - Chapters: {parsed_data['total_chapters']}")
    print(f"  - Verses: {parsed_data['total_verses']}")
    print("\nOutput files:")
    for key, value in output_files.items():
        print(f"  - {key}: {value}")

if __name__ == "__main__":
    main()
