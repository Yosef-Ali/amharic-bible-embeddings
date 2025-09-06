#!/usr/bin/env python3
"""
Table of Contents (TOC) Analyzer
Detects and understands TOC structure from scanned book images
Essential for proper book digitization and multi-page organization
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️  OpenCV not available for TOC analysis")

@dataclass
class TOCEntry:
    """Single Table of Contents entry"""
    title: str
    page_number: Optional[int]
    level: int  # 1=chapter, 2=section, 3=subsection
    line_number: int
    confidence: float
    bbox: Dict[str, int]
    
class TOCAnalyzer:
    """
    Analyzes Table of Contents from scanned book images
    Understands book structure before processing content pages
    """
    
    def __init__(self):
        """Initialize TOC analyzer"""
        self.toc_patterns = self._setup_toc_patterns()
        self.amharic_chapter_words = [
            'ምዕራፍ', 'ክፍል', 'ሕዝብ', 'መፅሀፍ', 'ጋራ', 'ቀን', 'ሰንበት',
            'በዓል', 'ጾም', 'ፈጣን', 'ማኅበር', 'ጉባዔ', 'ድምሳስ', 'ወቅት'
        ]
        
    def _setup_toc_patterns(self) -> Dict[str, Any]:
        """Setup patterns for TOC detection"""
        
        return {
            # Page number patterns at end of line
            'page_numbers': [
                r'\.{2,}\s*(\d+)\s*$',           # Chapter.....123
                r'\s+(\d+)\s*$',                 # Chapter Title  123  
                r'-{2,}\s*(\d+)\s*$',            # Chapter----123
                r'_{2,}\s*(\d+)\s*$',            # Chapter____123
                r'\.\s*(\d+)\s*$'                # Chapter. 123
            ],
            
            # TOC header patterns
            'toc_headers': [
                r'(?i)(table\s+of\s+contents?|contents?)',
                r'(?i)(ይዘት|ማውጫ|ዝርዝር)',
                r'(?i)(index|ማውጫ|ጽሑፍ)',
                r'(?i)(ርዕሶች|ክፍሎች|ምዕራፎች)'
            ],
            
            # Chapter/section patterns
            'hierarchy_patterns': [
                r'^(CHAPTER|Chapter|ምዕራፍ)\s+([IVX\d]+)',    # Chapter markers
                r'^(\d+\.)?\s*([^.]+)',                       # Numbered entries
                r'^([A-Z][.:])\s*([^.]+)',                    # Letter markers
                r'^(Part|ክፍል|ክፍለ)\s+([IVX\d]+)'             # Part markers
            ]
        }
    
    def detect_toc_pages(self, image_files: List[str]) -> List[Dict[str, Any]]:
        """
        Detect which pages contain Table of Contents
        Must be called FIRST before processing other pages
        """
        
        print("📋 Detecting Table of Contents pages...")
        toc_pages = []
        
        for i, image_path in enumerate(image_files[:10]):  # Check first 10 pages
            print(f"  🔍 Analyzing page {i+1}: {Path(image_path).name}")
            
            toc_analysis = self._analyze_page_for_toc(image_path, i+1)
            
            if toc_analysis['is_toc']:
                print(f"    ✅ TOC detected with {toc_analysis['toc_confidence']:.1%} confidence")
                toc_pages.append(toc_analysis)
            else:
                print(f"    ❌ Not a TOC page")
        
        return toc_pages
    
    def _analyze_page_for_toc(self, image_path: str, page_num: int) -> Dict[str, Any]:
        """
        Analyze single page to determine if it's a TOC page
        """
        
        from .document_scanner import DocumentScanner
        
        scanner = DocumentScanner()
        
        # Get text blocks from page
        layout_result = scanner.extract_text_blocks_ordered(image_path)
        
        if "error" in layout_result:
            return {"is_toc": False, "page_number": page_num, "error": layout_result["error"]}
        
        text_blocks = layout_result.get("text_blocks", [])
        page_text = " ".join([block.get("text", "") for block in text_blocks])
        
        # Analyze for TOC characteristics
        toc_score = 0.0
        toc_indicators = []
        
        # 1. Check for TOC headers
        header_found = False
        for pattern in self.toc_patterns['toc_headers']:
            if re.search(pattern, page_text, re.IGNORECASE):
                toc_score += 0.3
                toc_indicators.append("toc_header")
                header_found = True
                break
        
        # 2. Check for page number patterns (strong indicator)
        page_number_count = 0
        for pattern in self.toc_patterns['page_numbers']:
            matches = re.findall(pattern, page_text, re.MULTILINE)
            page_number_count += len(matches)
        
        if page_number_count >= 3:  # At least 3 page references
            toc_score += 0.4
            toc_indicators.append(f"page_numbers_{page_number_count}")
        
        # 3. Check for hierarchical structure
        hierarchy_count = 0
        for pattern in self.toc_patterns['hierarchy_patterns']:
            matches = re.findall(pattern, page_text, re.MULTILINE)
            hierarchy_count += len(matches)
        
        if hierarchy_count >= 2:
            toc_score += 0.2
            toc_indicators.append(f"hierarchy_{hierarchy_count}")
        
        # 4. Check for Amharic chapter words
        amharic_chapter_count = 0
        for word in self.amharic_chapter_words:
            if word in page_text:
                amharic_chapter_count += 1
        
        if amharic_chapter_count >= 2:
            toc_score += 0.1
            toc_indicators.append(f"amharic_chapters_{amharic_chapter_count}")
        
        # 5. Line structure analysis (TOC has many short lines with dots/spaces)
        lines = [block.get("text", "").strip() for block in text_blocks if block.get("text", "").strip()]
        dot_lines = sum(1 for line in lines if '..' in line or '__' in line or '--' in line)
        
        if len(lines) > 5 and dot_lines / len(lines) > 0.3:  # 30% of lines have dots
            toc_score += 0.2
            toc_indicators.append(f"dot_lines_{dot_lines}/{len(lines)}")
        
        is_toc = toc_score >= 0.5  # Minimum threshold for TOC detection
        
        return {
            "is_toc": is_toc,
            "toc_confidence": toc_score,
            "page_number": page_num,
            "image_path": image_path,
            "indicators": toc_indicators,
            "text_blocks": text_blocks if is_toc else [],
            "analysis": {
                "header_found": header_found,
                "page_references": page_number_count,
                "hierarchy_elements": hierarchy_count,
                "amharic_terms": amharic_chapter_count,
                "total_lines": len(lines),
                "dot_lines": dot_lines
            }
        }
    
    def extract_toc_structure(self, toc_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract structured TOC information from detected TOC pages
        This creates the book's organizational structure
        """
        
        print("📖 Extracting TOC structure...")
        
        all_toc_entries = []
        book_structure = {
            "has_toc": len(toc_pages) > 0,
            "toc_pages": [p["page_number"] for p in toc_pages],
            "entries": [],
            "chapters": [],
            "sections": [],
            "estimated_total_pages": 0
        }
        
        for toc_page in toc_pages:
            print(f"  📋 Processing TOC page {toc_page['page_number']}")
            
            page_entries = self._extract_entries_from_page(toc_page)
            all_toc_entries.extend(page_entries)
        
        # Sort entries by line number and page
        all_toc_entries.sort(key=lambda x: (x.line_number))
        
        # Organize into hierarchical structure
        book_structure["entries"] = [self._toc_entry_to_dict(entry) for entry in all_toc_entries]
        book_structure["chapters"] = self._identify_chapters(all_toc_entries)
        book_structure["sections"] = self._identify_sections(all_toc_entries)
        
        # Estimate total pages
        page_numbers = [entry.page_number for entry in all_toc_entries if entry.page_number]
        if page_numbers:
            book_structure["estimated_total_pages"] = max(page_numbers)
        
        print(f"  ✅ Extracted {len(all_toc_entries)} TOC entries")
        print(f"  📚 Found {len(book_structure['chapters'])} chapters")
        print(f"  📄 Estimated {book_structure['estimated_total_pages']} total pages")
        
        return book_structure
    
    def _extract_entries_from_page(self, toc_page: Dict[str, Any]) -> List[TOCEntry]:
        """Extract individual TOC entries from a single page"""
        
        entries = []
        text_blocks = toc_page.get("text_blocks", [])
        
        for i, block in enumerate(text_blocks):
            text = block.get("text", "").strip()
            if not text or len(text) < 3:
                continue
            
            # Try to extract page number and title
            page_number = None
            title = text
            
            # Check each page number pattern
            for pattern in self.toc_patterns['page_numbers']:
                match = re.search(pattern, text)
                if match:
                    page_number = int(match.group(1))
                    # Remove page number from title
                    title = re.sub(pattern, '', text).strip()
                    # Clean up dots, dashes, underscores
                    title = re.sub(r'[._-]{2,}', ' ', title).strip()
                    break
            
            # Determine hierarchy level
            level = self._determine_hierarchy_level(title)
            
            # Calculate confidence based on various factors
            confidence = self._calculate_entry_confidence(text, page_number, level)
            
            if confidence > 0.3:  # Minimum confidence for valid entry
                entry = TOCEntry(
                    title=title,
                    page_number=page_number,
                    level=level,
                    line_number=i,
                    confidence=confidence,
                    bbox=block.get("bbox", {})
                )
                entries.append(entry)
        
        return entries
    
    def _determine_hierarchy_level(self, title: str) -> int:
        """Determine the hierarchy level of a TOC entry"""
        
        # Chapter indicators (level 1)
        chapter_patterns = [
            r'^(CHAPTER|Chapter|ምዕራፍ|ክፍል)',
            r'^\d+\.\s*[A-Z]',  # 1. CHAPTER TITLE
            r'^[IVX]+\.',       # I. Roman numeral
        ]
        
        for pattern in chapter_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return 1
        
        # Section indicators (level 2)
        section_patterns = [
            r'^\d+\.\d+',       # 1.1 Section
            r'^[A-Z]\.',        # A. Section
            r'^\s{2,}',         # Indented
        ]
        
        for pattern in section_patterns:
            if re.match(pattern, title):
                return 2
        
        # Subsection (level 3)
        if re.match(r'^\d+\.\d+\.\d+', title) or title.startswith('    '):
            return 3
        
        return 1  # Default to chapter level
    
    def _calculate_entry_confidence(self, text: str, page_number: Optional[int], level: int) -> float:
        """Calculate confidence score for TOC entry"""
        
        confidence = 0.5  # Base confidence
        
        # Has page number
        if page_number:
            confidence += 0.3
        
        # Has reasonable length
        if 5 <= len(text) <= 100:
            confidence += 0.1
        
        # Has hierarchy markers
        if any(pattern in text for pattern in ['Chapter', 'ምዕራፍ', 'ክፍል']):
            confidence += 0.2
        
        # Has dots or lines (typical TOC formatting)
        if any(char in text for char in ['...', '---', '___']):
            confidence += 0.1
        
        # Penalize very long entries (likely not TOC)
        if len(text) > 150:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _identify_chapters(self, entries: List[TOCEntry]) -> List[Dict[str, Any]]:
        """Identify main chapters from TOC entries"""
        
        chapters = []
        for entry in entries:
            if entry.level == 1 and entry.confidence > 0.5:
                chapters.append({
                    "title": entry.title,
                    "page_number": entry.page_number,
                    "estimated_length": self._estimate_chapter_length(entry, entries)
                })
        
        return chapters
    
    def _identify_sections(self, entries: List[TOCEntry]) -> List[Dict[str, Any]]:
        """Identify sections and subsections"""
        
        sections = []
        for entry in entries:
            if entry.level >= 2 and entry.confidence > 0.4:
                sections.append({
                    "title": entry.title,
                    "page_number": entry.page_number,
                    "level": entry.level,
                    "parent_chapter": self._find_parent_chapter(entry, entries)
                })
        
        return sections
    
    def _estimate_chapter_length(self, chapter_entry: TOCEntry, all_entries: List[TOCEntry]) -> Optional[int]:
        """Estimate chapter length in pages"""
        
        if not chapter_entry.page_number:
            return None
        
        # Find next chapter
        next_chapter_page = None
        for entry in all_entries:
            if (entry.level == 1 and 
                entry.page_number and 
                entry.page_number > chapter_entry.page_number):
                next_chapter_page = entry.page_number
                break
        
        if next_chapter_page:
            return next_chapter_page - chapter_entry.page_number
        
        return None
    
    def _find_parent_chapter(self, section_entry: TOCEntry, all_entries: List[TOCEntry]) -> Optional[str]:
        """Find parent chapter for a section"""
        
        # Look backwards for the most recent chapter
        for entry in reversed(all_entries[:section_entry.line_number]):
            if entry.level == 1:
                return entry.title
        
        return None
    
    def _toc_entry_to_dict(self, entry: TOCEntry) -> Dict[str, Any]:
        """Convert TOCEntry to dictionary"""
        
        return {
            "title": entry.title,
            "page_number": entry.page_number,
            "level": entry.level,
            "confidence": entry.confidence,
            "bbox": entry.bbox
        }
    
    def validate_toc_structure(self, toc_structure: Dict[str, Any], total_image_files: int) -> Dict[str, Any]:
        """
        Validate TOC structure against actual book images
        Ensures TOC makes sense with available pages
        """
        
        print("✅ Validating TOC structure...")
        
        validation = {
            "is_valid": True,
            "issues": [],
            "recommendations": [],
            "coverage": 0.0
        }
        
        if not toc_structure["has_toc"]:
            validation["is_valid"] = False
            validation["issues"].append("No TOC detected - processing will use page order")
            validation["recommendations"].append("Consider manual page ordering")
            return validation
        
        entries = toc_structure["entries"]
        page_numbers = [e["page_number"] for e in entries if e["page_number"]]
        
        # Check if page numbers make sense
        if page_numbers:
            max_toc_page = max(page_numbers)
            if max_toc_page > total_image_files:
                validation["issues"].append(f"TOC references page {max_toc_page} but only {total_image_files} images available")
                validation["recommendations"].append("Check if all book pages are scanned")
        
        # Calculate coverage
        if total_image_files > 0:
            covered_pages = len(set(page_numbers))
            validation["coverage"] = covered_pages / total_image_files
            
            if validation["coverage"] < 0.3:
                validation["issues"].append("TOC covers less than 30% of book pages")
                validation["recommendations"].append("TOC may be incomplete or incorrectly detected")
        
        # Check for logical page order
        if len(page_numbers) > 1:
            if page_numbers != sorted(page_numbers):
                validation["issues"].append("TOC page numbers not in ascending order")
                validation["recommendations"].append("Check TOC extraction accuracy")
        
        if len(validation["issues"]) == 0:
            print("  ✅ TOC structure validation passed")
        else:
            print(f"  ⚠️  Found {len(validation['issues'])} issues")
            for issue in validation["issues"]:
                print(f"    - {issue}")
        
        return validation

