#!/bin/bash
# Quick test for OCR + RAG

echo "🔬 Quick Test: PyPDF2 vs DeepSeek OCR"
echo "======================================"
echo ""

PDF="uploads/20241224_QuyCheThi_Final.pdf"

if [ ! -f "$PDF" ]; then
    echo "❌ PDF not found: $PDF"
    exit 1
fi

source venv/bin/activate

echo "Testing: $PDF"
echo ""

# Quick PyPDF2 test
python3 << END
import sys
sys.path.insert(0, '.')
from app.services.rag import RAGService

rag = RAGService(use_deepseek_ocr=False)
text = rag.extract_text_from_pdf("$PDF")

print("📊 PyPDF2 Results:")
print(f"  Characters: {len(text)}")
print(f"  Words: ~{len(text.split())}")
print(f"  Preview: {text[:200]}...")
print("")

if len(text) < 100:
    print("⚠️  PyPDF2 extracted very little text")
    print("   This might be a scanned PDF")
    print("   → Recommend: Enable DeepSeek OCR")
else:
    print("✅ PyPDF2 works well")
    print("   This is a text PDF")
    print("   → Recommend: Use PyPDF2 (fast & free)")
END

echo ""
echo "🎯 To test RAG search:"
echo "   python test_ocr_rag.py '$PDF'"
echo "   → Choose: 3 (Save to DB + RAG search)"

