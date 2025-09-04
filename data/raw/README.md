# Add your Amharic Bible files here

This directory should contain your Amharic Bible text files in one of these formats:

## Supported Formats

### 1. Plain Text (.txt)
```
ኦሪት ዘፍጥረት ምዕራፍ 1
1 መጀመሪያ ላይ እግዚአብሔር ሰማይንና ምድርን ፈጠረ።
2 ምድርም ባዶና ክፉ ነበረች፤ ጨለማውም በጥልቁ ላይ ነበር፤...
```

### 2. JSON Structure (.json)
```json
{
  "Genesis": {
    "chapter_1": "መጀመሪያ ላይ እግዚአብሔር ሰማይንና ምድርን ፈጠረ...",
    "chapter_2": "..."
  },
  "Exodus": {
    "chapter_1": "...",
    "chapter_2": "..."
  }
}
```

### 3. CSV Format (.csv)
```csv
book,chapter,verse,text
Genesis,1,1,"መጀመሪያ ላይ እግዚአብሔር ሰማይንና ምድርን ፈጠረ።"
Genesis,1,2,"ምድርም ባዶና ክፉ ነበረች፤"
```

## Sources for Amharic Bible Text

1. **Ethiopian Bible Society**: Official Amharic translations
2. **Word Project**: https://www.wordproject.org/bibles/am/ 
3. **Bible Gateway**: Some Amharic versions available
4. **Local Ethiopian churches**: May have digital copies
5. **Academic institutions**: Ethiopian universities with digitized texts

## File Naming Conventions

- Use descriptive names like `amharic_bible_full.txt`
- For multiple books: `genesis_amharic.txt`, `matthew_amharic.txt`
- Include translation version if known: `amharic_bible_1962.json`

## Processing Notes

The system will automatically:
- Detect file format and structure
- Clean and normalize Amharic text
- Handle Ge'ez numerals and Fidel variations
- Preserve verse and chapter boundaries
- Generate contextual enhancements using modern LLMs

Place your files here and run `python scripts/process_bible.py` to begin processing.
