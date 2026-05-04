import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv("../.env")

pc          = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index       = pc.Index(os.getenv("PINECONE_INDEX_NAME", "sist-chatbot"))
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def retrieve_context(query: str, k: int = 4) -> str:
    query_vector = embed_model.encode(query).tolist()
    results = index.query(vector=query_vector, top_k=k, include_metadata=True)
    if not results["matches"]:
        return "No relevant context found."
    chunks = [match["metadata"]["text"] for match in results["matches"]]
    return "\n\n".join(chunks)

test_questions = [
    "What programmes does SIST Tangier offer?",
    "What are the admission requirements for the bachelor?",
    "Does SIST offer scholarships?",
    "Where is the Tangier campus located?",
    "Can I transfer to a UK university?",
    "What is the Foundation Year?",
    "When is the next intake?",
    "What is the language of instruction?",
    "What degrees do SIST students receive?",
    "How do I apply to SIST?",
]

print("="*60)
print("RAG RETRIEVAL EVALUATION")
print("="*60)
for i, q in enumerate(test_questions, 1):
    ctx = retrieve_context(q)
    print(f"\nQ{i}: {q}")
    print(f"Context snippet:\n{ctx[:250]}...")
    print("-"*40)
