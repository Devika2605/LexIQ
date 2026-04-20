# ⚖️ LexIQ — Legal Contract Intelligence for Indian SMBs

> RAG-powered legal assistant that answers contract law questions, scans clause risks, and cross-references uploaded agreements against Indian legislation — deployed full-stack.

---

## The Problem

Indian SMBs routinely sign contracts without immediate access to legal counsel. Hidden liability clauses, unfair payment terms, weak NDA protections, MSME delayed payment violations, and GST documentation errors go unnoticed — often until it's too late.

**LexIQ solves this** by combining retrieval-augmented generation over 38 Indian legal documents with clause-level risk scoring, giving instant legal intelligence to anyone who uploads a contract.

---

## Live Demo

| Service | URL |
|---------|-----|
| 🌐 Frontend | `https://your-vercel-url.vercel.app` |
| ⚙️ API | `https://devikand-lexiq-api.hf.space` |
| 📖 API Docs | `https://devikand-lexiq-api.hf.space/docs` |

---

## Features

### 🔍 Legal Q&A with RAG
Ask natural language questions grounded in Indian law:
- *"What is the penalty for breach of contract?"*
- *"What are MSME 45-day payment rules?"*
- *"What makes a contract void in India?"*

Every answer is retrieved from real legal documents with source citations and a risk level indicator.

### 📄 Contract Upload + Risk Scanner
Upload any PDF contract and get:
- Clause-by-clause analysis (HIGH / MEDIUM / LOW risk)
- Cross-referenced against Indian Contract Act, MSMED Act, GST rules
- Full text expansion per clause with page references

### ⚡ Hybrid Retrieval System
Three retrieval modes fused via Reciprocal Rank Fusion:
- **Dense** — semantic search using `all-MiniLM-L6-v2` embeddings + ChromaDB
- **Sparse** — BM25 keyword search via `rank-bm25`
- **Hybrid** — RRF fusion of both

Includes legal query expansion: *"minor enters contract"* → mapped to Section 11, competency provisions.

### 📊 Evaluation Framework
Custom RAGAS-style evaluation over **51 hand-curated Indian law Q&A pairs** — no OpenAI dependency:
- Faithfulness, Answer Relevancy, Context Precision, Context Recall
- Failure analysis across 9 retrieval configurations
- Best config: `fixed chunking + dense retrieval` → faithfulness **0.598**

---

## Architecture

```
User Query
    │
    ▼
Query Expander ──► Legal term mapping
    │
    ▼
Hybrid Retriever
  ├── Dense (ChromaDB + MiniLM embeddings)
  ├── Sparse (BM25)
  └── RRF Fusion
    │
    ▼
Context Reranker
    │
    ▼
Groq LLM (llama-3.1-8b-instant)
    │
    ▼
Answer + Sources + Risk Level
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | Groq — `llama-3.1-8b-instant` |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers) |
| Vector DB | ChromaDB (persistent) |
| Sparse Retrieval | rank-bm25 |
| Backend | FastAPI + Uvicorn |
| Frontend | React 18 |
| Backend Hosting | Hugging Face Spaces (Docker, 16GB RAM) |
| Frontend Hosting | Vercel |
| Evaluation | Custom Groq-based RAGAS (OpenAI-free) |

---

## Legal Corpus — 38 Documents

**Legislation**
- Indian Contract Act 1872
- Sale of Goods Act 1930
- Companies Act 2013, LLP Act 2008
- Arbitration and Conciliation Act 1996
- Specific Relief Act 1963, Limitation Act 1963
- Consumer Protection Act 2019
- Payment of Wages Act, Minimum Wages Act
- Patents / Copyright / Trademark Acts

**Compliance**
- CGST Act 2017 + Rules, IGST Act 2017
- MSMED Act 2006
- MSME 45-Day Payment Rules

**Contract Templates**
- Employment Agreements, NDA Templates
- IP Assignment, Service Agreements
- Consultancy & Founder Agreements

---

## Evaluation Results

| Configuration | Faithfulness | Answer Rel. | Ctx. Precision | Ctx. Recall |
|---------------|-------------|-------------|----------------|-------------|
| fixed + dense ⭐ | **0.598** | 0.721 | 0.643 | 0.584 |
| fixed + hybrid | 0.547 | 0.689 | 0.612 | 0.541 |
| recursive + dense | 0.488 | 0.651 | 0.573 | 0.512 |
| fixed + sparse | 0.309 | 0.498 | 0.412 | 0.378 |

**Key findings:**
- Dense retrieval consistently outperforms sparse BM25 (vocabulary mismatch with legal terminology)
- 70% of failures are retrieval failures, not LLM hallucination — query expansion matters more than prompt engineering
- Query expansion fixed multiple 0.00-score queries (minor contracts, NDA clauses)

---

## Project Structure

```
LexIQ/
├── api/
│   └── main.py                  # FastAPI app, all endpoints
├── ingestion/
│   ├── pdf_parser.py
│   ├── chunker.py               # fixed / recursive / clause strategies
│   └── embedder.py              # MiniLM + ChromaDB storage
├── retrieval/
│   ├── dense_retriever.py
│   ├── sparse_retriever.py      # BM25
│   ├── hybrid_retriever.py      # RRF fusion
│   └── query_expander.py        # legal term mapping
├── generation/
│   ├── generator.py             # Groq LLM calls
│   ├── prompt_templates.py
│   └── risk_scorer.py           # clause risk classification
├── evaluation/
│   ├── ragas_eval.py            # custom eval pipeline
│   ├── failure_analysis.py
│   ├── test_dataset.json        # 51 Q&A pairs
│   └── results/
├── frontend-react/
│   ├── src/
│   │   ├── App.js
│   │   └── components/
│   │       ├── ChatTab.js
│   │       ├── RiskScanTab.js
│   │       └── EvalTab.js
│   └── package.json
├── chroma_db/                   # persistent vector index (Git LFS)
├── Dockerfile
└── requirements.txt
```

---

## Local Setup

**1. Clone and install**
```bash
git clone https://github.com/Devika2605/LexIQ
cd LexIQ
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

**2. Environment variables**
```bash
# Create .env in root
GROQ_API_KEY=your_groq_api_key_here
```

**3. Run backend**
```bash
python api/main.py
# API live at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**4. Run frontend**
```bash
cd frontend-react
npm install
npm start
# UI at http://localhost:3000
```

**5. Run evaluation**
```bash
python evaluation/ragas_eval.py
python evaluation/failure_analysis.py
```

---

## Deployment

| Layer | Platform | Notes |
|-------|----------|-------|
| Backend | Hugging Face Spaces (Docker) | 16GB RAM — handles MiniLM + ChromaDB |
| Frontend | Vercel | Auto-deploys from GitHub main branch |
| Vector Index | Git LFS | 204MB ChromaDB pushed via LFS |

> ⚠️ HF Spaces free tier sleeps after 48h inactivity. First request after sleep takes ~30s to wake.

---

## Future Improvements

- OCR support for scanned PDFs
- Clause recommendation and redlining suggestions
- Fine-tuned legal embeddings for Indian terminology
- Multi-user sessions with persistent history
- Citation confidence scoring
- Admin analytics dashboard

---

## Author

**Devika N D** — AI & ML undergraduate, JNNCE  
📧 devikashetty2716@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/devika2605) · [GitHub](https://github.com/Devika2605)

---

## License

For academic and educational use only.
