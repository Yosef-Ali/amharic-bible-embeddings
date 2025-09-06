#!/usr/bin/env python3
"""
Amharic OCR System
Optical Character Recognition for Amharic text and biblical documents
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import re
from pathlib import Path
import random

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    # Create mock numpy for type hints
    class MockNumpy:
        ndarray = Any
    np = MockNumpy()
    print("⚠️  OpenCV not available. OCR functionality limited.")

class AmharicOCR:
    """
    Amharic OCR system for extracting text from images
    Specialized for Ethiopian biblical and liturgical documents
    """
    
    # Amharic character patterns and common words
    AMHARIC_CHARS = [
        'ሀ', 'ሁ', 'ሂ', 'ሃ', 'ሄ', 'ህ', 'ሆ', 'ሇ',
        'ለ', 'ሉ', 'ሊ', 'ላ', 'ሌ', 'ል', 'ሎ', 'ሏ',
        'ሐ', 'ሑ', 'ሒ', 'ሓ', 'ሔ', 'ሕ', 'ሖ', 'ሗ',
        'መ', 'ሙ', 'ሚ', 'ማ', 'ሜ', 'ም', 'ሞ', 'ሟ',
        'ሠ', 'ሡ', 'ሢ', 'ሣ', 'ሤ', 'ሥ', 'ሦ', 'ሧ',
        'ረ', 'ሩ', 'ሪ', 'ራ', 'ሬ', 'ር', 'ሮ', 'ሯ',
        'ሰ', 'ሱ', 'ሲ', 'ሳ', 'ሴ', 'ስ', 'ሶ', 'ሷ',
        'ሸ', 'ሹ', 'ሺ', 'ሻ', 'ሼ', 'ሽ', 'ሾ', 'ሿ',
        'ቀ', 'ቁ', 'ቂ', 'ቃ', 'ቄ', 'ቅ', 'ቆ', 'ቇ',
        'በ', 'ቡ', 'ቢ', 'ባ', 'ቤ', 'ብ', 'ቦ', 'ቧ',
        'ተ', 'ቱ', 'ቲ', 'ታ', 'ቴ', 'ት', 'ቶ', 'ቷ',
        'ቸ', 'ቹ', 'ቺ', 'ቻ', 'ቼ', 'ች', 'ቾ', 'ቿ',
        'ኀ', 'ኁ', 'ኂ', 'ኃ', 'ኄ', 'ኅ', 'ኆ', 'ኇ',
        'ነ', 'ኑ', 'ኒ', 'ና', 'ኔ', 'ን', 'ኖ', 'ኗ',
        'ኘ', 'ኙ', 'ኚ', 'ኛ', 'ኜ', 'ኝ', 'ኞ', 'ኟ',
        'አ', 'ኡ', 'ኢ', 'ኣ', 'ኤ', 'እ', 'ኦ', 'ኧ',
        'ከ', 'ኩ', 'ኪ', 'ካ', 'ኬ', 'ክ', 'ኮ', 'ኯ',
        'ኸ', 'ኹ', 'ኺ', 'ኻ', 'ኼ', 'ኽ', 'ኾ', '኿',
        'ወ', 'ዉ', 'ዊ', 'ዋ', 'ዌ', 'ው', 'ዎ', 'ዏ',
        'ዐ', 'ዑ', 'ዒ', 'ዓ', 'ዔ', 'ዕ', 'ዖ', '዗',
        'ዘ', 'ዙ', 'ዚ', 'ዛ', 'ዜ', 'ዝ', 'ዞ', 'ዟ',
        'ዠ', 'ዡ', 'ዢ', 'ዣ', 'ዤ', 'ዥ', 'ዦ', 'ዧ',
        'የ', 'ዩ', 'ዪ', 'ያ', 'ዬ', 'ይ', 'ዮ', 'ዯ',
        'ደ', 'ዱ', 'ዲ', 'ዳ', 'ዴ', 'ድ', 'ዶ', 'ዷ',
        'ጀ', 'ጁ', 'ጂ', 'ጃ', 'ጄ', 'ጅ', 'ጆ', 'ጇ',
        'ገ', 'ጉ', 'ጊ', 'ጋ', 'ጌ', 'ግ', 'ጎ', 'ጏ',
        'ጠ', 'ጡ', 'ጢ', 'ጣ', 'ጤ', 'ጥ', 'ጦ', 'ጧ',
        'ጨ', 'ጩ', 'ጪ', 'ጫ', 'ጬ', 'ጭ', 'ጮ', 'ጯ',
        'ጰ', 'ጱ', 'ጲ', 'ጳ', 'ጴ', 'ጵ', 'ጶ', 'ጷ',
        'ጸ', 'ጹ', 'ጺ', 'ጻ', 'ጼ', 'ጽ', 'ጾ', 'ጿ',
        'ፀ', 'ፁ', 'ፂ', 'ፃ', 'ፄ', 'ፅ', 'ፆ', 'ፇ',
        'ፈ', 'ፉ', 'ፊ', 'ፋ', 'ፌ', 'ፍ', 'ፎ', 'ፏ',
        'ፐ', 'ፑ', 'ፒ', 'ፓ', 'ፔ', 'ፕ', 'ፖ', 'ፗ'
    ]
    
    # Common biblical/liturgical words in Amharic
    BIBLICAL_WORDS = [
        'እግዚአብሔር',  # God
        'ኢየሱስ',      # Jesus
        'መንፈስ',       # Spirit
        'ቅዱስ',        # Holy
        'መስቀል',       # Cross
        'ሰላም',        # Peace
        'ፍቅር',        # Love
        'ጌታ',         # Lord
        'አምላክ',       # God
        'መላእክት',      # Angels
        'ዐብይ',        # Great
        'ቤተ',         # House/Church
        'ክርስትያን',     # Christian
        'በረከት',       # Blessing
        'ጸሎት',        # Prayer
        'ምስጋና',       # Thanksgiving
        'ሰማይ',        # Heaven
        'ምድር',        # Earth
        'መጽሐፍ',       # Book/Bible
        'ቅዱሳን'        # Saints
    ]
    
    # Ethiopian numerals
    ETHIOPIAN_NUMERALS = {
        '፩': '1', '፪': '2', '፫': '3', '፬': '4', '፭': '5',
        '፮': '6', '፯': '7', '፰': '8', '፱': '9', '፲': '10',
        '፳': '20', '፴': '30', '፵': '40', '፶': '50',
        '፷': '60', '፸': '70', '፹': '80', '፺': '90', '፻': '100'
    }
    
    def __init__(self):
        """Initialize Amharic OCR system"""
        self.confidence_threshold = 0.7
        self.min_word_length = 2
    
    def preprocess_image(self, image_path: str):
        """
        Preprocess image for better OCR results
        Specialized for Amharic text recognition
        """
        
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV is required for image preprocessing. Install with: pip install opencv-python")
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive thresholding for better text extraction
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up text
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_regions(self, processed_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Extract text regions from processed image
        Returns bounding boxes of potential text areas
        """
        
        # Find contours
        contours, _ = cv2.findContours(
            processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        text_regions = []
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter based on size (typical for Amharic characters)
            if w > 10 and h > 15 and w < 500 and h < 100:
                # Check aspect ratio
                aspect_ratio = w / h
                if 0.1 < aspect_ratio < 10:  # Reasonable aspect ratio for text
                    text_regions.append((x, y, w, h))
        
        # Sort regions by y-coordinate (top to bottom)
        text_regions.sort(key=lambda region: region[1])
        
        return text_regions
    
    def recognize_amharic_characters(self, image_region: np.ndarray) -> str:
        """
        Recognize Amharic characters in an image region
        Placeholder for actual OCR implementation
        """
        
        # This is a simplified placeholder implementation
        # In a real system, you would use trained models like:
        # - TensorFlow/PyTorch models trained on Amharic text
        # - Tesseract with Amharic language support
        # - Custom CNN models for Fidel script recognition
        
        # For now, return a mock recognition based on image properties
        height, width = image_region.shape[:2]
        area = height * width
        
        # Mock character recognition based on region characteristics
        if area < 500:
            return random.choice(self.AMHARIC_CHARS[:10])  # Common characters
        elif area < 1000:
            return random.choice(self.AMHARIC_CHARS[10:30])
        else:
            return random.choice(self.BIBLICAL_WORDS[:5])  # Likely a word
    
    def post_process_text(self, raw_text: str) -> str:
        """
        Basic post-processing of extracted text
        Only handles formatting and numeral conversion
        Spell correction left for native speakers
        """
        
        # Remove extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', raw_text.strip())
        
        # Convert Ethiopian numerals to Arabic
        for eth_num, arab_num in self.ETHIOPIAN_NUMERALS.items():
            cleaned_text = cleaned_text.replace(eth_num, arab_num)
        
        # NOTE: Spell correction intentionally omitted
        # Amharic biblical text requires native speaker knowledge
        # LLMs don't fully understand Amharic religious vocabulary
        
        return cleaned_text
    
    # Spell correction methods removed - left for native speakers
    # Amharic biblical vocabulary requires deep cultural and religious knowledge
    # that current LLMs cannot adequately handle
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Main method to extract Amharic text from an image
        """
        
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # Extract text regions
            regions = self.extract_text_regions(processed_img)
            
            # Recognize text in each region
            recognized_texts = []
            for x, y, w, h in regions:
                region = processed_img[y:y+h, x:x+w]
                text = self.recognize_amharic_characters(region)
                if text:
                    recognized_texts.append({
                        'text': text,
                        'bbox': (x, y, w, h),
                        'confidence': 0.8  # Mock confidence
                    })
            
            # Combine all text
            full_text = ' '.join([item['text'] for item in recognized_texts])
            
            # Post-process
            processed_text = self.post_process_text(full_text)
            
            return {
                'raw_text': full_text,
                'processed_text': processed_text,
                'regions': recognized_texts,
                'total_regions': len(regions),
                'success': True
            }
            
        except Exception as e:
            return {
                'raw_text': '',
                'processed_text': '',
                'regions': [],
                'total_regions': 0,
                'success': False,
                'error': str(e)
            }
    
    def batch_process_images(self, image_dir: str) -> List[Dict[str, Any]]:
        """
        Process multiple images in a directory
        """
        
        results = []
        image_dir = Path(image_dir)
        
        # Supported image formats
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        
        for image_path in image_dir.glob('*'):
            if image_path.suffix.lower() in image_extensions:
                result = self.extract_text_from_image(str(image_path))
                result['filename'] = image_path.name
                results.append(result)
        
        return results

def test_amharic_ocr():
    """
    Test the Amharic OCR system
    """
    
    print("🇪🇹 Amharic OCR System Test")
    print("=" * 40)
    
    ocr = AmharicOCR()
    
    print("📝 Amharic Character Set Size:", len(ocr.AMHARIC_CHARS))
    print("📖 Biblical Vocabulary Size:", len(ocr.BIBLICAL_WORDS))
    print("🔢 Ethiopian Numerals:", len(ocr.ETHIOPIAN_NUMERALS))
    print()
    
    print("🔤 Sample Amharic Characters:")
    print(' '.join(ocr.AMHARIC_CHARS[:20]))
    print()
    
    print("📚 Sample Biblical Words:")
    for word in ocr.BIBLICAL_WORDS[:10]:
        print(f"  - {word}")
    print()
    
    print("🔢 Ethiopian Numerals:")
    for eth_num, arab_num in list(ocr.ETHIOPIAN_NUMERALS.items())[:10]:
        print(f"  {eth_num} = {arab_num}")
    
    print()
    print("✅ Amharic OCR System Ready!")
    print("📌 Note: This is a framework. Actual OCR requires trained models.")

if __name__ == "__main__":
    test_amharic_ocr()