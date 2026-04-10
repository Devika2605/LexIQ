import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from groq import Groq

from generation.prompt_templates import (
    SYSTEM_PROMPT,
    build_query_prompt,
    NO_CONTEXT_PROMPT,
)
from generation.risk_scorer import (
    score_retrieved_chunks,
    score_answer_risk,
    get_risk_emoji,
)
from retrieval.hybrid_retriever import hybrid_search
from retrieval.sparse_retriever import load_corpus

load_dotenv()


# ── Setup Groq ────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.1-8b-instant"  # free, fast, good quality


# ── Minimum Relevance Threshold ───────────────────────────
MIN_SCORE = 0.005


# ── Main Query Function ───────────────────────────────────
def query_lexiq(
    question: str,
    strategy: str  = "clause",
    top_k:    int  = 10,
    chunks:   list = None,
    bm25            = None,
) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks (hybrid search)
    2. Score chunks for risk
    3. Build prompt with context
    4. Call Groq LLM
    5. Return answer + sources + risk
    """
    print(f"\n🔍 Query: {question}")
    print(f"   Strategy: {strategy} | Top-K: {top_k}")

    # ── Step 1: Retrieve ──────────────────────────────────
    retrieved = hybrid_search(
        query    = question,
        chunks   = chunks,
        bm25     = bm25,
        strategy = strategy,
        top_k    = top_k,
    )

    # ── Step 2: Filter low relevance ──────────────────────
    relevant = [r for r in retrieved if r["score"] >= MIN_SCORE]

    if not relevant:
        print("   ⚠️  No relevant chunks found")
        return {
            "question":   question,
            "answer":     NO_CONTEXT_PROMPT,
            "sources":    [],
            "risk_level": "UNKNOWN",
            "risk_emoji": "⚪",
            "chunks":     [],
        }

    # ── Step 3: Score risk ────────────────────────────────
    relevant = score_retrieved_chunks(relevant)

    # ── Step 4: Build prompt ──────────────────────────────
    prompt = build_query_prompt(question, relevant)

    # ── Step 5: Call Groq ─────────────────────────────────
    print(f"   📤 Sending to Groq ({len(relevant)} chunks)...")

    response = client.chat.completions.create(
        model    = MODEL,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature = 0.1,   # low temperature = more factual, less creative
        max_tokens  = 1024,
    )

    answer = response.choices[0].message.content

    # ── Step 6: Score answer risk ─────────────────────────
    risk_level = score_answer_risk(answer)
    risk_emoji = get_risk_emoji(risk_level)

    # ── Step 7: Build sources list ────────────────────────
    sources = []
    seen    = set()
    for chunk in relevant:
        key = f"{chunk['metadata'].get('filename')}_{chunk['metadata'].get('page')}"
        if key not in seen:
            sources.append({
                "filename":   chunk["metadata"].get("filename", "unknown"),
                "page":       chunk["metadata"].get("page", "?"),
                "category":   chunk["metadata"].get("category", "?"),
                "risk_level": chunk["risk_level"],
                "risk_emoji": chunk["risk_emoji"],
            })
            seen.add(key)

    print(f"   ✅ Answer generated | Risk: {risk_emoji} {risk_level}")

    return {
        "question":   question,
        "answer":     answer,
        "sources":    sources,
        "risk_level": risk_level,
        "risk_emoji": risk_emoji,
        "chunks":     relevant,
    }


# ── RAG vs No-RAG Baseline ────────────────────────────────
def query_no_rag(question: str) -> str:
    """
    Calls the LLM WITHOUT any retrieved context.
    Baseline comparison — shows how much RAG improves faithfulness.
    """
    response = client.chat.completions.create(
        model    = MODEL,
        messages = [
            {"role": "system", "content": "You are a helpful legal assistant."},
            {"role": "user",   "content": question},
        ],
        temperature = 0.1,
        max_tokens  = 512,
    )
    return response.choices[0].message.content


# ── Test ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🔧 Loading BM25 corpus...")
    chunks, bm25 = load_corpus(strategy="clause")

    test_questions = [
        "What is the penalty for breach of contract under Indian law?",
        "What are the GST invoice mandatory fields?",
        "How much interest does an MSME get for delayed payments?",
    ]

    for question in test_questions:
        print(f"\n{'='*65}")
        result = query_lexiq(question, chunks=chunks, bm25=bm25)

        print(f"\n📋 ANSWER:")
        print(result["answer"])

        print(f"\n📚 SOURCES USED:")
        for s in result["sources"]:
            print(f"   {s['risk_emoji']} {s['filename']} (Page {s['page']}) [{s['risk_level']}]")

        print(f"\n⚠️  OVERALL RISK: {result['risk_emoji']} {result['risk_level']}")

        print(f"\n{'─'*65}")
        print(f"🔄 WITHOUT RAG (baseline):")
        no_rag = query_no_rag(question)
        print(no_rag[:400] + "...")