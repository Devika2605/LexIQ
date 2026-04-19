# ── Query Expansion ───────────────────────────────────────
# Maps user questions to legal terminology
# This bridges the gap between how users ask and how laws are written

EXPANSIONS = {
    # Minor / capacity queries — more specific
    "minor": "minor competent contract Section 11 who is competent to contract void ab initio incapable",
    "minor enters": "Section 11 competent contract minor void ab initio person of unsound mind",
    "child": "minor competent contract Section 11 Indian Contract Act",
    "age":   "minor competent contract capacity Section 11",

    # NDA queries
    "nda":                  "non disclosure agreement confidential information trade secret receiving party disclosing party",
    "non disclosure":       "NDA confidential information receiving party disclosing party obligations",
    "confidentiality":      "confidential information NDA non disclosure agreement trade secret",
    "what does it protect": "confidential information trade secret proprietary business information",

    # Contract basics
    "void":     "void voidable contract Section 2 Indian Contract Act",
    "voidable": "voidable contract coercion fraud misrepresentation Section 19",

    # Payment queries
    "delayed payment": "MSMED Act Section 15 16 45 days interest RBI bank rate compound",
    "msme payment":    "MSMED Act Section 15 buyer supplier payment 45 days appointed day",
    "interest rate":   "MSMED Act Section 16 three times bank rate RBI compound interest",

    # GST queries
    "gst invoice":  "tax invoice CGST Rules mandatory fields GSTIN supplier buyer",
    "invoice":      "tax invoice CGST Rules Section 31 mandatory fields registered person",
    "gst":          "CGST Act IGST supply goods services registered taxable person",

    # Breach queries
    "breach":      "breach contract Section 73 74 compensation damages Indian Contract Act",
    "penalty":     "penalty breach Section 73 74 compensation liquidated damages stipulated",

    # Arbitration
    "arbitration": "Arbitration Conciliation Act 1996 Section 7 arbitral tribunal award",
    "dispute":     "arbitration dispute resolution Section 7 arbitration agreement",

    # Employment
    "termination": "notice period termination employment agreement months written",
    "notice period": "termination notice months written employment founder agreement",

    # IP
    "intellectual property": "IP assignment copyright trademark patent ownership company employee",
    "copyright": "Copyright Act 1957 Section 22 duration literary works author",

    # Guarantee
    "guarantee": "Section 126 contract guarantee surety principal debtor creditor",
    "surety":    "Section 126 127 contract guarantee surety principal debtor",

    # Partnership
    "partnership": "Indian Partnership Act 1932 partners rights duties liability firm",
    "llp":         "LLP Act 2008 limited liability partnership contribution",

    # Consumer
    "consumer": "Consumer Protection Act 2019 rights redressal unfair trade practice",
    "consumer rights": "Consumer Protection Act 2019 Section 2 right to be informed safety",
}


def expand_query(query: str) -> str:
    """
    Expands a user query with legal terminology.
    Helps bridge vocabulary gap between user language and legal language.

    Example:
        "What happens when a minor enters a contract?"
        → "What happens when a minor enters a contract?
           minor competent contract Section 11 Indian Contract Act void ab initio"
    """
    query_lower   = query.lower()
    expansions    = []

    for keyword, expansion in EXPANSIONS.items():
        if keyword in query_lower:
            expansions.append(expansion)

    if expansions:
        expanded = query + " " + " ".join(expansions)
        return expanded

    return query  # return original if no expansion found