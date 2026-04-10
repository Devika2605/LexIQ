import sys
sys.path.insert(0, '.')

import json
from retrieval.dense_retriever import dense_search

# Load test dataset
data = json.load(open('evaluation/test_dataset.json'))
q07  = data[6]['question']
q10  = data[9]['question']

print(f"Q07: {q07}")
print(f"Q10: {q10}")
print()

# Test Q07
print("=== Q07 Retrieval Results ===")
results = dense_search(q07, strategy='clause', top_k=5)
for i, r in enumerate(results, 1):
    filename = r['metadata']['filename']
    page     = r['metadata']['page']
    score    = r['score']
    text     = r['text'][:200]
    print(f"#{i} [{score:.3f}] {filename} page {page}")
    print(f"   {text}")
    print()

print()

# Test Q10
print("=== Q10 Retrieval Results ===")
results = dense_search(q10, strategy='clause', top_k=5)
for i, r in enumerate(results, 1):
    filename = r['metadata']['filename']
    page     = r['metadata']['page']
    score    = r['score']
    text     = r['text'][:200]
    print(f"#{i} [{score:.3f}] {filename} page {page}")
    print(f"   {text}")
    print()