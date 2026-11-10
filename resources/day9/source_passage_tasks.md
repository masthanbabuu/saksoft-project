# Tasks: Show the Source Passage

- [x] Define the source-passage acceptance criteria.
- [x] Implement context assembly with a token budget.
- [x] Filter unauthorized passages.
- [x] Validate generated citation IDs.
- [x] Return exact source passages with citations.
- [x] Add service tests for citations and authorization.
- [x] Add API serialization test for source and passage.
- [x] Run the full test suite.
- [ ] Connect real retrieval, generation and authentication.
- [ ] Add frontend source-passage display.

## Test results
- API tests: 7 passed.
- Full test suite: 34 passed.

The API test uses a mocked service. It verifies response
serialization, not live retrieval or generation.
