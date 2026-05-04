import os
=======
import asyncio
>>>>>>> 91f3e15 (save changes before pull)
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

<<<<<<< HEAD
load_dotenv("../.env")

# Initialise once when the module loads
_pc         = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
_index      = _pc.Index(os.getenv("PINECONE_INDEX_NAME", "sist-chatbot"))
_embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def retrieve_context(query: str, k: int = 4) -> str:
    """
    Embed the query, search Pinecone for top-k matching
    chunks, and return them joined as a single string.
    """
=======
load_dotenv(".env")

# ── Initialise once at module load ───────────────────────
_pc          = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
_index       = _pc.Index(os.getenv("PINECONE_INDEX_NAME", "sist-chatbot"))
_embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def _retrieve_sync(query: str, k: int) -> str:
    """Blocking retrieval — runs in a thread pool (see retrieve_context below)."""
>>>>>>> 91f3e15 (save changes before pull)
    query_vector = _embed_model.encode(query).tolist()

    results = _index.query(
        vector=query_vector,
        top_k=k,
        include_metadata=True,
    )

    if not results["matches"]:
        return "No relevant context found in the SIST knowledge base."

<<<<<<< HEAD
    chunks = [match["metadata"]["text"] for match in results["matches"]]
    return "\n\n".join(chunks)


# ── Quick standalone test ────────────────────────────────
if __name__ == "__main__":
    test_q = "What programmes does SIST Tangier offer?"
    print(f"Query: {test_q}\n")
    print("Retrieved context:")
    print(retrieve_context(test_q))
=======
    chunks = [
        match["metadata"].get("text", "")
        for match in results["matches"]
        if match["metadata"].get("text")
    ]

    if not chunks:
        return "No relevant context found in the SIST knowledge base."

    return "\n\n".join(chunks)


# ── Fix: wrap sync call so it doesn't block the async event loop ──
async def retrieve_context(query: str, k: int = 4) -> str:
    return await asyncio.to_thread(_retrieve_sync, query, k)


# ── Quick standalone test ────────────────────────────────
if __name__ == "__main__":
    import asyncio

    async def test():
        q = "What programmes does SIST Tangier offer?"
        print(f"Query: {q}\n")
        ctx = await retrieve_context(q)
        print("Retrieved context:")
        print(ctx)

    asyncio.run(test())
>>>>>>> 91f3e15 (save changes before pull)
