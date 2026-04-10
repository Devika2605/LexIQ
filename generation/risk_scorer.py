# ── Risk Categories ───────────────────────────────────────
RISK_KEYWORDS = {
    "high": [
        "indemnif", "penalty", "liable", "liability", "damages",
        "termination", "breach", "default", "forfeit", "injunction",
        "arbitration", "jurisdiction", "governing law", "liquidated",
        "non-compete", "restraint of trade", "intellectual property",
        "ownership", "assign", "warrant", "represent",
        "unlimited liability", "personal guarantee",
    ],
    "medium": [
        "notice period", "confidential", "exclusiv", "renew",
        "amend", "modify", "waiver", "force majeure", "dispute",
        "payment terms", "invoice", "interest", "late payment",
        "subcontract", "third party", "audit", "inspect",
    ],
    "low": [
        "definitions", "interpretation", "recital", "whereas",
        "general", "miscellaneous", "severability", "entire agreement",
        "counterpart", "headings", "schedule", "annexure",
    ],
}


def score_chunk_risk(text: str) -> str:
    """
    Classifies a chunk as HIGH / MEDIUM / LOW risk
    based on keyword presence.
    Returns the risk level as a string.
    """
    text_lower = text.lower()

    high_count   = sum(1 for kw in RISK_KEYWORDS["high"]   if kw in text_lower)
    medium_count = sum(1 for kw in RISK_KEYWORDS["medium"] if kw in text_lower)
    low_count    = sum(1 for kw in RISK_KEYWORDS["low"]    if kw in text_lower)

    if high_count >= 2:
        return "HIGH"
    elif high_count == 1 or medium_count >= 2:
        return "MEDIUM"
    else:
        return "LOW"


def score_answer_risk(answer: str) -> str:
    """
    Scores the full generated answer for overall risk level.
    """
    return score_chunk_risk(answer)


def get_risk_emoji(risk_level: str) -> str:
    return {
        "HIGH":   "🔴",
        "MEDIUM": "🟡",
        "LOW":    "🟢",
    }.get(risk_level, "⚪")


def score_retrieved_chunks(chunks: list[dict]) -> list[dict]:
    """
    Adds risk_level to each retrieved chunk.
    Used to show risk flags in the UI.
    """
    for chunk in chunks:
        chunk["risk_level"] = score_chunk_risk(chunk["text"])
        chunk["risk_emoji"] = get_risk_emoji(chunk["risk_level"])
    return chunks