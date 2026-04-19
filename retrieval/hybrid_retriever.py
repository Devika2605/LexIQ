import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval.dense_retriever  import dense_search
from retrieval.sparse_retriever import sparse_search, load_corpus


# ── Reciprocal Rank Fusion ────────────────────────────────
def reciprocal_rank_fusion(
    dense_results:  list[dict],
    sparse_results: list[dict],
    k:              int = 60
) -> list[dict]:
    """
    Combines dense and sparse results using Reciprocal Rank Fusion.

    RRF score = Σ 1 / (k + rank)

    k=60 is the standard value from the original RRF paper.
    Higher k = less penalty for lower ranks.

    Why RRF works:
    - Dense retrieval finds semantically similar chunks
    - Sparse retrieval finds exact keyword matches
    - RRF combines both without needing to normalize scores
    """
    # Map chunk_id → RRF score
    rrf_scores = {}
    # Map chunk_id → chunk data (to reconstruct results)
    chunk_data = {}

    # Score dense results
    for rank, result in enumerate(dense_results, start=1):
        cid = result["chunk_id"]
        rrf_scores[cid]  = rrf_scores.get(cid, 0) + 1 / (k + rank)
        chunk_data[cid]  = result

    # Score sparse results
    for rank, result in enumerate(sparse_results, start=1):
        cid = result["chunk_id"]
        rrf_scores[cid]  = rrf_scores.get(cid, 0) + 1 / (k + rank)
        if cid not in chunk_data:
            chunk_data[cid] = result

    # Sort by RRF score descending
    sorted_ids = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)

    # Build final results
    results = []
    for rank, cid in enumerate(sorted_ids, start=1):
        chunk          = chunk_data[cid].copy()
        chunk["score"] = rrf_scores[cid]
        chunk["rank"]  = rank
        chunk["retriever"] = "hybrid"
        results.append(chunk)

    return results


# ── Hybrid Retriever ──────────────────────────────────────
def hybrid_search(
    query:    str,
    chunks:   list[dict],
    bm25,
    strategy: str = "clause",
    top_k:    int = 5,
    rrf_k:    int = 60
) -> list[dict]:
    # Add query expansion
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from retrieval.query_expander import expand_query

    expanded_query = expand_query(query)

    # Use expanded query for retrieval
    dense_results  = dense_search(expanded_query, strategy=strategy, top_k=10)
    sparse_results = sparse_search(expanded_query, chunks, bm25, top_k=10)

    fused = reciprocal_rank_fusion(dense_results, sparse_results, k=rrf_k)
    return fused[:top_k]


# ── Test ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🔧 Loading BM25 index...")
    chunks, bm25 = load_corpus(strategy="clause")

    queries = [
        "What is the penalty for breach of contract?",
        "How many days notice for employee termination?",
        "What are the GST invoice requirements?",
        "Force majeure clause in vendor agreement",
        "MSME delayed payment interest rate",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"🔍 {query}")
        print(f"{'='*60}")

        results = hybrid_search(query, chunks, bm25, strategy="clause", top_k=3)

        for i, r in enumerate(results, 1):
            print(f"\n  #{i} [RRF: {r['score']:.4f}]")
            print(f"      File : {r['metadata'].get('filename', '?')}")
            print(f"      Page : {r['metadata'].get('page', '?')}")
            print(f"      Cat  : {r['metadata'].get('category', '?')} / {r['metadata'].get('subcategory', '?')}")
            print(f"      Text : {r['text'][:180]}...")