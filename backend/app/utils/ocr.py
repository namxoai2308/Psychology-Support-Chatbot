"""Gemini Vision OCR for PDF scans (optional)"""
import os
from io import BytesIO
from typing import List
from pdf2image import convert_from_path
from PIL import Image
import google.generativeai as genai


class GeminiVisionOCR:
    """Gemini Vision OCR for processing scanned PDFs"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API Key is required for OCR")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini Vision OCR initialized")
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using Gemini Vision"""
        try:
            prompt = """Trích xuất toàn bộ văn bản trong ảnh này (tiếng Việt).

Quy tắc:
- Giữ nguyên định dạng và cấu trúc gốc
- Giữ nguyên xuống dòng và đoạn văn
- Bao gồm tất cả text, kể cả chữ nhỏ
- Nếu text không rõ, cố gắng phiên âm tốt nhất
- Chỉ xuất text, không giải thích gì thêm

Text:"""
            
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
        
        except Exception as e:
            print(f"❌ Gemini Vision OCR error: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str, dpi: int = 200, max_pages: int = None) -> str:
        """Extract text from PDF using Gemini Vision OCR
        
        Args:
            pdf_path: Path to PDF file
            dpi: Image resolution (default: 200)
            max_pages: Max pages to process (None = all pages)
        
        Returns:
            Extracted text from all pages
        """
        print(f"🤖 Gemini Vision OCR: Converting {pdf_path} to images (DPI: {dpi})...")
        
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            total_pages = len(images)
            
            # Limit pages if specified
            if max_pages and max_pages < total_pages:
                images = images[:max_pages]
                print(f"📄 Processing first {max_pages} of {total_pages} pages")
            else:
                print(f"📄 Processing all {total_pages} pages")
        
        except Exception as e:
            print(f"❌ Gemini Vision OCR: Error converting PDF: {e}")
            print("   💡 Make sure poppler-utils is installed:")
            print("      sudo apt-get install poppler-utils")
            raise
        
        full_text = ""
        
        for i, image in enumerate(images, start=1):
            print(f"🤖 Processing page {i}/{len(images)}...")
            
            page_text = self.extract_text_from_image(image)
            
            if page_text:
                full_text += f"\n\n=== TRANG {i} ===\n\n{page_text}"
                print(f"   ✅ Extracted {len(page_text)} characters")
            else:
                print(f"   ⚠️  No text from page {i}")
        
        print(f"✅ Total: {len(full_text)} characters from {len(images)} pages")
        
        return full_text


def init_gemini_vision_ocr(api_key: str) -> GeminiVisionOCR:
    """Initialize Gemini Vision OCR"""
    return GeminiVisionOCR(api_key)

