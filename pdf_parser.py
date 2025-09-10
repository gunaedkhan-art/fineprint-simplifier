# fineprint_simplifier/pdf_parser.py

import PyPDF2
from PIL import Image
import io
import re

# OCR functionality - EasyOCR (Railway compatible)
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("EasyOCR loaded successfully")
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not available. OCR functionality disabled.")

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Returns a dict with keys: pages, quality_assessment, total_characters, readable_pages
    Uses PyPDF2 for text extraction with quality assessment for scanned PDFs.
    """
    pages = []
    total_characters = 0
    readable_pages = 0
    quality_issues = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"PDF has {total_pages} pages")
            
            for page_number, page in enumerate(pdf_reader.pages, start=1):
                # Try normal text extraction
                text = page.extract_text()
                char_count = len(text) if text else 0
                print(f"Page {page_number}: Extracted {char_count} characters")
                
                # Quality assessment for this page
                page_quality = assess_text_quality(text, page_number)
                
                if not text or not text.strip():
                    # No text found - likely a scanned image
                    quality_issues.append(f"Page {page_number}: No text detected (likely scanned image)")
                    text = f"[OCR needed for page {page_number}]"
                    page_quality = "poor"
                elif page_quality == "poor":
                    quality_issues.append(f"Page {page_number}: Poor text quality (may be scanned)")
                
                if page_quality in ["good", "fair"]:
                    readable_pages += 1
                    total_characters += char_count
                
                pages.append({
                    "page_number": page_number,
                    "text": text.strip(),
                    "quality": page_quality,
                    "char_count": char_count
                })
                
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return {
            "pages": [],
            "quality_assessment": "error",
            "total_characters": 0,
            "readable_pages": 0,
            "total_pages": 0,
            "quality_issues": [f"Error reading PDF: {str(e)}"]
        }
    
    # Overall quality assessment
    overall_quality = assess_overall_quality(readable_pages, total_pages, total_characters, quality_issues)
    
    print(f"Total pages processed: {len(pages)}")
    print(f"Readable pages: {readable_pages}/{total_pages}")
    print(f"Total characters: {total_characters}")
    print(f"Overall quality: {overall_quality}")
    
    return {
        "pages": pages,
        "quality_assessment": overall_quality,
        "total_characters": total_characters,
        "readable_pages": readable_pages,
        "total_pages": total_pages,
        "quality_issues": quality_issues
    }

def assess_text_quality(text: str, page_number: int) -> str:
    """
    Assess the quality of extracted text
    Returns: 'good', 'fair', or 'poor'
    """
    if not text or not text.strip():
        return "poor"
    
    # Check for common OCR artifacts and poor quality indicators
    text_lower = text.lower()
    
    # Indicators of poor quality
    poor_indicators = [
        len(re.findall(r'[^\w\s.,!?;:()\-]', text)) > len(text) * 0.1,  # Too many special characters
        len(re.findall(r'\b[a-z]{1,2}\b', text)) > len(text.split()) * 0.3,  # Too many short words
        len(re.findall(r'[0-9]{10,}', text)) > 0,  # Very long numbers (likely OCR errors)
        len(text.strip()) < 50,  # Very short text for a page
    ]
    
    # Check for readable text patterns
    good_indicators = [
        len(re.findall(r'\b[a-zA-Z]{3,}\b', text)) > len(text.split()) * 0.5,  # Good proportion of normal words
        len(re.findall(r'[.!?]', text)) > 0,  # Has sentence endings
        len(text.strip()) > 200,  # Reasonable amount of text
    ]
    
    poor_count = sum(poor_indicators)
    good_count = sum(good_indicators)
    
    if poor_count >= 2:
        return "poor"
    elif good_count >= 2 and poor_count == 0:
        return "good"
    else:
        return "fair"

def assess_overall_quality(readable_pages: int, total_pages: int, total_characters: int, quality_issues: list) -> str:
    """
    Assess overall document quality
    Returns: 'excellent', 'good', 'fair', 'poor', or 'unreadable'
    """
    if total_pages == 0:
        return "unreadable"
    
    readable_ratio = readable_pages / total_pages
    avg_chars_per_page = total_characters / total_pages if total_pages > 0 else 0
    
    # Excellent: All pages readable, good amount of text
    if readable_ratio == 1.0 and avg_chars_per_page > 500:
        return "excellent"
    
    # Good: Most pages readable, reasonable text
    elif readable_ratio >= 0.8 and avg_chars_per_page > 200:
        return "good"
    
    # Fair: Some pages readable, some text
    elif readable_ratio >= 0.5 and avg_chars_per_page > 100:
        return "fair"
    
    # Poor: Few pages readable, little text
    elif readable_ratio > 0 and avg_chars_per_page > 50:
        return "poor"
    
    # Unreadable: No readable pages
    else:
        return "unreadable"

def extract_text_with_ocr(image_path: str) -> str:
    """
    Extract text from an image using EasyOCR
    Returns the extracted text as a string
    """
    if not EASYOCR_AVAILABLE:
        return ""
    
    try:
        # Initialize EasyOCR reader (English)
        reader = easyocr.Reader(['en'])
        
        # Read text from image
        results = reader.readtext(image_path)
        
        # Combine all detected text
        extracted_text = ""
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Only include high-confidence text
                extracted_text += text + " "
        
        return extracted_text.strip()
    
    except Exception as e:
        print(f"OCR extraction failed: {e}")
        return ""

def get_ocr_text(image_path: str) -> str:
    """
    Get OCR text using EasyOCR
    """
    if not EASYOCR_AVAILABLE:
        return ""
    
    return extract_text_with_ocr(image_path)