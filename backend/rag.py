import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

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
    query_vector = _embed_model.encode(query).tolist()

    results = _index.query(
        vector=query_vector,
        top_k=k,
        include_metadata=True,
    )

    if not results["matches"]:
        return "No relevant context found in the SIST knowledge base."

    chunks = [match["metadata"]["text"] for match in results["matches"]]
    return "\n\n".join(chunks)


# ── Quick standalone test ────────────────────────────────
if __name__ == "__main__":
    test_q = "What programmes does SIST Tangier offer?"
    print(f"Query: {test_q}\n")
    print("Retrieved context:")
    print(retrieve_context(test_q))