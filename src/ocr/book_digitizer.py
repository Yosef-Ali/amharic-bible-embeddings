#!/usr/bin/env python3
"""
Complete Book Digitization Pipeline
OCR → Embeddings + PDF Recreation with Original Layout
Specifically designed for Amharic books and complex manuscripts
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib
from datetime import datetime

try:
    import cv2
    import numpy as np
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfbase import pdfutils
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    from reportlab.lib.utils import ImageReader
    CV2_AVAILABLE = True
    PDF_AVAILABLE = True
except ImportError as e:
    CV2_AVAILABLE = False
    PDF_AVAILABLE = False
    print(f"⚠️  Missing dependencies: {e}")
    print("Install with: pip install opencv-python reportlab pillow")

class BookDigitizer:
    """
    Complete book digitization system
    1. OCR text extraction for embeddings
    2. PDF recreation maintaining original layout
    """
    
    def __init__(self):
        """Initialize book digitizer"""
        self.chunk_size = 500
        self.overlap = 50
        self.output_formats = ['embeddings', 'pdf', 'text']
        
        # Try to register Amharic font if available
        self.amharic_font_available = self._setup_fonts()
    
    def _setup_fonts(self) -> bool:
        """Setup fonts for Amharic text in PDF"""
        try:
            # Try to find system Amharic fonts
            possible_fonts = [
                '/System/Library/Fonts/Kefa.ttc',  # macOS
                '/usr/share/fonts/truetype/abyssinica/AbyssinicaSIL-Regular.ttf',  # Linux
                'C:/Windows/Fonts/nyala.ttf',  # Windows
                'fonts/NotoSansEthiopic-Regular.ttf'  # Local font
            ]
            
            for font_path in possible_fonts:
                if Path(font_path).exists():
                    pdfmetrics.registerFont(TTFont('AmharicFont', font_path))
                    print(f"✅ Registered Amharic font: {font_path}")
                    return True
            
            print("⚠️  No Amharic font found - using default font")
            return False
            
        except Exception as e:
            print(f"⚠️  Font setup failed: {e}")
            return False
    
    def digitize_book(self, image_dir: str, output_dir: str, book_title: str = "Amharic Book") -> Dict[str, Any]:
        """
        Complete book digitization pipeline
        Input: Directory of scanned book images
        Output: Embeddings data + Recreated PDF + Text files
        """
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print(f"📚 Digitizing Book: {book_title}")
        print("=" * 60)
        
        # Step 1: OCR Processing
        print("🔍 Step 1: OCR Text Extraction...")
        ocr_results = self._extract_text_from_images(image_dir, output_dir)
        
        # Step 2: Generate Embeddings Data
        print("📝 Step 2: Preparing Embedding Data...")
        embedding_data = self._create_embedding_data(ocr_results, book_title)
        
        # Step 3: Create Searchable PDF
        print("📄 Step 3: Creating PDF with Original Layout...")
        pdf_path = self._create_layout_pdf(image_dir, ocr_results, output_dir, book_title)
        
        # Step 4: Save All Outputs
        print("💾 Step 4: Saving All Formats...")
        output_files = self._save_all_formats(embedding_data, output_dir, book_title)
        
        result = {
            "book_title": book_title,
            "digitization_complete": True,
            "output_files": output_files,
            "statistics": {
                "pages_processed": len(ocr_results.get("pages", [])),
                "total_text_blocks": sum(len(p.get("text_blocks", [])) for p in ocr_results.get("pages", [])),
                "total_chunks": len(embedding_data.get("chunks", [])),
                "formats_created": len(output_files)
            }
        }
        
        print("✅ Book Digitization Complete!")
        self._print_results(result)
        
        return result
    
    def _extract_text_from_images(self, image_dir: str, output_dir: Path) -> Dict[str, Any]:
        """
        Extract text from all book images using document scanner
        """
        
        from .document_scanner import DocumentScanner
        
        scanner = DocumentScanner()
        ocr_output_file = output_dir / "book_ocr_raw.json"
        
        # Process all images in the directory
        ocr_data = scanner.process_book_batch(str(image_dir), str(ocr_output_file))
        
        return ocr_data
    
    def _create_embedding_data(self, ocr_results: Dict[str, Any], book_title: str) -> Dict[str, Any]:
        """
        Create embedding-ready data from OCR results
        """
        
        from .embedding_pipeline import EmbeddingPipeline
        
        pipeline = EmbeddingPipeline()
        pipeline.chunk_size = self.chunk_size
        pipeline.overlap = self.overlap
        
        # Create temporary file for processing
        temp_ocr_file = "temp_ocr.json"
        with open(temp_ocr_file, 'w', encoding='utf-8') as f:
            json.dump(ocr_results, f, ensure_ascii=False)
        
        embedding_data = pipeline.process_ocr_results(temp_ocr_file)
        embedding_data["book_metadata"] = {
            "title": book_title,
            "digitization_date": datetime.now().isoformat(),
            "format_version": "1.0"
        }
        
        # Clean up temp file
        Path(temp_ocr_file).unlink(missing_ok=True)
        
        return embedding_data
    
    def _create_layout_pdf(self, image_dir: str, ocr_results: Dict[str, Any], output_dir: Path, book_title: str) -> str:
        """
        Create PDF that recreates original layout with searchable text
        """
        
        if not PDF_AVAILABLE:
            print("⚠️  PDF creation requires reportlab. Skipping PDF generation.")
            return ""
        
        pdf_path = output_dir / f"{book_title.replace(' ', '_')}_recreated.pdf"
        
        # Get image files
        image_dir = Path(image_dir)
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(image_dir.glob(f'*{ext}'))
            image_files.extend(image_dir.glob(f'*{ext.upper()}'))
        
        image_files.sort(key=lambda x: self._natural_sort_key(x.name))
        
        # Create PDF
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        page_width, page_height = A4
        
        pages_data = ocr_results.get("book_scan_results", {}).get("pages", [])
        
        for i, (image_file, page_data) in enumerate(zip(image_files, pages_data)):
            print(f"  📄 Processing page {i+1}/{len(image_files)}: {image_file.name}")
            
            # Add background image
            try:
                img = ImageReader(str(image_file))
                c.drawImage(img, 0, 0, width=page_width, height=page_height, preserveAspectRatio=True)
            except Exception as e:
                print(f"    ⚠️  Could not add image: {e}")
            
            # Add invisible text for searchability
            self._add_searchable_text(c, page_data, page_width, page_height)
            
            # Add page
            if i < len(image_files) - 1:  # Not the last page
                c.showPage()
        
        # Save PDF
        c.save()
        print(f"  ✅ PDF created: {pdf_path}")
        
        return str(pdf_path)
    
    def _add_searchable_text(self, canvas_obj, page_data: Dict[str, Any], page_width: float, page_height: float):
        """
        Add invisible searchable text overlay on PDF page
        """
        
        text_blocks = page_data.get("text_blocks", [])
        if not text_blocks:
            return
        
        # Get original image dimensions
        layout = page_data.get("layout", {})
        orig_width, orig_height = layout.get("dimensions", [800, 1200])
        
        # Calculate scaling factors
        x_scale = page_width / orig_width
        y_scale = page_height / orig_height
        
        for block in text_blocks:
            bbox = block.get("bbox", {})
            text = block.get("text", "").strip()
            
            if not text or text.startswith("[Text block"):  # Skip placeholders
                continue
            
            # Convert coordinates
            x = bbox.get("x", 0) * x_scale
            y = page_height - (bbox.get("y", 0) + bbox.get("height", 0)) * y_scale  # Flip Y coordinate
            
            # Set text properties
            canvas_obj.setFillColorRGB(0, 0, 0, 0)  # Invisible text
            
            # Use Amharic font if available, otherwise default
            if self.amharic_font_available and self._contains_amharic(text):
                canvas_obj.setFont("AmharicFont", 12)
            else:
                canvas_obj.setFont("Helvetica", 12)
            
            # Draw text
            try:
                canvas_obj.drawString(x, y, text)
            except Exception as e:
                # Fallback for problematic characters
                try:
                    canvas_obj.setFont("Helvetica", 12)
                    # Replace problematic characters
                    safe_text = text.encode('ascii', 'ignore').decode('ascii')
                    if safe_text.strip():
                        canvas_obj.drawString(x, y, safe_text)
                except:
                    pass  # Skip this text block
    
    def _contains_amharic(self, text: str) -> bool:
        """Check if text contains Amharic characters"""
        # Amharic Unicode range: U+1200–U+137F
        return any(0x1200 <= ord(char) <= 0x137F for char in text)
    
    def _save_all_formats(self, embedding_data: Dict[str, Any], output_dir: Path, book_title: str) -> Dict[str, str]:
        """
        Save book in all requested formats
        """
        
        output_files = {}
        safe_title = book_title.replace(' ', '_').replace('/', '_')
        
        # 1. Embedding data (JSON)
        embedding_file = output_dir / f"{safe_title}_embeddings.json"
        with open(embedding_file, 'w', encoding='utf-8') as f:
            json.dump(embedding_data, f, indent=2, ensure_ascii=False)
        output_files["embeddings"] = str(embedding_file)
        
        # 2. Plain text (for quick reading)
        text_file = output_dir / f"{safe_title}_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"# {book_title}\n")
            f.write(f"Digitized on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for chunk in embedding_data.get("chunks", []):
                f.write(f"=== Page {chunk.get('page_number', '?')} - {chunk.get('chunk_id', '')} ===\n")
                f.write(f"{chunk.get('text', '')}\n\n")
        output_files["text"] = str(text_file)
        
        # 3. Metadata file
        metadata_file = output_dir / f"{safe_title}_metadata.json"
        metadata = {
            "book_info": embedding_data.get("book_metadata", {}),
            "statistics": embedding_data.get("statistics", {}),
            "digitization_info": {
                "pipeline_version": "1.0",
                "chunk_size": self.chunk_size,
                "overlap": self.overlap,
                "formats": list(output_files.keys())
            }
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        output_files["metadata"] = str(metadata_file)
        
        # 4. Training data (simplified for ML models)
        training_file = output_dir / f"{safe_title}_training.jsonl"
        with open(training_file, 'w', encoding='utf-8') as f:
            for chunk in embedding_data.get("chunks", []):
                training_record = {
                    "text": chunk.get("text", ""),
                    "metadata": {
                        "book": book_title,
                        "page": chunk.get("page_number"),
                        "chunk_id": chunk.get("chunk_id"),
                        "layout": chunk.get("layout_type")
                    }
                }
                f.write(json.dumps(training_record, ensure_ascii=False) + '\n')
        output_files["training"] = str(training_file)
        
        return output_files
    
    def _natural_sort_key(self, filename: str) -> List:
        """Natural sorting for filenames with numbers"""
        import re
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        return [convert(c) for c in re.split('([0-9]+)', filename)]
    
    def _print_results(self, result: Dict[str, Any]):
        """Print digitization results"""
        
        print("\n" + "🎉 BOOK DIGITIZATION COMPLETE" + " 🎉")
        print("=" * 60)
        
        stats = result["statistics"]
        print(f"📚 Book: {result['book_title']}")
        print(f"📄 Pages processed: {stats['pages_processed']}")
        print(f"🔤 Text blocks extracted: {stats['total_text_blocks']}")
        print(f"📦 Embedding chunks: {stats['total_chunks']}")
        print(f"📁 Output formats: {stats['formats_created']}")
        print()
        
        print("📤 Output Files:")
        for format_name, file_path in result["output_files"].items():
            print(f"  📄 {format_name.title()}: {Path(file_path).name}")
        print()
        
        print("✅ Ready for:")
        print("  🤖 AI model training (embeddings + training data)")
        print("  🔍 Full-text search (PDF with searchable text)")
        print("  📖 Human reading (recreated PDF with original layout)")
        print("  💾 Archive storage (all formats preserved)")

def test_book_digitizer():
    """
    Test the complete book digitization system
    """
    
    print("📚 Complete Book Digitization System")
    print("=" * 50)
    
    digitizer = BookDigitizer()
    
    print("✅ Features:")
    print("  🔍 OCR text extraction for embeddings")
    print("  📄 PDF recreation with original layout")
    print("  🔍 Searchable text overlay in PDF")
    print("  🔤 Multiple output formats")
    print("  📚 Batch processing for entire books")
    print("  🌍 Amharic font support")
    print()
    
    print("📤 Output Formats:")
    print("  📦 embeddings.json - AI training data")
    print("  📄 recreated.pdf - Searchable PDF with layout")
    print("  📝 text.txt - Plain text version")
    print("  📊 metadata.json - Book statistics")
    print("  🤖 training.jsonl - ML training format")
    print()
    
    print("💡 Usage:")
    print("  result = digitizer.digitize_book(")
    print("      'book_images/',     # Scanned pages")
    print("      'output/',         # Output directory")
    print("      'Amharic Bible'    # Book title")
    print("  )")
    print()
    
    if not CV2_AVAILABLE:
        print("⚠️  Install OpenCV: pip install opencv-python")
    if not PDF_AVAILABLE:
        print("⚠️  Install ReportLab: pip install reportlab pillow")
    
    if CV2_AVAILABLE and PDF_AVAILABLE:
        print("✅ All dependencies available - system ready!")

if __name__ == "__main__":
    test_book_digitizer()