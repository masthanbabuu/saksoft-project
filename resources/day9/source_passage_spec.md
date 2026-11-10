# Feature Spec: Show the Source Passage

## User need
When the assistant answers using a document, the user should be
able to see the source passage behind the answer and verify it.

## Acceptance criteria
- Each citation includes a source name and exact passage.
- Citations refer only to passages selected for the answer.
- Unauthorized passages are excluded before generation.
- Missing or invalid citations cause the assistant to abstain.
- The API response exposes both source and passage.

## Out of scope
- Live database integration.
- Live LLM integration.
- Authentication wiring.
- Frontend display changes.
