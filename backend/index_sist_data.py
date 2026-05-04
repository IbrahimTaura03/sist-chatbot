"""
index_sist_data.py — chunk sist_info.txt and upload to Pinecone
Run AFTER scraper.py + clean_data.py:
    python index_sist_data.py
"""

import os
import uuid
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv(".env")

PINECONE_API_KEY  = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX    = os.getenv("PINECONE_INDEX_NAME", "sist-chatbot")
EMBEDDING_DIM     = 384
BATCH_SIZE        = 50
CHUNK_SIZE        = 400   # words per chunk
CHUNK_OVERLAP     = 50    # words overlap between chunks
DATA_FILE         = "data/sist_info.txt"


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end   = start + size
        chunk = " ".join(words[start:end]).strip()
        if len(chunk) > 80:
            chunks.append(chunk)
        start += size - overlap
    return chunks


def main():
    # ── Load scraped data ────────────────────────────────────────────────────
    if not os.path.exists(DATA_FILE):
        print(f"❌  {DATA_FILE} not found. Run scraper.py first.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = f.read()

    print(f"📄 Loaded {DATA_FILE}  ({len(raw):,} characters)")

    chunks = chunk_text(raw)
    print(f"✂️  Split into {len(chunks)} chunks  (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})\n")

    # ── Connect to Pinecone ──────────────────────────────────────────────────
    pc = Pinecone(api_key=PINECONE_API_KEY)

    existing = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX not in existing:
        print(f"📦 Creating index '{PINECONE_INDEX}'...")
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print("   Done.\n")
    else:
        print(f"✅ Index '{PINECONE_INDEX}' already exists.\n")

    index = pc.Index(PINECONE_INDEX)

    # ── Load embedding model ─────────────────────────────────────────────────
    print("🧠 Loading embedding model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("   Ready.\n")

    # ── Embed + upsert ───────────────────────────────────────────────────────
    print("📤 Uploading to Pinecone...")
    vectors = []
    for chunk in chunks:
        embedding = model.encode(chunk).tolist()
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {"text": chunk},
        })

    for start in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[start: start + BATCH_SIZE]
        index.upsert(vectors=batch)
        end = min(start + BATCH_SIZE, len(vectors))
        print(f"   Batch {start // BATCH_SIZE + 1}: uploaded vectors {start+1}–{end}")

    print(f"\n✅ Done! {len(vectors)} chunks indexed into '{PINECONE_INDEX}'.")
    print("\n📊 Index stats:")
    print(index.describe_index_stats())


if __name__ == "__main__":
    main()