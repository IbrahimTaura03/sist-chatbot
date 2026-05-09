import os
import asyncio
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv(".env")

# ── Initialise once at module load ───────────────────────
_pc          = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
_index       = _pc.Index(os.getenv("PINECONE_INDEX_NAME", "sist-chatbot"))
_embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def _retrieve_sync(query: str, k: int) -> str:
    query_vector = _embed_model.encode(query).tolist()
    results = _index.query(
        vector=query_vector,
        top_k=k,
        include_metadata=True,
    )
    if not results["matches"]:
        return "No relevant context found in the SIST knowledge base."
    chunks = [
        match["metadata"].get("text", "")
        for match in results["matches"]
        if match["metadata"].get("text")
    ]
    if not chunks:
        return "No relevant context found in the SIST knowledge base."
    return "\n\n".join(chunks)

async def retrieve_context(query: str, k: int = 4) -> str:
    return await asyncio.to_thread(_retrieve_sync, query, k)

if __name__ == "__main__":
    async def test():
        q = "What programmes does SIST Tangier offer?"
        print(f"Query: {q}\n")
        ctx = await retrieve_context(q)
        print("Retrieved context:")
        print(ctx)
    asyncio.run(test())