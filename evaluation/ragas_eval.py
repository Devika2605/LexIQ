import sys
import json
import os
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from groq import Groq

from retrieval.hybrid_retriever import hybrid_search
from retrieval.sparse_retriever import load_corpus
from retrieval.dense_retriever  import dense_search

load_dotenv()

# ── Config ────────────────────────────────────────────────
TEST_DATASET_PATH = Path("evaluation/test_dataset.json")
RESULTS_DIR       = Path("evaluation/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL       = "llama-3.1-8b-instant"


# ── Load Test Dataset ─────────────────────────────────────
def load_test_dataset() -> list[dict]:
    with open(TEST_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Generate Answer ───────────────────────────────────────
def generate_answer(question: str, contexts: list[str]) -> str:
    context_text = "\n\n".join(
        f"[Document {i+1}]\n{ctx}"
        for i, ctx in enumerate(contexts)
    )
    prompt = f"""Based on the following legal documents, answer the question.
Answer ONLY from the provided context. If the answer is not in the context, say "I cannot find this in the provided documents."

Context:
{context_text}

Question: {question}

Answer:"""

    try:
        response = groq_client.chat.completions.create(
            model       = MODEL,
            messages    = [
                {"role": "system", "content": "You are a legal assistant. Answer only from the provided context."},
                {"role": "user",   "content": prompt},
            ],
            temperature = 0.1,
            max_tokens  = 512,
        )
        return response.choices[0].message.content
    except Exception as e:
        time.sleep(10)  # rate limit pause
        return "Error generating answer."


# ── Manual RAGAS-style Metrics ────────────────────────────
# We implement our own metrics using Groq
# This avoids the OpenAI dependency completely

def score_faithfulness(question: str, answer: str, contexts: list[str]) -> float:
    """
    Measures if the answer is grounded in the retrieved contexts.
    Asks LLM: does the answer contain only information from the context?
    """
    context_text = "\n".join(contexts)
    prompt = f"""You are evaluating whether an answer is faithful to the provided context.

Context:
{context_text[:2000]}

Question: {question}
Answer: {answer}

Is every claim in the answer supported by the context? 
Respond with a score from 0.0 to 1.0 where:
- 1.0 = answer is completely grounded in the context
- 0.5 = answer is partially grounded, some claims not in context  
- 0.0 = answer contains information not in the context

Respond with ONLY a number between 0.0 and 1.0. Nothing else."""

    try:
        response = groq_client.chat.completions.create(
            model       = MODEL,
            messages    = [{"role": "user", "content": prompt}],
            temperature = 0.0,
            max_tokens  = 10,
        )
        score_str = response.choices[0].message.content.strip()
        return min(1.0, max(0.0, float(score_str)))
    except:
        return 0.5


def score_answer_relevancy(question: str, answer: str) -> float:
    """
    Measures if the answer actually addresses the question.
    """
    prompt = f"""You are evaluating whether an answer is relevant to the question.

Question: {question}
Answer: {answer}

Does the answer directly address the question asked?
Respond with a score from 0.0 to 1.0 where:
- 1.0 = answer directly and completely addresses the question
- 0.5 = answer partially addresses the question
- 0.0 = answer does not address the question at all

Respond with ONLY a number between 0.0 and 1.0. Nothing else."""

    try:
        response = groq_client.chat.completions.create(
            model       = MODEL,
            messages    = [{"role": "user", "content": prompt}],
            temperature = 0.0,
            max_tokens  = 10,
        )
        score_str = response.choices[0].message.content.strip()
        return min(1.0, max(0.0, float(score_str)))
    except:
        return 0.5


def score_context_precision(question: str, contexts: list[str]) -> float:
    """
    Measures what fraction of retrieved contexts are actually relevant.
    """
    if not contexts:
        return 0.0

    relevant = 0
    for ctx in contexts:
        prompt = f"""Is the following context relevant to answering this question?

Question: {question}
Context: {ctx[:500]}

Respond with ONLY 1 (relevant) or 0 (not relevant). Nothing else."""
        try:
            response = groq_client.chat.completions.create(
                model       = MODEL,
                messages    = [{"role": "user", "content": prompt}],
                temperature = 0.0,
                max_tokens  = 5,
            )
            score_str = response.choices[0].message.content.strip()
            if "1" in score_str:
                relevant += 1
        except:
            relevant += 0.5

    return relevant / len(contexts)


def score_context_recall(question: str, ground_truth: str, contexts: list[str]) -> float:
    """
    Measures if the retrieved contexts contain enough to answer correctly.
    """
    context_text = "\n".join(contexts)
    prompt = f"""You are checking if the provided context contains enough information to answer a question correctly.

Ground Truth Answer: {ground_truth}
Retrieved Context: {context_text[:2000]}

Does the retrieved context contain the key information needed to arrive at the ground truth answer?
Respond with a score from 0.0 to 1.0 where:
- 1.0 = context contains all the information needed
- 0.5 = context contains some but not all information needed
- 0.0 = context does not contain the information needed

Respond with ONLY a number between 0.0 and 1.0. Nothing else."""

    try:
        response = groq_client.chat.completions.create(
            model       = MODEL,
            messages    = [{"role": "user", "content": prompt}],
            temperature = 0.0,
            max_tokens  = 10,
        )
        score_str = response.choices[0].message.content.strip()
        return min(1.0, max(0.0, float(score_str)))
    except:
        return 0.5


# ── Run One Experiment ────────────────────────────────────
def run_experiment(
    test_data:   list[dict],
    strategy:    str,
    retriever:   str,
    bm25_chunks: list,
    bm25_index,
    top_k:       int = 5,
) -> dict:
    print(f"\n  ▶ strategy={strategy} | retriever={retriever}")

    faith_scores   = []
    relevancy_scores = []
    precision_scores = []
    recall_scores  = []

    for i, item in enumerate(test_data):
        question     = item["question"]
        ground_truth = item["ground_truth"]

        # Retrieve
        if retriever == "dense":
            retrieved = dense_search(question, strategy=strategy, top_k=top_k)
        elif retriever == "sparse":
            from retrieval.sparse_retriever import sparse_search
            retrieved = sparse_search(question, bm25_chunks, bm25_index, top_k=top_k)
        else:
            retrieved = hybrid_search(
                query    = question,
                chunks   = bm25_chunks,
                bm25     = bm25_index,
                strategy = strategy,
                top_k    = top_k,
            )

        contexts = [r["text"] for r in retrieved]

        # Generate answer
        answer = generate_answer(question, contexts)
        time.sleep(0.5)  # avoid rate limiting

        # Score all 4 metrics
        faith   = score_faithfulness(question, answer, contexts)
        time.sleep(0.3)
        rel     = score_answer_relevancy(question, answer)
        time.sleep(0.3)
        prec    = score_context_precision(question, contexts)
        time.sleep(0.3)
        rec     = score_context_recall(question, ground_truth, contexts)
        time.sleep(0.3)

        faith_scores.append(faith)
        relevancy_scores.append(rel)
        precision_scores.append(prec)
        recall_scores.append(rec)

        print(f"    Q{i+1:02d} | faith={faith:.2f} rel={rel:.2f} prec={prec:.2f} rec={rec:.2f}")

    result = {
        "strategy":          strategy,
        "retriever":         retriever,
        "faithfulness":      round(sum(faith_scores)    / len(faith_scores),    4),
        "answer_relevancy":  round(sum(relevancy_scores)/ len(relevancy_scores),4),
        "context_precision": round(sum(precision_scores)/ len(precision_scores),4),
        "context_recall":    round(sum(recall_scores)   / len(recall_scores),   4),
    }

    print(f"\n  ✅ DONE | faith={result['faithfulness']} | "
          f"rel={result['answer_relevancy']} | "
          f"prec={result['context_precision']} | "
          f"rec={result['context_recall']}")

    return result


# ── Run All 9 Experiments ─────────────────────────────────
def run_all_experiments():
    print("\n📊 Loading test dataset...")
    test_data = load_test_dataset()

    # Use first 10 questions for speed — change to 20 for full eval
    eval_data = test_data[:10]
    print(f"   Running on {len(eval_data)} questions × 9 experiments")
    print(f"   Estimated time: 25-35 minutes\n")

    strategies = ["fixed", "recursive", "clause"]
    retrievers = ["dense", "sparse", "hybrid"]

    print("🔧 Loading BM25 indices...")
    bm25_corpora = {}
    for strategy in strategies:
        chunks, bm25 = load_corpus(strategy=strategy)
        bm25_corpora[strategy] = (chunks, bm25)
    print("✅ All indices loaded\n")

    results = []

    for strategy in strategies:
        chunks, bm25 = bm25_corpora[strategy]
        for retriever in retrievers:
            result = run_experiment(
                test_data   = eval_data,
                strategy    = strategy,
                retriever   = retriever,
                bm25_chunks = chunks,
                bm25_index  = bm25,
                top_k       = 5,
            )
            results.append(result)

            # Save progress after every experiment
            save_results(results, "experiments_progress.json")
            print(f"\n  💾 Progress saved ({len(results)}/9 experiments done)\n")

    save_results(results, "all_experiments.json")
    print_comparison_table(results)
    return results


# ── Save Results ──────────────────────────────────────────
def save_results(results: list[dict], filename: str):
    path = RESULTS_DIR / filename
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


# ── Print Comparison Table ────────────────────────────────
def print_comparison_table(results: list[dict]):
    print(f"\n{'='*85}")
    print(f"  {'Chunking':<12} | {'Retriever':<8} | {'Faithful':>8} | "
          f"{'Ans.Rel':>8} | {'Ctx.Prec':>9} | {'Ctx.Rec':>8}")
    print(f"{'='*85}")

    best_faith = max(r["faithfulness"] for r in results)

    for r in results:
        marker = " ★" if r["faithfulness"] == best_faith else "  "
        print(
            f"  {r['strategy']:<12} | {r['retriever']:<8} | "
            f"{r['faithfulness']:>8.4f} | {r['answer_relevancy']:>8.4f} | "
            f"{r['context_precision']:>9.4f} | {r['context_recall']:>8.4f}{marker}"
        )

    print(f"{'='*85}")

    best  = max(results, key=lambda x: x["faithfulness"])
    worst = min(results, key=lambda x: x["faithfulness"])
    improvement = ((best["faithfulness"] - worst["faithfulness"])
                   / max(worst["faithfulness"], 0.001)) * 100

    print(f"\n★  Best  : {best['strategy']} + {best['retriever']} "
          f"→ faithfulness={best['faithfulness']}")
    print(f"▼  Worst : {worst['strategy']} + {worst['retriever']} "
          f"→ faithfulness={worst['faithfulness']}")
    print(f"🚀 Improvement: {improvement:.1f}% from worst to best")


if __name__ == "__main__":
    run_all_experiments()