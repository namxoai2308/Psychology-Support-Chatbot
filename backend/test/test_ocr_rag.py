#!/usr/bin/env python3
"""
Test DeepSeek OCR + RAG System
Kiểm tra khả năng scan PDF và RAG search
"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import SessionLocal, engine, Base
from app.services.rag import RAGService
from app.models.models import SchoolDocument, DocumentChunk

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def test_pypdf2(pdf_path: str):
    """Test with PyPDF2 (default)"""
    print_header("🔍 TEST 1: PyPDF2 (Fast, for text PDFs)")
    
    rag = RAGService(use_deepseek_ocr=False)
    
    try:
        text = rag.extract_text_from_pdf(pdf_path)
        
        print(f"✅ Extracted: {len(text)} characters")
        print(f"📄 Preview (first 500 chars):")
        print("-" * 60)
        print(text[:500])
        print("-" * 60)
        
        return text, True
    except Exception as e:
        print(f"❌ Error: {e}")
        return "", False


def test_deepseek_ocr(pdf_path: str):
    """Test with DeepSeek Vision OCR"""
    print_header("🤖 TEST 2: DeepSeek Vision OCR (For scanned PDFs)")
    
    if not settings.DEEPSEEK_API_KEY:
        print("❌ DEEPSEEK_API_KEY not found in .env")
        print("   Please add: DEEPSEEK_API_KEY=sk-xxxxx")
        return "", False
    
    print(f"✅ Using API key: {settings.DEEPSEEK_API_KEY[:10]}...")
    
    rag = RAGService(
        use_deepseek_ocr=True,
        deepseek_api_key=settings.DEEPSEEK_API_KEY
    )
    
    try:
        text = rag.extract_text_from_pdf(pdf_path)
        
        print(f"✅ Extracted: {len(text)} characters")
        print(f"📄 Preview (first 500 chars):")
        print("-" * 60)
        print(text[:500])
        print("-" * 60)
        
        return text, True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return "", False


def test_chunking(text: str):
    """Test text chunking"""
    print_header("✂️ TEST 3: Text Chunking")
    
    rag = RAGService()
    chunks = rag.text_splitter.split_text(text)
    
    print(f"✅ Created: {len(chunks)} chunks")
    print(f"📊 Chunk size: {settings.CHUNK_SIZE} chars")
    print(f"📊 Overlap: {settings.CHUNK_OVERLAP} chars")
    
    # Show first 3 chunks
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n📄 Chunk {i} ({len(chunk)} chars):")
        print("-" * 60)
        print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
    
    return chunks


def test_rag_search(db, query: str):
    """Test RAG search"""
    print_header("🔍 TEST 4: RAG Search")
    
    rag = RAGService()
    
    print(f"Query: \"{query}\"")
    print()
    
    results = rag.search_chunks(query, db, top_k=3)
    
    if results:
        print(f"✅ Found {len(results)} relevant chunks:\n")
        for i, chunk in enumerate(results, 1):
            print(f"📄 Result {i}:")
            print("-" * 60)
            print(chunk[:300] + "..." if len(chunk) > 300 else chunk)
            print()
    else:
        print("❌ No relevant chunks found")
    
    return results


def save_to_database(pdf_path: str, use_ocr: bool = False):
    """Save PDF to database"""
    print_header("💾 TEST 5: Save to Database")
    
    db = SessionLocal()
    
    try:
        rag = RAGService(
            use_deepseek_ocr=use_ocr,
            deepseek_api_key=settings.DEEPSEEK_API_KEY if use_ocr else None
        )
        
        filename = os.path.basename(pdf_path)
        doc = rag.process_and_save_pdf(pdf_path, filename, db)
        
        print(f"✅ Document saved!")
        print(f"   ID: {doc.id}")
        print(f"   Filename: {doc.filename}")
        print(f"   Chunks: {len(doc.chunks)}")
        
        return doc, True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, False
    finally:
        db.close()


def compare_methods(pdf_path: str):
    """Compare PyPDF2 vs DeepSeek OCR"""
    print_header("⚖️ COMPARISON: PyPDF2 vs DeepSeek OCR")
    
    # Test PyPDF2
    text1, success1 = test_pypdf2(pdf_path)
    
    # Test DeepSeek OCR
    text2, success2 = test_deepseek_ocr(pdf_path)
    
    # Compare
    print_header("📊 Comparison Results")
    
    print(f"PyPDF2:")
    print(f"  ✅ Success: {success1}")
    print(f"  📏 Length: {len(text1)} chars")
    print(f"  💰 Cost: FREE")
    print(f"  ⚡ Speed: FAST")
    
    print(f"\nDeepSeek OCR:")
    print(f"  ✅ Success: {success2}")
    print(f"  📏 Length: {len(text2)} chars")
    print(f"  💰 Cost: ~$0.0001/page")
    print(f"  ⚡ Speed: SLOW")
    
    if success1 and len(text1) > 100:
        print(f"\n✅ RECOMMENDATION: Use PyPDF2 (this is a text PDF)")
    elif success2:
        print(f"\n✅ RECOMMENDATION: Use DeepSeek OCR (this is a scanned PDF)")
    else:
        print(f"\n❌ Both methods failed!")


def main():
    """Main test function"""
    print("""
╔══════════════════════════════════════════════════════════╗
║   🔬 DeepSeek OCR + RAG Test Suite                      ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Check for PDF file
    if len(sys.argv) < 2:
        print("❌ Usage: python test_ocr_rag.py <path_to_pdf>")
        print()
        print("📝 Example:")
        print("   python test_ocr_rag.py uploads/document.pdf")
        print()
        print("💡 Tips:")
        print("   - For text PDF: PyPDF2 works great")
        print("   - For scanned PDF: Use DeepSeek OCR")
        print("   - Set USE_DEEPSEEK_OCR=true in .env to enable OCR")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"📁 Testing PDF: {pdf_path}")
    print(f"📊 File size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
    print()
    
    # Run tests
    choice = input("Choose test:\n"
                   "1. Quick test (PyPDF2 only)\n"
                   "2. Full test (PyPDF2 + DeepSeek OCR)\n"
                   "3. Save to DB and test RAG search\n"
                   "4. Compare both methods\n"
                   "Choice [1-4]: ").strip()
    
    if choice == "1":
        text, success = test_pypdf2(pdf_path)
        if success:
            test_chunking(text)
    
    elif choice == "2":
        text1, _ = test_pypdf2(pdf_path)
        text2, _ = test_deepseek_ocr(pdf_path)
        
        if text1:
            test_chunking(text1)
    
    elif choice == "3":
        use_ocr = input("\nUse DeepSeek OCR? [y/N]: ").strip().lower() == 'y'
        
        doc, success = save_to_database(pdf_path, use_ocr=use_ocr)
        
        if success:
            # Test RAG search
            db = SessionLocal()
            try:
                print()
                query = input("Enter search query (Vietnamese): ").strip()
                if query:
                    test_rag_search(db, query)
            finally:
                db.close()
    
    elif choice == "4":
        compare_methods(pdf_path)
    
    else:
        print("❌ Invalid choice")
    
    print()
    print("=" * 60)
    print("✅ Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

