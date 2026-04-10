import fitz  # PyMuPDF
import pdfplumber
import json
import os
from pathlib import Path


# ── Config ────────────────────────────────────────────────
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────
def get_metadata_from_path(pdf_path: Path) -> dict:
    """
    Extracts category, subcategory, doc_type from folder structure.
    e.g. data/raw/legislation/labour_law/payment_of_wages_act_1936.pdf
    → category=legislation, subcategory=labour_law, doc_type=act
    """
    parts = pdf_path.parts  # splits path into components

    # Find position of 'raw' in path
    try:
        raw_index = parts.index("raw")
    except ValueError:
        raw_index = 0

    category    = parts[raw_index + 1] if len(parts) > raw_index + 1 else "unknown"
    subcategory = parts[raw_index + 2] if len(parts) > raw_index + 2 else "unknown"
    filename    = pdf_path.stem  # filename without .pdf

    # Infer doc_type from category
    if category == "legislation":
        doc_type = "act"
    elif category == "compliance":
        doc_type = "compliance"
    elif category == "templates":
        doc_type = "template"
    else:
        doc_type = "unknown"

    return {
        "category":    category,
        "subcategory": subcategory,
        "doc_type":    doc_type,
        "filename":    filename,
        "filepath":    str(pdf_path),
    }


def is_scanned_pdf(pdf_path: Path) -> bool:
    """
    Checks if a PDF is a scanned image (no selectable text).
    Scanned PDFs need OCR — we skip them for now and flag them.
    """
    doc = fitz.open(pdf_path)
    text_found = False
    for page in doc:
        if len(page.get_text().strip()) > 50:
            text_found = True
            break
    doc.close()
    return not text_found


def extract_text_pymupdf(pdf_path: Path) -> list[dict]:
    """
    Extracts text page by page using PyMuPDF.
    Returns a list of dicts, one per page.
    Fast and accurate for most PDFs.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")  # plain text extraction
        text = text.strip()

        if text:  # skip empty pages
            pages.append({
                "page_number": page_num,
                "text": text,
                "char_count": len(text),
            })

    doc.close()
    return pages


def extract_tables_pdfplumber(pdf_path: Path) -> list[dict]:
    """
    Extracts tables using pdfplumber.
    Tables in legal PDFs (schedules, rates, penalties) are
    missed by plain text extraction — this captures them.
    """
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_tables = page.extract_tables()

            for table_idx, table in enumerate(page_tables):
                if not table:
                    continue

                # Convert table to readable text
                # First row is usually the header
                rows_text = []
                for row in table:
                    # Clean None values
                    cleaned = [cell if cell else "" for cell in row]
                    rows_text.append(" | ".join(cleaned))

                table_text = "\n".join(rows_text)

                if table_text.strip():
                    tables.append({
                        "page_number": page_num,
                        "table_index": table_idx,
                        "text": table_text,
                        "type": "table",
                    })

    return tables


def parse_pdf(pdf_path: Path) -> dict | None:
    """
    Main function — parses a single PDF.
    Combines text extraction (PyMuPDF) + table extraction (pdfplumber).
    Returns a structured dict ready to be saved as JSON.
    """
    print(f"  Parsing: {pdf_path.name}")

    # Check if scanned
    if is_scanned_pdf(pdf_path):
        print(f"  ⚠️  SKIPPED (scanned PDF, no text layer): {pdf_path.name}")
        return None

    # Extract metadata from folder path
    metadata = get_metadata_from_path(pdf_path)

    # Extract text pages
    pages = extract_text_pymupdf(pdf_path)
    if not pages:
        print(f"  ⚠️  SKIPPED (no text extracted): {pdf_path.name}")
        return None

    # Extract tables
    tables = extract_tables_pdfplumber(pdf_path)

    # Build final document structure
    document = {
        "metadata": metadata,
        "total_pages": len(pages),
        "total_tables": len(tables),
        "pages": pages,
        "tables": tables,
        "total_chars": sum(p["char_count"] for p in pages),
    }

    return document


def save_as_json(document: dict, pdf_path: Path):
    """
    Saves parsed document as JSON in data/processed/
    Mirrors the folder structure of data/raw/
    """
    # Mirror the raw folder structure in processed/
    relative_path = pdf_path.relative_to(RAW_DIR)
    output_path = PROCESSED_DIR / relative_path.with_suffix(".json")

    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Saved: {output_path}")


# ── Main Runner ───────────────────────────────────────────
def parse_all_pdfs():
    """
    Walks data/raw/ recursively and parses every PDF it finds.
    """
    pdf_files = list(RAW_DIR.rglob("*.pdf"))

    if not pdf_files:
        print("❌ No PDF files found in data/raw/")
        print("   Make sure your PDFs are in the right folders.")
        return

    print(f"\n📂 Found {len(pdf_files)} PDFs\n")

    success = 0
    skipped = 0
    failed  = 0

    for pdf_path in pdf_files:
        try:
            document = parse_pdf(pdf_path)

            if document is None:
                skipped += 1
                continue

            save_as_json(document, pdf_path)
            success += 1

        except Exception as e:
            print(f"  ❌ FAILED: {pdf_path.name} → {e}")
            failed += 1

    # Summary
    print(f"\n{'─'*50}")
    print(f"✅ Successfully parsed : {success}")
    print(f"⚠️  Skipped (scanned)  : {skipped}")
    print(f"❌ Failed              : {failed}")
    print(f"{'─'*50}")
    print(f"\nOutput saved to: {PROCESSED_DIR}/")


if __name__ == "__main__":
    parse_all_pdfs()