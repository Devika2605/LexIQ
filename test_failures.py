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

from retrieval.query_expander import expand_query

print("=== Query Expansion Test ===")
print(f"Q07 expanded: {expand_query(q07)}")
print()
print(f"Q10 expanded: {expand_query(q10)}")
print()

# Test Q07 with expanded query
from retrieval.query_expander import expand_query
q07_expanded = expand_query(q07)
q10_expanded = expand_query(q10)

print("=== Q07 After Expansion ===")
results = dense_search(q07_expanded, strategy='clause', top_k=5)
for i, r in enumerate(results, 1):
    print(f"#{i} [{r['score']:.3f}] {r['metadata']['filename']} page {r['metadata']['page']}")
    print(f"   {r['text'][:200]}")
    print()

print("=== Q10 After Expansion ===")
results = dense_search(q10_expanded, strategy='clause', top_k=5)
for i, r in enumerate(results, 1):
    print(f"#{i} [{r['score']:.3f}] {r['metadata']['filename']} page {r['metadata']['page']}")
    print(f"   {r['text'][:200]}")
    print()