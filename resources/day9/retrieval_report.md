# Day 9 – Retrieval Evaluation

## Dataset
- Source: `resources/day7/variant_3_parcels (1).zip`
- Documents evaluated: 24
- Golden questions: 15
- Answerable questions: 8
- Expected refusal questions: 7
- Expected relevant document IDs: 16

## Retrieval method
- Baseline: BM25 lexical ranking
- Search text: document title and body
- Tenant filter: `main`
- Role-based access filtering: applied before ranking
- Evaluation scope: offline ZIP dataset; no live PostgreSQL or pgvector connection

## Recall results

| Metric | Relevant documents retrieved | Recall |
|---|---:|---:|
| Recall@1 | 8/16 | 0.500 (50%) |
| Recall@3 | 15/16 | 0.938 (93.8%) |
| Recall@5 | 16/16 | 1.000 (100%) |

Micro recall and macro recall were equal for all three cut-offs.

## Observation
The only expected document missing from the top three was document `3011` (Delivery window Policy). It appeared at rank four for the first question.

All 16 expected source documents were retrieved within the top five results.

## Permission check
The customer-role route-change question was correctly filtered:
- Route documents in corpus: `3071`, `3072`, `3073`
- Route documents visible to customer: none

## Limitations
- BM25 ranks documents but does not establish whether they support an answer.
- Six unrelated refusal questions still require answerability and abstention testing.
- This is an offline lexical baseline, not a live PostgreSQL/pgvector evaluation.

## Abstention test

- Added a service-level test for an unsupported question when retrieval returns an unrelated document.
- The fake generator returns an answer without valid source IDs.
- Expected behaviour: the service returns "I don't know" with no citations.
- Result: passed as part of the full test suite (34 tests).

### Abstention limitation

This test verifies the service's fail-closed citation validation using a fake generator. It does not measure whether a real LLM can recognize unsupported questions. The six unrelated golden-set refusal questions still need evaluation with a real answerability mechanism and representative generator.
