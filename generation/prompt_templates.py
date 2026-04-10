# ── System Prompt ─────────────────────────────────────────
SYSTEM_PROMPT = """You are LexIQ, an expert legal assistant specializing in Indian business law and contracts.

Your job is to answer questions about Indian contracts, business laws, and compliance based ONLY on the provided context documents.

STRICT RULES:
1. Answer ONLY from the provided context. Never use outside knowledge.
2. Always cite your source using [Source: filename, Page X] after every claim.
3. If the answer is not in the context, say exactly: "I cannot find this in the provided documents."
4. Never make up section numbers, penalties, or legal interpretations.
5. If multiple documents are relevant, synthesize them and cite each one.
6. Keep answers clear and practical — the user is a small business owner, not a lawyer.

RISK FLAGGING:
After your answer, always add a risk assessment:
- 🔴 HIGH RISK: clauses that could expose the business to major liability
- 🟡 MEDIUM RISK: clauses that need attention but are manageable
- 🟢 LOW RISK: standard clauses with minimal concern
"""


# ── Query Prompt ──────────────────────────────────────────
def build_query_prompt(question: str, context_chunks: list[dict]) -> str:
    """
    Builds the full prompt by combining retrieved chunks with the question.
    """
    # Format context chunks
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        filename = chunk["metadata"].get("filename", "unknown")
        page     = chunk["metadata"].get("page", "?")
        category = chunk["metadata"].get("category", "?")

        context_parts.append(
            f"[Document {i}]\n"
            f"Source: {filename} | Page: {page} | Category: {category}\n"
            f"---\n"
            f"{chunk['text']}\n"
        )

    context_text = "\n".join(context_parts)

    prompt = f"""Here are the relevant documents retrieved for your question:

{context_text}

---

Question: {question}

Instructions:
- Answer based only on the documents above
- Cite sources as [Source: filename, Page X]
- End with a risk assessment (🔴/🟡/🟢)
- If the answer is not in the documents, say so clearly
"""
    return prompt


# ── No Context Prompt ─────────────────────────────────────
NO_CONTEXT_PROMPT = """I cannot find relevant information about this in the provided legal documents.

This could mean:
- The specific topic is not covered in the current document corpus
- Try rephrasing your question with different keywords
- Consider consulting a qualified legal professional for this specific matter

If you believe this should be in the corpus, please let me know and I can investigate further."""