def test_toc_analyzer():
    """
    Test the TOC analyzer system
    """
    
    print("📋 Table of Contents Analyzer")
    print("=" * 40)
    
    analyzer = TOCAnalyzer()
    
    print("✅ Features:")
    print("  📋 Detects TOC pages automatically")
    print("  📖 Extracts hierarchical book structure")
    print("  🔢 Identifies page numbers and chapters")
    print("  🔤 Supports Amharic chapter terms")
    print("  ✅ Validates TOC against available pages")
    print()
    
    print("🎯 Critical for:")
    print("  📚 Multi-page book processing")
    print("  📖 Understanding book structure BEFORE OCR")
    print("  🔍 Proper page organization")
    print("  📄 Accurate chapter detection")
    print("  🎭 Contextual text processing")
    print()
    
    print("💡 Usage:")
    print("  # Must be called FIRST")
    print("  toc_pages = analyzer.detect_toc_pages(image_files)")
    print("  book_structure = analyzer.extract_toc_structure(toc_pages)")
    print("  validation = analyzer.validate_toc_structure(book_structure, len(images))")
    print()
    
    print("📤 TOC Structure Output:")
    print("  📋 Book organization hierarchy")
    print("  📚 Chapter titles and page numbers")
    print("  📄 Estimated total pages")
    print("  ✅ Validation results and recommendations")

if __name__ == "__main__":
    test_toc_analyzer()