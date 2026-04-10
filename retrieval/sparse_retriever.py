import json
from pathlib import Path
from rank_bm25 import BM25Okapi


# ── Config ────────────────────────────────────────────────
CHUNKS_DIR = Path("data/chunks")


# ── Build BM25 Index ──────────────────────────────────────
def load_corpus(strategy: str = "clause") -> tuple[list[dict], BM25Okapi]:
    """
    Loads all chunks for a given strategy and builds a BM25 index.
    BM25 is great for exact legal terms: 'Section 73', 'force majeure'

    Returns:
        chunks : list of all chunk dicts
        bm25   : fitted BM25 index
    """
    json_files = list(CHUNKS_DIR.rglob("*.json"))

    if not json_files:
        raise FileNotFoundError("No chunked JSON files found. Run chunker.py first.")

    all_chunks = []
    for json_path in json_files:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        chunks = data["chunks"].get(strategy, [])
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError(f"No chunks found for strategy: {strategy}")

    # Tokenize for BM25 — simple whitespace split works well for legal text
    tokenized = [chunk["text"].lower().split() for chunk in all_chunks]
    bm25      = BM25Okapi(tokenized)

    print(f"✅ BM25 index built: {len(all_chunks)} chunks ({strategy} strategy)")
    return all_chunks, bm25


# ── Sparse Retriever ──────────────────────────────────────
def sparse_search(
    query:    str,
    chunks:   list[dict],
    bm25:     BM25Okapi,
    top_k:    int = 10
) -> list[dict]:
    """
    Searches using BM25 keyword matching.
    Best for exact legal terms, section numbers, specific clauses.

    Args:
        query  : the user's question
        chunks : full corpus (from load_corpus)
        bm25   : fitted BM25 index
        top_k  : how many chunks to return
    """
    # Tokenize query
    tokenized_query = query.lower().split()

    # Get BM25 scores for all chunks
    scores = bm25.get_scores(tokenized_query)

    # Get top_k indices
    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:top_k]

    # Format results
    results = []
    for rank, idx in enumerate(top_indices):
        chunk = chunks[idx]
        results.append({
            "chunk_id":  chunk["chunk_id"],
            "text":      chunk["text"],
            "metadata":  chunk.get("metadata", {}),
            "score":     float(scores[idx]),
            "rank":      rank + 1,
            "retriever": "sparse",
        })

    return results


# ── Test ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🔧 Building BM25 index...")
    chunks, bm25 = load_corpus(strategy="clause")

    query   = "Section 73 compensation breach of contract"
    results = sparse_search(query, chunks, bm25, top_k=5)

    print(f"\n🔍 Query: {query}\n")
    print(f"{'─'*60}")
    for i, r in enumerate(results, 1):
        print(f"\n#{i} [BM25: {r['score']:.3f}] {r['metadata'].get('filename','?')} (page {r['metadata'].get('page','?')})")
        print(f"   {r['text'][:200]}...")
    print(f"\n{'─'*60}")