import json
import re
from pathlib import Path


# ── Config ────────────────────────────────────────────────
PROCESSED_DIR = Path("data/processed")
CHUNKS_DIR    = Path("data/chunks")
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

# Fixed chunking config
FIXED_CHUNK_SIZE    = 512   # characters (not tokens, simpler for now)
FIXED_CHUNK_OVERLAP = 50    # overlap between chunks


# ── Strategy A: Fixed Size ────────────────────────────────
def chunk_fixed(text: str, metadata: dict, page_number: int, global_idx: list) -> list[dict]:
    chunks = []
    start  = 0

    while start < len(text):
        end        = start + FIXED_CHUNK_SIZE
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append({
                "chunk_id": f"{metadata['filename']}_fixed_{global_idx[0]:05d}",
                "text":     chunk_text,
                "strategy": "fixed",
                "page":     page_number,
                "metadata": metadata,
            })
            global_idx[0] += 1

        start = end - FIXED_CHUNK_OVERLAP

    return chunks


# ── Strategy B: Recursive ─────────────────────────────────
def chunk_recursive(text: str, metadata: dict, page_number: int, global_idx: list) -> list[dict]:
    separators  = ["\n\n", "\n", ". ", " "]
    target_size = 512

    def split_text(text: str, separators: list) -> list[str]:
        if not separators:
            return [text[i:i+target_size] for i in range(0, len(text), target_size)]

        sep    = separators[0]
        splits = text.split(sep)
        chunks = []
        current = ""

        for split in splits:
            if len(current) + len(split) + len(sep) <= target_size:
                current += split + sep
            else:
                if current.strip():
                    chunks.append(current.strip())
                if len(split) > target_size:
                    sub_chunks = split_text(split, separators[1:])
                    chunks.extend(sub_chunks)
                    current = ""
                else:
                    current = split + sep

        if current.strip():
            chunks.append(current.strip())

        return chunks

    raw_chunks = split_text(text, separators)
    chunks     = []

    for chunk_text in raw_chunks:
        if chunk_text.strip():
            chunks.append({
                "chunk_id": f"{metadata['filename']}_recursive_{global_idx[0]:05d}",
                "text":     chunk_text.strip(),
                "strategy": "recursive",
                "page":     page_number,
                "metadata": metadata,
            })
            global_idx[0] += 1

    return chunks



# ── Strategy C: Clause Boundary ───────────────────────────
def chunk_clause(text: str, metadata: dict, page_number: int, global_idx: list) -> list[dict]:
    clause_patterns = [
        r'\n(?=Section\s+\d+)',
        r'\n(?=SECTION\s+\d+)',
        r'\n(?=Clause\s+\d+)',
        r'\n(?=CLAUSE\s+\d+)',
        r'\n(?=Article\s+\d+)',
        r'\n(?=ARTICLE\s+\d+)',
        r'\n(?=\d+\.\s+[A-Z])',
        r'\n(?=\(\d+\)\s)',
        r'\n(?=[A-Z]{3,}[\s:]+)',
        r'\n(?=Schedule\s+[IVX\d]+)',
        r'\n(?=SCHEDULE\s+[IVX\d]+)',
        r'\n(?=Whereas)',
        r'\n(?=NOW THEREFORE)',
        r'\n(?=IN WITNESS)',
    ]

    combined_pattern = "|".join(clause_patterns)
    splits           = re.split(combined_pattern, text)
    chunks           = []
    current_chunk    = ""
    MAX_CLAUSE_SIZE  = 1000

    for split in splits:
        split = split.strip()
        if not split:
            continue

        if len(current_chunk) + len(split) <= MAX_CLAUSE_SIZE:
            current_chunk += "\n" + split if current_chunk else split
        else:
            if current_chunk.strip():
                chunks.append({
                    "chunk_id": f"{metadata['filename']}_clause_{global_idx[0]:05d}",
                    "text":     current_chunk.strip(),
                    "strategy": "clause",
                    "page":     page_number,
                    "metadata": metadata,
                })
                global_idx[0] += 1

            if len(split) > MAX_CLAUSE_SIZE:
                sub_chunks = chunk_recursive(split, metadata, page_number, global_idx)
                for sub in sub_chunks:
                    sub["strategy"] = "clause"
                    sub["chunk_id"] = f"{metadata['filename']}_clause_{global_idx[0]:05d}"
                    global_idx[0] += 1
                chunks.extend(sub_chunks)
                current_chunk = ""
            else:
                current_chunk = split

    if current_chunk.strip():
        chunks.append({
            "chunk_id": f"{metadata['filename']}_clause_{global_idx[0]:05d}",
            "text":     current_chunk.strip(),
            "strategy": "clause",
            "page":     page_number,
            "metadata": metadata,
        })
        global_idx[0] += 1

    return chunks

