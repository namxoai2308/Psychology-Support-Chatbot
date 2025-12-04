#!/usr/bin/env python3
"""Test improved RAG with user queries"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.services.rag import RAGService

db = SessionLocal()
rag = RAGService()

print("╔═══════════════════════════════════════════════════════════╗")
print("║   🧪 TEST IMPROVED RAG WITH USER QUERIES                 ║")
print("╚═══════════════════════════════════════════════════════════╝\n")

# Test 1: SEL nhận thức bản thân
print("=" * 60)
print("🔍 TEST 1: SEL trong nhận thức bản thân")
print("=" * 60)
results = rag.search_chunks("SEL nhận thức bản thân", db, top_k=5)
print(f"\n✅ Found: {len(results)} chunks\n")
for i, chunk in enumerate(results[:3], 1):
    print(f"📄 Chunk {i} ({len(chunk)} chars):")
    print("-" * 60)
    print(chunk[:400])
    print()

# Test 2: Quy chế thi
print("\n" + "=" * 60)
print("🔍 TEST 2: Quy chế thi của trường")
print("=" * 60)
results = rag.search_chunks("quy chế thi của trường", db, top_k=5)
print(f"\n✅ Found: {len(results)} chunks\n")
for i, chunk in enumerate(results[:3], 1):
    print(f"📄 Chunk {i} ({len(chunk)} chars):")
    print("-" * 60)
    print(chunk[:400])
    print()

# Test 3: More specific query
print("\n" + "=" * 60)
print("🔍 TEST 3: Kỹ năng SEL")
print("=" * 60)
results = rag.search_chunks("kỹ năng SEL là gì", db, top_k=5)
print(f"\n✅ Found: {len(results)} chunks\n")
for i, chunk in enumerate(results[:2], 1):
    print(f"📄 Chunk {i} ({len(chunk)} chars):")
    print("-" * 60)
    print(chunk[:400])
    print()

db.close()
print("\n" + "=" * 60)
print("✅ Test completed!")
print("=" * 60)

