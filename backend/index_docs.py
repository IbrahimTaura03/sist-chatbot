import os
import uuid
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv("../.env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME       = os.getenv("PINECONE_INDEX_NAME", "sist-chatbot")
DOCS_PATH        = "../data/sist_docs.txt"

print("Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

existing = [i.name for i in pc.list_indexes()]
if INDEX_NAME not in existing:
    print(f"Creating index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print("✅ Index created")
else:
    print(f"✅ Index '{INDEX_NAME}' already exists")

index = pc.Index(INDEX_NAME)

print("\nLoading SIST documents...")
with open(DOCS_PATH, "r", encoding="utf-8") as f:
    raw_text = f.read()

chunks = [c.strip() for c in raw_text.split("---") if c.strip()]
print(f"✅ Created {len(chunks)} text chunks")

print("\nLoading embedding model...")
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Embedding model ready")

print("\nEmbedding and uploading to Pinecone...")
vectors = []
for i, chunk in enumerate(chunks):
    embedding = embed_model.encode(chunk).tolist()
    vectors.append({
        "id":       str(uuid.uuid4()),
        "values":   embedding,
        "metadata": {
            "text":        chunk,
            "source":      "sist_docs.txt",
            "chunk_index": i,
        },
    })

BATCH = 100
for i in range(0, len(vectors), BATCH):
    batch = vectors[i : i + BATCH]
    index.upsert(vectors=batch)
    print(f"  Uploaded batch {i // BATCH + 1}/{(len(vectors) - 1) // BATCH + 1}")

stats = index.describe_index_stats()
print(f"\n✅ Done! Pinecone now has {stats['total_vector_count']} vectors")
