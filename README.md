# LexIQ — Legal Contract Intelligence for Indian SMBs

LexIQ is a Legal Contract Intelligence RAG (Retrieval-Augmented Generation) system designed for Indian SMBs to analyze contracts, answer legal queries, identify clause risks, and cross-reference uploaded agreements against Indian law.

It helps users understand contracts faster by combining legal corpus retrieval, AI-powered reasoning, clause-level risk scoring, and document-grounded answers.

---

## Problem Statement

Small and medium businesses often sign contracts without immediate access to legal experts.

This creates risks such as:

* hidden liability clauses
* unfair payment terms
* weak NDA protections
* compliance failures
* MSME delayed payment disputes
* GST and legal documentation errors

LexIQ solves this by providing instant legal intelligence using Indian legal documents and contract templates.

---

## Key Features

### Legal Q&A with RAG

Ask legal questions like:

* What is the penalty for breach of contract?
* What are MSME 45-day payment rules?
* What is force majeure?
* What makes a contract void in India?
* What are NDA confidentiality obligations?

Answers are generated only from retrieved legal documents with source citations.

---

### Contract Upload + Risk Scanner

Upload PDF contracts and get:

* clause-by-clause analysis
* HIGH / MEDIUM / LOW risk scoring
* legal issue detection
* uploaded contract + legal corpus cross-referencing

---

### Hybrid Retrieval System

Supports:

* Dense Retrieval (semantic search using embeddings)
* Sparse Retrieval (BM25 keyword search)
* Hybrid Retrieval (Reciprocal Rank Fusion)

Includes legal query expansion for better retrieval performance.

Example:

"minor enters contract" → mapped to Section 11, competency to contract

---

### Evaluation Framework

Custom evaluation pipeline across 51 legal benchmark questions using:

* Faithfulness
* Answer Relevancy
* Context Precision
* Context Recall

Failure analysis identifies:

* wrong chunk retrieval
* chunk boundary split
* hallucination
* out-of-corpus gaps
* ambiguous questions

---

## Tech Stack

### LLM

Groq — llama-3.1-8b-instant

### Embeddings

all-MiniLM-L6-v2

### Vector Database

ChromaDB

### Sparse Retrieval

rank-bm25

### Backend

FastAPI

### Frontend

React (production frontend)

### Previous UI

Streamlit (used during development)

### Evaluation

Custom Groq-based RAG evaluation (OpenAI-free)

---

## Project Structure

```text
LexIQ/
│
├── api/
│   └── main.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── chunks/
│   └── uploads/
│
├── ingestion/
│   ├── pdf_parser.py
│   ├── chunker.py
│   └── embedder.py
│
├── retrieval/
│   ├── dense_retriever.py
│   ├── sparse_retriever.py
│   ├── hybrid_retriever.py
│   └── query_expander.py
│
├── generation/
│   ├── generator.py
│   ├── prompt_templates.py
│   └── risk_scorer.py
│
├── evaluation/
│   ├── ragas_eval.py
│   ├── failure_analysis.py
│   ├── test_dataset.json
│   └── results/
│
├── frontend-react/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── requirements.txt
├── .env
└── README.md
```

---

## Dataset / Corpus

The system uses 38 legal and compliance documents including:

### Legislation

* Indian Contract Act 1872
* Sale of Goods Act 1930
* Companies Act 2013
* LLP Act 2008
* Arbitration and Conciliation Act 1996
* Specific Relief Act 1963
* Limitation Act 1963
* Consumer Protection Act 2019
* Payment of Wages Act
* Minimum Wages Act
* Patents / Copyright / Trademark Acts

### Compliance

* CGST Act 2017
* CGST Rules 2017
* IGST Act 2017
* MSMED Act 2006
* MSME 45-Day Payment Rules

### Templates

* Employment Agreements
* NDA Templates
* IP Assignment Agreements
* Service Agreements
* Consultancy Agreements
* Founder Agreements

---

## Setup Instructions

## 1. Clone Repository

```bash
git clone YOUR_GITHUB_REPO_LINK
cd LexIQ
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 4. Add Environment Variables

Create `.env`

```env
GROQ_API_KEY=your_groq_api_key
```

---

## 5. Run Backend API

```bash
python api/main.py
```

Runs on:

```text
http://localhost:8000
```

---

## 6. Run React Frontend

```bash
cd frontend-react
npm install
npm start
```

Runs on:

```text
http://localhost:3000
```

---

## Evaluation Commands

### Run Benchmark Experiments

```bash
python evaluation/ragas_eval.py
```

### Run Failure Analysis

```bash
python evaluation/failure_analysis.py
```

---

## Current Evaluation Results

| Configuration     | Faithfulness |
| ----------------- | -----------: |
| fixed + dense     |        0.598 |
| fixed + sparse    |        0.309 |
| fixed + hybrid    |        0.547 |
| recursive + dense |        0.488 |

### Key Findings

* Dense retrieval outperforms sparse BM25
* Sparse retrieval suffers from vocabulary mismatch
* Query expansion significantly improves weak queries
* Retrieval quality impacts output more than prompt engineering
* Best production setup: fixed + dense

---

## Deployment

### Frontend

Deployed on Vercel

### Backend

Deployed on Render

### Production Stack

React + FastAPI + ChromaDB + Groq

---

## Future Improvements

* OCR support for scanned PDFs
* Clause recommendation engine
* Contract redlining suggestions
* Multi-user dashboards
* Admin analytics
* Legal clause summarization
* Citation confidence scoring
* Fine-tuned legal embeddings

---

## Author

Built as an AI/ML + RAG Engineering project focused on practical legal intelligence for Indian SMBs.

---

## License

For academic and educational use.
