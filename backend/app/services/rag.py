"""
RAG Service - Improved keyword-based RAG without embeddings
Uses Gemini Vision OCR for scanned PDFs (optional)
"""
import PyPDF2
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from app.models.models import SchoolDocument, DocumentChunk
import re
import unicodedata
from collections import Counter
from app.core.config import settings


# Extended Vietnamese stopwords list
VIETNAMESE_STOPWORDS = {
    'là', 'của', 'và', 'có', 'được', 'trong', 'không', 'một', 'với', 'để', 'các', 
    'này', 'cho', 'đã', 'từ', 'như', 'về', 'hoặc', 'khi', 'những', 'hay', 'cũng', 
    'vào', 'thì', 'sẽ', 'bị', 'do', 'nếu', 'nào', 'mà', 'theo', 'tại', 'đến', 'ra', 
    'trên', 'gì', 'ai', 'bởi', 'nhưng', 'cả', 'lại', 'rất', 'quá', 'hơn', 'kém', 
    'chỉ', 'còn', 'đều', 'vẫn', 'thường', 'luôn', 'chưa', 'đang', 'sắp', 'vừa', 
    'mới', 'sau', 'trước', 'đâu', 'đây', 'kia', 'đó', 'ấy', 'vậy', 'thế', 'sao', 
    'bao', 'nhiêu', 'mấy', 'từng', 'mỗi', 'mọi', 'khác', 'riêng', 'chung', 'toàn', 
    'chính', 'tự', 'lấy', 'làm', 'nên', 'phải', 'cần', 'muốn'
}


