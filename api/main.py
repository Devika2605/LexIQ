import sys
import os
import uuid
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from ingestion.pdf_parser  import parse_pdf
from ingestion.chunker     import chunk_document
from ingestion.embedder    import embed_and_store, get_collections, model
from retrieval.hybrid_retriever import hybrid_search
from retrieval.sparse_retriever import load_corpus
from retrieval.dense_retriever  import dense_search
from generation.generator  import query_lexiq, query_no_rag
from generation.risk_scorer import score_chunk_risk, get_risk_emoji

import chromadb

load_dotenv()

# ── App Setup ─────────────────────────────────────────────
app = FastAPI(
    title       = "LexIQ API",
    description = "Legal Contract Intelligence for Indian SMBs",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Global State ──────────────────────────────────────────
CHROMA_DIR   = "chroma_db"
UPLOAD_DIR   = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

# Pre-load BM25 corpus on startup
print("\n🔧 Loading BM25 corpus...")
CORPUS_CHUNKS, CORPUS_BM25 = load_corpus(strategy="clause")
print("✅ BM25 corpus loaded\n")

# Track active user sessions
# session_id → collection_name
active_sessions: dict[str, str] = {}


# ── Request/Response Models ───────────────────────────────
class QueryRequest(BaseModel):
    question:   str
    session_id: str  = None  # if provided, also searches uploaded contract
    strategy:   str  = "clause"
    top_k:      int  = 5

class QueryResponse(BaseModel):
    question:   str
    answer:     str
    sources:    list[dict]
    risk_level: str
    risk_emoji: str
    no_rag_answer: str = None


class ScanRequest(BaseModel):
    session_id: str


# ── Health Check ──────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status":  "running",
        "product": "LexIQ",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# ── Query Endpoint ────────────────────────────────────────
@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """
    Main RAG query endpoint.
    If session_id provided, searches both corpus AND uploaded contract.
    """
    try:
        # Check if user has an uploaded contract
        user_collection = None
        if req.session_id and req.session_id in active_sessions:
            col_name = active_sessions[req.session_id]
            try:
                user_collection = chroma_client.get_collection(col_name)
            except Exception:
                pass

        # If user has uploaded a contract, search it too
        extra_chunks = []
        if user_collection:
            query_embedding = model.encode(req.question).tolist()
            user_results    = user_collection.query(
                query_embeddings = [query_embedding],
                n_results        = 5,
                include          = ["documents", "metadatas", "distances"]
            )
            for i in range(len(user_results["ids"][0])):
                extra_chunks.append({
                    "chunk_id": user_results["ids"][0][i],
                    "text":     user_results["documents"][0][i],
                    "metadata": {
                        **user_results["metadatas"][0][i],
                        "source": "uploaded_contract",
                    },
                    "score":    1 - user_results["distances"][0][i],
                    "retriever": "dense",
                    "risk_level": score_chunk_risk(user_results["documents"][0][i]),
                    "risk_emoji": get_risk_emoji(score_chunk_risk(user_results["documents"][0][i])),
                })

        # Run main RAG pipeline
        result = query_lexiq(
            question = req.question,
            strategy = req.strategy,
            top_k    = req.top_k,
            chunks   = CORPUS_CHUNKS,
            bm25     = CORPUS_BM25,
        )

        # Merge user contract chunks with corpus chunks
        if extra_chunks:
            all_chunks = extra_chunks + result["chunks"]
            # Re-sort by score
            all_chunks.sort(key=lambda x: x["score"], reverse=True)
            result["chunks"]  = all_chunks[:req.top_k]
            result["sources"] = []
            seen = set()
            for chunk in result["chunks"]:
                key = f"{chunk['metadata'].get('filename', 'upload')}_{chunk['metadata'].get('page', '?')}"
                if key not in seen:
                    result["sources"].append({
                        "filename":   chunk["metadata"].get("filename", "uploaded_contract"),
                        "page":       chunk["metadata"].get("page", "?"),
                        "category":   chunk["metadata"].get("source", chunk["metadata"].get("category", "?")),
                        "risk_level": chunk.get("risk_level", "LOW"),
                        "risk_emoji": chunk.get("risk_emoji", "🟢"),
                    })
                    seen.add(key)

        # Get no-RAG baseline for comparison
        no_rag = query_no_rag(req.question)

        return QueryResponse(
            question      = result["question"],
            answer        = result["answer"],
            sources       = result["sources"],
            risk_level    = result["risk_level"],
            risk_emoji    = result["risk_emoji"],
            no_rag_answer = no_rag,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Upload Contract Endpoint ──────────────────────────────
@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """
    Uploads a user contract PDF.
    Parses, chunks, embeds into a temporary session collection.
    Returns session_id for subsequent queries.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Generate unique session
    session_id   = str(uuid.uuid4())[:8]
    col_name     = f"session_{session_id}"

    # Save uploaded file
    upload_path  = UPLOAD_DIR / f"{session_id}_{file.filename}"
    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        # Parse PDF
        print(f"\n📄 Processing upload: {file.filename}")
        document = parse_pdf(upload_path)

        if document is None:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. It may be a scanned image."
            )

        # Chunk with clause strategy
        from ingestion.chunker import chunk_document as chunk_doc
        import json
        import tempfile

        # Save as temp JSON for chunker
        tmp_json = UPLOAD_DIR / f"{session_id}_parsed.json"
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(document, f)

        chunked   = chunk_doc(tmp_json)
        chunks    = chunked["chunks"]["clause"]

        if not chunks:
            raise HTTPException(status_code=400, detail="No text chunks extracted from PDF.")

        # Create session collection in ChromaDB
        collection = chroma_client.get_or_create_collection(
            name     = col_name,
            metadata = {"hnsw:space": "cosine"}
        )

        # Embed and store chunks
        embed_and_store(chunks, collection, strategy="clause")

        # Register session
        active_sessions[session_id] = col_name

        # Cleanup temp files
        tmp_json.unlink(missing_ok=True)

        print(f"✅ Upload processed: {len(chunks)} chunks stored in {col_name}")

        return {
            "session_id":  session_id,
            "filename":    file.filename,
            "chunks":      len(chunks),
            "pages":       document["total_pages"],
            "message":     "Contract uploaded successfully. Use session_id in your queries.",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# ── Clause Risk Scanner Endpoint ──────────────────────────
@app.post("/scan")
def scan_contract(req: ScanRequest):
    """
    Scans ALL clauses in an uploaded contract for risk.
    Returns a full risk report with HIGH/MEDIUM/LOW classification per clause.
    """
    if req.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a contract first.")

    col_name   = active_sessions[req.session_id]

    try:
        collection = chroma_client.get_collection(col_name)
    except Exception:
        raise HTTPException(status_code=404, detail="Session collection not found.")

    # Get all chunks from user's contract
    all_data = collection.get(include=["documents", "metadatas"])

    if not all_data["documents"]:
        raise HTTPException(status_code=400, detail="No content found in uploaded contract.")

    # Score each clause
    high_risk   = []
    medium_risk = []
    low_risk    = []

    for i, text in enumerate(all_data["documents"]):
        risk_level = score_chunk_risk(text)
        emoji      = get_risk_emoji(risk_level)
        meta       = all_data["metadatas"][i] if all_data["metadatas"] else {}

        clause_info = {
            "clause_number": i + 1,
            "page":          meta.get("page", "?"),
            "text":          text[:300] + "..." if len(text) > 300 else text,
            "full_text":     text,
            "risk_level":    risk_level,
            "risk_emoji":    emoji,
        }

        if risk_level == "HIGH":
            high_risk.append(clause_info)
        elif risk_level == "MEDIUM":
            medium_risk.append(clause_info)
        else:
            low_risk.append(clause_info)

    # Overall risk
    if high_risk:
        overall_risk  = "HIGH"
        overall_emoji = "🔴"
    elif medium_risk:
        overall_risk  = "MEDIUM"
        overall_emoji = "🟡"
    else:
        overall_risk  = "LOW"
        overall_emoji = "🟢"

    return {
        "session_id":    req.session_id,
        "overall_risk":  overall_risk,
        "overall_emoji": overall_emoji,
        "summary": {
            "total_clauses":  len(all_data["documents"]),
            "high_risk":      len(high_risk),
            "medium_risk":    len(medium_risk),
            "low_risk":       len(low_risk),
        },
        "high_risk_clauses":   high_risk,
        "medium_risk_clauses": medium_risk,
        "low_risk_clauses":    low_risk,
    }


# ── Clear Session Endpoint ────────────────────────────────
@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    """
    Clears a user session and deletes the temporary ChromaDB collection.
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    col_name = active_sessions[session_id]

    try:
        chroma_client.delete_collection(col_name)
    except Exception:
        pass

    del active_sessions[session_id]

    return {"message": f"Session {session_id} cleared successfully."}


# ── Eval Results Endpoint ─────────────────────────────────
@app.get("/results")
def get_results():
    """
    Returns the experiment comparison results.
    """
    results_file = Path("evaluation/results/experiments_progress.json")

    if not results_file.exists():
        raise HTTPException(status_code=404, detail="No evaluation results found.")

    import json
    with open(results_file) as f:
        results = json.load(f)

    return {"experiments": results}


# ── Run ───────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)