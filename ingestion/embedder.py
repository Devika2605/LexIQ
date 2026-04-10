import json
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# ── Config ────────────────────────────────────────────────
CHUNKS_DIR  = Path("data/chunks")
CHROMA_DIR  = "chroma_db"

# 3 collections — one per chunking strategy
COLLECTIONS = {
    "fixed":     "lexiq_fixed",
    "recursive": "lexiq_recursive",
    "clause":    "lexiq_clause",
}

# Batch size for embedding — keep low if you have limited RAM
BATCH_SIZE = 32


# ── Setup ─────────────────────────────────────────────────
print("\n🔧 Loading embedding model (first time may take a minute)...")
model  = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_DIR)
print("✅ Model loaded\n")


# ── Get or Create Collections ─────────────────────────────
def get_collections() -> dict:
    """
    Gets existing ChromaDB collections or creates them fresh.
    """
    collections = {}
    for strategy, name in COLLECTIONS.items():
        collection = client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}  # cosine similarity
        )
        collections[strategy] = collection
        print(f"  📦 Collection: {name} ({collection.count()} existing chunks)")
    return collections


# ── Embed and Store ───────────────────────────────────────
def embed_and_store(chunks: list[dict], collection, strategy: str):
    """
    Embeds a list of chunks and upserts them into ChromaDB.
    Uses batching to avoid memory issues with large corpora.
    """
    if not chunks:
        return

    # Process in batches
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]

        texts    = [c["text"] for c in batch]
        ids      = [c["chunk_id"] for c in batch]

        # Build metadata for each chunk
        metadatas = []
        for c in batch:
            meta = c.get("metadata", {})
            metadatas.append({
                "category":    str(meta.get("category",    "unknown")),
                "subcategory": str(meta.get("subcategory", "unknown")),
                "doc_type":    str(meta.get("doc_type",    "unknown")),
                "filename":    str(meta.get("filename",    "unknown")),
                "filepath":    str(meta.get("filepath",    "unknown")),
                "page":        str(c.get("page", 0)),
                "strategy":    strategy,
            })

        # Generate embeddings
        embeddings = model.encode(
            texts,
            show_progress_bar=False,
        ).tolist()

        # Upsert into ChromaDB
        # Upsert = insert if new, update if exists
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )


# ── Process One Document ──────────────────────────────────
def process_document(json_path: Path, collections: dict) -> dict:
    """
    Loads one chunked JSON and embeds all 3 strategies.
    Returns chunk counts per strategy.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    counts = {}
    for strategy, collection in collections.items():
        chunks = data["chunks"].get(strategy, [])
        embed_and_store(chunks, collection, strategy)
        counts[strategy] = len(chunks)

    return counts


# ── Main Runner ───────────────────────────────────────────
def embed_all():
    json_files = list(CHUNKS_DIR.rglob("*.json"))

    if not json_files:
        print("❌ No chunked JSON files found in data/chunks/")
        print("   Run chunker.py first.")
        return

    print(f"📂 Found {len(json_files)} chunked documents\n")

    # Setup collections
    print("📦 Setting up ChromaDB collections...")
    collections = get_collections()
    print()

    # Track totals
    totals = {"fixed": 0, "recursive": 0, "clause": 0}

    # Process each document
    for json_path in tqdm(json_files, desc="Embedding documents"):
        try:
            counts = process_document(json_path, collections)
            for strategy, count in counts.items():
                totals[strategy] += count
        except Exception as e:
            print(f"\n  ❌ FAILED: {json_path.name} → {e}")

    # Final summary
    print(f"\n{'─'*55}")
    print(f"  Strategy       | Chunks Embedded | Collection")
    print(f"{'─'*55}")
    for strategy, name in COLLECTIONS.items():
        col   = collections[strategy]
        count = col.count()
        print(f"  {strategy:<14} | {totals[strategy]:<15} | {name} ({count} total)")
    print(f"{'─'*55}")
    print(f"\n✅ ChromaDB saved to: {CHROMA_DIR}/")
    print(f"   You can now run retrieval queries against your corpus.")


if __name__ == "__main__":
    embed_all()