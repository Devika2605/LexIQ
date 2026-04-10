import chromadb
from sentence_transformers import SentenceTransformer


# ── Setup ─────────────────────────────────────────────────
CHROMA_DIR = "chroma_db"

COLLECTIONS = {
    "fixed":     "lexiq_fixed",
    "recursive": "lexiq_recursive",
    "clause":    "lexiq_clause",
}

client = chromadb.PersistentClient(path=CHROMA_DIR)
model  = SentenceTransformer("all-MiniLM-L6-v2")


# ── Dense Retriever ───────────────────────────────────────
def dense_search(query: str, strategy: str = "clause", top_k: int = 10) -> list[dict]:
    """
    Searches ChromaDB using cosine similarity.
    Returns top_k most semantically similar chunks.

    Args:
        query    : the user's question
        strategy : which collection to search (fixed/recursive/clause)
        top_k    : how many chunks to return
    """
    if strategy not in COLLECTIONS:
        raise ValueError(f"Invalid strategy: {strategy}. Choose from {list(COLLECTIONS.keys())}")

    collection = client.get_collection(COLLECTIONS[strategy])

    # Embed the query
    query_embedding = model.encode(query).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Format results
    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "chunk_id":  results["ids"][0][i],
            "text":      results["documents"][0][i],
            "metadata":  results["metadatas"][0][i],
            "score":     1 - results["distances"][0][i],  # convert distance to similarity
            "retriever": "dense",
        })

    return chunks


# ── Test ──────────────────────────────────────────────────
if __name__ == "__main__":
    query   = "What is the penalty for breach of contract?"
    results = dense_search(query, strategy="clause", top_k=5)

    print(f"\n🔍 Query: {query}\n")
    print(f"{'─'*60}")
    for i, r in enumerate(results, 1):
        print(f"\n#{i} [{r['score']:.3f}] {r['metadata']['filename']} (page {r['metadata']['page']})")
        print(f"   {r['text'][:200]}...")
    print(f"\n{'─'*60}")