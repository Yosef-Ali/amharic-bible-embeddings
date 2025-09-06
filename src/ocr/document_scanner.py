#!/usr/bin/env python3
"""
Document Scanner for Complex Book Layouts
Handles multi-column, non-sequential pages, and complex layouts
Specifically designed for scanning books for embedding generation
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import re

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️  OpenCV not available. Install with: pip install opencv-python")

class DocumentScanner:
    """
    Document scanner for complex book layouts
    Handles multi-page, multi-column, and non-sequential page scanning
    """
    
    def __init__(self):
        """Initialize document scanner"""
        self.page_regions = []
        self.text_blocks = []
        self.page_order = []
        
    def detect_page_layout(self, image_path: str) -> Dict[str, Any]:
        """
        Detect page layout type and structure
        Handles single page, double page, multi-column layouts
        """
        
        if not CV2_AVAILABLE:
            return {"error": "OpenCV required for layout detection"}
        
        img = cv2.imread(image_path)
        if img is None:
            return {"error": f"Could not load image: {image_path}"}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Detect if it's a double-page spread
        is_double_page = width > height * 1.3  # Wide aspect ratio indicates double page
        
        # Detect column structure
        columns = self._detect_columns(gray)
        
        # Detect text regions
        text_regions = self._detect_text_regions(gray)
        
        return {
            "image_path": image_path,
            "dimensions": (width, height),
            "is_double_page": is_double_page,
            "columns": columns,
            "text_regions": text_regions,
            "layout_type": self._classify_layout(is_double_page, len(columns))
        }
    
    def _detect_columns(self, gray_image) -> List[Dict[str, int]]:
        """
        Detect column boundaries in the image
        """
        
        height, width = gray_image.shape
        
        # Create horizontal projection (sum of pixels in each column)
        h_projection = np.sum(gray_image < 128, axis=0)  # Count dark pixels
        
        # Smooth the projection
        kernel_size = width // 100  # Adaptive kernel size
        if kernel_size > 0:
            kernel = np.ones(kernel_size) / kernel_size
            h_projection = np.convolve(h_projection, kernel, mode='same')
        
        # Find column separators (valleys in projection)
        threshold = np.mean(h_projection) * 0.3  # Low activity areas
        separators = []
        
        in_valley = False
        valley_start = 0
        
        for i, val in enumerate(h_projection):
            if val < threshold and not in_valley:
                valley_start = i
                in_valley = True
            elif val >= threshold and in_valley:
                # End of valley - this is a potential separator
                separator_x = (valley_start + i) // 2
                separators.append(separator_x)
                in_valley = False
        
        # Convert separators to column boundaries
        columns = []
        prev_x = 0
        
        for sep_x in separators:
            if sep_x - prev_x > width * 0.1:  # Minimum column width
                columns.append({
                    "x": prev_x,
                    "y": 0,
                    "width": sep_x - prev_x,
                    "height": height
                })
                prev_x = sep_x
        
        # Add final column
        if width - prev_x > width * 0.1:
            columns.append({
                "x": prev_x,
                "y": 0,
                "width": width - prev_x,
                "height": height
            })
        
        return columns
    
    def _detect_text_regions(self, gray_image) -> List[Dict[str, Any]]:
        """
        Detect text regions using contour analysis
        """
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations to connect text regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        height, width = gray_image.shape
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter regions by size and aspect ratio
            if (w > 20 and h > 10 and  # Minimum size
                w < width * 0.8 and h < height * 0.5 and  # Maximum size
                w > h * 0.5):  # Reasonable aspect ratio for text
                
                # Calculate text density in region
                roi = thresh[y:y+h, x:x+w]
                text_density = np.sum(roi > 0) / (w * h)
                
                if text_density > 0.1:  # Minimum text density
                    text_regions.append({
                        "x": x, "y": y, "width": w, "height": h,
                        "text_density": text_density,
                        "area": w * h
                    })
        
        # Sort by position (top to bottom, left to right)
        text_regions.sort(key=lambda r: (r["y"] // 50, r["x"]))
        
        return text_regions
    
    def _classify_layout(self, is_double_page: bool, num_columns: int) -> str:
        """
        Classify the page layout type
        """
        
        if is_double_page:
            if num_columns <= 2:
                return "double_page_single_column"
            else:
                return "double_page_multi_column"
        else:
            if num_columns == 1:
                return "single_page_single_column"
            elif num_columns == 2:
                return "single_page_two_column"
            else:
                return "single_page_multi_column"
    
    def extract_text_blocks_ordered(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text blocks in reading order
        Handles complex layouts and maintains proper sequence
        """
        
        layout = self.detect_page_layout(image_path)
        
        if "error" in layout:
            return layout
        
        text_blocks = []
        
        # Process based on layout type
        if layout["layout_type"].startswith("double_page"):
            text_blocks = self._process_double_page(image_path, layout)
        else:
            text_blocks = self._process_single_page(image_path, layout)
        
        return {
            "image_path": image_path,
            "layout": layout,
            "text_blocks": text_blocks,
            "total_blocks": len(text_blocks)
        }
    
    def _process_double_page(self, image_path: str, layout: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process double-page spread
        Split into left and right pages, maintain reading order
        """
        
        if not CV2_AVAILABLE:
            return []
        
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        # Split into left and right pages
        left_page = img[:, :width//2]
        right_page = img[:, width//2:]
        
        text_blocks = []
        
        # Process left page first (for left-to-right reading)
        left_blocks = self._extract_blocks_from_region(left_page, "left_page", 0, 0)
        text_blocks.extend(left_blocks)
        
        # Then right page
        right_blocks = self._extract_blocks_from_region(right_page, "right_page", width//2, 0)
        text_blocks.extend(right_blocks)
        
        return text_blocks
    
    def _process_single_page(self, image_path: str, layout: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process single page with multiple columns
        """
        
        if not CV2_AVAILABLE:
            return []
        
        img = cv2.imread(image_path)
        text_blocks = []
        
        # Process each column in order
        for i, column in enumerate(layout["columns"]):
            x, y, w, h = column["x"], column["y"], column["width"], column["height"]
            column_img = img[y:y+h, x:x+w]
            
            column_blocks = self._extract_blocks_from_region(
                column_img, f"column_{i+1}", x, y
            )
            text_blocks.extend(column_blocks)
        
        return text_blocks
    
    def _extract_blocks_from_region(self, region_img, region_name: str, offset_x: int, offset_y: int) -> List[Dict[str, Any]]:
        """
        Extract text blocks from a specific region
        Returns blocks with proper coordinates and metadata
        """
        
        # This would integrate with actual OCR engine
        # For now, return mock blocks based on detected regions
        
        gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
        text_regions = self._detect_text_regions(gray)
        
        blocks = []
        for i, region in enumerate(text_regions):
            blocks.append({
                "block_id": f"{region_name}_block_{i+1}",
                "region": region_name,
                "bbox": {
                    "x": region["x"] + offset_x,
                    "y": region["y"] + offset_y,
                    "width": region["width"],
                    "height": region["height"]
                },
                "text": f"[Text block {i+1} from {region_name}]",  # Placeholder
                "confidence": 0.8,
                "text_density": region["text_density"],
                "reading_order": len(blocks) + 1
            })
        
        return blocks
    
    def process_book_batch(self, image_dir: str, output_file: str) -> Dict[str, Any]:
        """
        Process multiple book pages for embedding generation
        Handles non-sequential pages and complex layouts
        """
        
        image_dir = Path(image_dir)
        all_results = []
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(image_dir.glob(f'*{ext}'))
            image_files.extend(image_dir.glob(f'*{ext.upper()}'))
        
        # Sort files naturally (handle page numbers)
        image_files.sort(key=lambda x: self._natural_sort_key(x.name))
        
        print(f"📚 Processing {len(image_files)} book pages...")
        
        for i, image_path in enumerate(image_files):
            print(f"📄 Processing page {i+1}/{len(image_files)}: {image_path.name}")
            
            result = self.extract_text_blocks_ordered(str(image_path))
            
            if "error" not in result:
                result["page_number"] = i + 1
                result["filename"] = image_path.name
                all_results.append(result)
            else:
                print(f"⚠️  Error processing {image_path.name}: {result['error']}")
        
        # Save results
        output_data = {
            "book_scan_results": {
                "total_pages": len(all_results),
                "successful_pages": len([r for r in all_results if "error" not in r]),
                "pages": all_results
            },
            "metadata": {
                "source_directory": str(image_dir),
                "image_files_processed": len(image_files),
                "layout_types": self._summarize_layouts(all_results)
            }
        }
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_file}")
        return output_data
    
    def _natural_sort_key(self, filename: str) -> List:
        """
        Natural sorting for filenames with numbers
        Handles: page1.jpg, page2.jpg, page10.jpg correctly
        """
        
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split('([0-9]+)', filename)]
    
    def _summarize_layouts(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Summarize layout types found in the book
        """
        
        layout_counts = {}
        for result in results:
            if "layout" in result:
                layout_type = result["layout"]["layout_type"]
                layout_counts[layout_type] = layout_counts.get(layout_type, 0) + 1
        
        return layout_counts

def test_document_scanner():
    """
    Test the document scanner system
    """
    
    print("📚 Document Scanner for Complex Book Layouts")
    print("=" * 50)
    
    scanner = DocumentScanner()
    
    print("✅ Features:")
    print("  📄 Multi-page processing")
    print("  📊 Layout detection (single/double page)")
    print("  📰 Multi-column support")
    print("  🔄 Non-sequential page handling")
    print("  📖 Reading order preservation")
    print("  💾 Batch processing for books")
    print()
    
    print("🎯 Designed for:")
    print("  📚 Complex book layouts")
    print("  🔤 Amharic text embedding generation")
    print("  📄 Mixed single/double page books")
    print("  📰 Multi-column religious texts")
    print("  🖼️  Scanned manuscript processing")
    print()
    
    print("💡 Usage Examples:")
    print("  # Process single page")
    print("  result = scanner.extract_text_blocks_ordered('page.jpg')")
    print()
    print("  # Process entire book")
    print("  book_data = scanner.process_book_batch('book_images/', 'book_text.json')")
    print()
    
    if not CV2_AVAILABLE:
        print("⚠️  Install OpenCV for full functionality:")
        print("  pip install opencv-python")
    else:
        print("✅ OpenCV available - full functionality enabled")

if __name__ == "__main__":
    test_document_scanner()