# ── Process One Document ──────────────────────────────────
def chunk_document(json_path: Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        document = json.load(f)

    metadata   = document["metadata"]
    all_chunks = {"fixed": [], "recursive": [], "clause": []}

    # Global counters — one per strategy, passed by reference using list
    counters = {"fixed": [0], "recursive": [0], "clause": [0]}

    for page in document["pages"]:
        text        = page["text"]
        page_number = page["page_number"]

        if not text.strip():
            continue

        all_chunks["fixed"]     += chunk_fixed(text, metadata, page_number, counters["fixed"])
        all_chunks["recursive"] += chunk_recursive(text, metadata, page_number, counters["recursive"])
        all_chunks["clause"]    += chunk_clause(text, metadata, page_number, counters["clause"])

    for table in document.get("tables", []):
        table_text  = table["text"]
        page_number = table["page_number"]
        table_meta  = {**metadata, "content_type": "table"}

        all_chunks["fixed"]     += chunk_fixed(table_text, table_meta, page_number, counters["fixed"])
        all_chunks["recursive"] += chunk_recursive(table_text, table_meta, page_number, counters["recursive"])
        all_chunks["clause"]    += chunk_clause(table_text, table_meta, page_number, counters["clause"])

    return {
        "metadata":     metadata,
        "chunk_counts": {k: len(v) for k, v in all_chunks.items()},
        "chunks":       all_chunks,
    }

# ── Save Chunks ───────────────────────────────────────────
def save_chunks(chunked_doc: dict, json_path: Path):
    """
    Saves chunked document mirroring the processed/ folder structure.
    """
    relative  = json_path.relative_to(PROCESSED_DIR)
    out_path  = CHUNKS_DIR / relative
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chunked_doc, f, ensure_ascii=False, indent=2)


# ── Main Runner ───────────────────────────────────────────
def chunk_all_documents():
    json_files = list(PROCESSED_DIR.rglob("*.json"))

    if not json_files:
        print("❌ No JSON files found in data/processed/")
        print("   Run pdf_parser.py first.")
        return

    print(f"\n📂 Found {len(json_files)} processed documents\n")

    total_fixed     = 0
    total_recursive = 0
    total_clause    = 0

    for json_path in json_files:
        print(f"  Chunking: {json_path.name}")
        try:
            chunked = chunk_document(json_path)
            save_chunks(chunked, json_path)

            counts = chunked["chunk_counts"]
            total_fixed     += counts["fixed"]
            total_recursive += counts["recursive"]
            total_clause    += counts["clause"]

            print(f"  ✅ fixed={counts['fixed']} | recursive={counts['recursive']} | clause={counts['clause']}")

        except Exception as e:
            print(f"  ❌ FAILED: {json_path.name} → {e}")

    print(f"\n{'─'*55}")
    print(f"  Strategy       | Total Chunks")
    print(f"{'─'*55}")
    print(f"  Fixed          | {total_fixed}")
    print(f"  Recursive      | {total_recursive}")
    print(f"  Clause         | {total_clause}")
    print(f"{'─'*55}")
    print(f"\nOutput saved to: {CHUNKS_DIR}/")


if __name__ == "__main__":
    chunk_all_documents()