class RAGService:
    """Simple RAG using keyword matching - no embedding API needed"""
    
    def __init__(self, use_vision_ocr: bool = False, gemini_api_key: str = None):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
        )
        
        # Gemini Vision OCR support (optional)
        self.use_vision_ocr = use_vision_ocr
        self.vision_ocr = None
        
        if use_vision_ocr and gemini_api_key:
            try:
                from app.utils.ocr import init_gemini_vision_ocr
                self.vision_ocr = init_gemini_vision_ocr(gemini_api_key)
                print("✅ Gemini Vision OCR enabled")
            except Exception as e:
                print(f"⚠️ Cannot initialize Gemini Vision OCR: {e}")
                self.use_vision_ocr = False
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2 or Gemini Vision OCR"""
        if self.use_vision_ocr and self.vision_ocr:
            try:
                text = self.vision_ocr.extract_text_from_pdf(pdf_path)
                if text and len(text.strip()) > 100:
                    return text
            except Exception as e:
                print(f"❌ Gemini Vision OCR failed: {e}")
                print("   Falling back to PyPDF2...")
        
        # Fallback to PyPDF2
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        
        return text
    
    def normalize_vietnamese(self, text: str) -> str:
        """
        Normalize Vietnamese text by removing diacritics
        This helps match words regardless of accent marks
        """
        # Decompose Unicode characters (NFD normalization)
        text = unicodedata.normalize('NFD', text)
        # Remove combining characters (diacritics)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        return text.lower()
    
    def get_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from Vietnamese text
        
        Improvements:
        - Vietnamese normalization (bỏ dấu)
        - Extended stopwords list
        - Minimum word length filtering
        """
        # Normalize text (lowercase + remove punctuation)
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter: remove stopwords and short words
        keywords = [
            word for word in words 
            if word not in VIETNAMESE_STOPWORDS and len(word) > 2
        ]
        
        return keywords
    
    def get_normalized_keywords(self, text: str) -> List[str]:
        """Get keywords with Vietnamese normalization (no diacritics)"""
        normalized = self.normalize_vietnamese(text)
        return self.get_keywords(normalized)
    
    def calculate_jaccard_similarity(self, set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets"""
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def search_chunks(
        self, 
        query: str, 
        db: Session, 
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[str]:
        """
        Search for relevant chunks using improved keyword matching
        
        Improvements:
        - Vietnamese normalization (bỏ dấu) for better matching
        - Multi-factor scoring (Jaccard + frequency + position + phrase matching)
        - Both normalized and original text matching
        - Lower threshold for more results
        """
        if top_k is None:
            top_k = settings.TOP_K_CHUNKS
        if similarity_threshold is None:
            similarity_threshold = settings.SIMILARITY_THRESHOLD
        
        # Extract query keywords (both original and normalized)
        query_keywords = self.get_keywords(query)
        query_keyword_set = set(query_keywords)
        query_normalized_keywords = self.get_normalized_keywords(query)
        query_normalized_set = set(query_normalized_keywords)
        
        if not query_keywords:
            print("⚠️ No meaningful keywords in query")
            return []
        
        print(f"🔍 Query keywords: {query_keywords[:10]}...")
        
        # Get all chunks
        all_chunks = db.query(DocumentChunk).all()
        
        if not all_chunks:
            print("⚠️ No documents in database")
            return []
        
        # Score each chunk
        scored_chunks = []
        
        for chunk in all_chunks:
            chunk_text = chunk.chunk_text.lower()
            
            # Extract keywords (both original and normalized)
            chunk_keywords = self.get_keywords(chunk.chunk_text)
            chunk_keyword_set = set(chunk_keywords)
            chunk_normalized_keywords = self.get_normalized_keywords(chunk.chunk_text)
            chunk_normalized_set = set(chunk_normalized_keywords)
            
            # Factor 1: Jaccard Similarity (with normalization)
            # Calculate similarity on both original and normalized
            jaccard_score_original = self.calculate_jaccard_similarity(
                query_keyword_set, 
                chunk_keyword_set
            )
            jaccard_score_normalized = self.calculate_jaccard_similarity(
                query_normalized_set,
                chunk_normalized_set
            )
            # Take the maximum of both
            jaccard_score = max(jaccard_score_original, jaccard_score_normalized)
            
            # Factor 2: Keyword Frequency Bonus (check both normalized and original)
            keyword_counts = Counter(chunk_keywords)
            normalized_counts = Counter(chunk_normalized_keywords)
            frequency_score = 0
            for kw in query_keywords:
                frequency_score += keyword_counts.get(kw, 0)
            for kw in query_normalized_keywords:
                frequency_score += normalized_counts.get(kw, 0) * 0.8  # Slightly lower weight
            frequency_score = frequency_score / (len(chunk_keywords) + 1)
            
            # Factor 3: Position Bonus (keywords early in text are more important)
            position_score = 0
            first_half = chunk_text[:len(chunk_text)//2]
            chunk_normalized_text = self.normalize_vietnamese(chunk.chunk_text)
            for keyword in query_keywords:
                if keyword in first_half:
                    position_score += 0.15
            for keyword in query_normalized_keywords:
                if keyword in chunk_normalized_text[:len(chunk_normalized_text)//2]:
                    position_score += 0.1
            
            # Factor 4: Exact Phrase Matching (both original and normalized)
            phrase_score = 0
            query_lower = query.lower()
            query_normalized = self.normalize_vietnamese(query)
            if query_lower in chunk_text:
                phrase_score = 0.4
            elif query_normalized in chunk_normalized_text:
                phrase_score = 0.3
            
            # Combined score with adjusted weights
            total_score = (
                jaccard_score * 0.35 + 
                frequency_score * 0.25 + 
                position_score * 0.15 + 
                phrase_score * 0.25
            )
            
            scored_chunks.append((total_score, chunk.chunk_text))
        
        # Sort by score and filter by threshold
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        
        # Filter and get top K
        top_chunks = [
            content for score, content in scored_chunks 
            if score >= similarity_threshold
        ][:top_k]
        
        if top_chunks:
            top_scores = [score for score, _ in scored_chunks[:len(top_chunks)]]
            print(f"✅ Found {len(top_chunks)} chunks (scores: {[f'{s:.3f}' for s in top_scores]})")
        else:
            print(f"⚠️ No chunks above threshold {similarity_threshold}")
        
        return top_chunks
    
    def process_and_save_pdf(
        self, 
        pdf_path: str, 
        filename: str, 
        db: Session
    ) -> SchoolDocument:
        """Process PDF and save chunks to database"""
        print(f"📄 Processing: {filename}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text or len(text.strip()) < 50:
            raise ValueError(f"Could not extract meaningful text from {filename}")
        
        print(f"✅ Extracted {len(text)} characters")
        
        # Create document record
        doc = SchoolDocument(filename=filename)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Split into chunks
        chunks = self.text_splitter.split_text(text)
        print(f"✂️  Split into {len(chunks)} chunks")
        
        # Save chunks
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_text=chunk_text,
                chunk_index=i
            )
            db.add(chunk)
        
        db.commit()
        print(f"💾 Saved {len(chunks)} chunks to database")
        
        return doc


# Global instance - no OCR by default (enable in routes if needed)
rag_service = RAGService(
    use_vision_ocr=False,  # Can enable with settings.USE_VISION_OCR
    gemini_api_key=settings.GEMINI_API_KEY
)

