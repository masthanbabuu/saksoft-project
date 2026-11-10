# Chunking strategy evaluation

| Strategy | Chunks | Top-3 hits | Accuracy |
|---|---:|---:|---:|
| fixed_overlap | 42 | 10/10 | 100% |
| sentence | 55 | 10/10 | 100% |
| sentence_window | 35 | 10/10 | 100% |

## Result
Best strategy in this small synthetic test: **fixed_overlap**.

The winning strategy retrieves the expected policy most often within the top three results. Fixed-size chunks are simple but can split related facts; sentence chunks preserve meaning but may be too short; sentence windows retain nearby context at the cost of larger chunks. Results depend on document length, embedding model and question wording.
