# Implementation Plan: Show the Source Passage

1. Retrieve passages using tenant and role constraints.
2. Enforce authorization again before context assembly.
3. Assemble complete passages within the token budget.
4. Ask the generator to answer using the selected context.
5. Validate returned source IDs against selected passages.
6. Return the exact source name and passage in each citation.
7. Test service behaviour and API response serialization.

## Current limitation
The service-level ask() function accepts injected retriever and
generator dependencies. The existing API route still uses the
safe no-source fallback. Live dependencies and authentication
are not connected.
