# Day 8 – PostgreSQL, pgvector and Access Control

## Completed
- Enabled pgvector in PostgreSQL 16.
- Created document_chunks with VECTOR(768).
- Added tenant, allowed_roles, source and updated_at.
- Loaded 42 document chunks.
- Created HNSW cosine similarity and metadata indexes.
- Implemented similarity search with tenant and role filters before ranking.
- Verified tenant isolation.
- Verified agent cannot access Claims process.
- Verified supervisor and admin can access restricted documents.

## Access policy
- Agent: general policies.
- Supervisor: general and restricted policies.
- Admin: all policies.

## Security result
All demonstrated access-control checks passed.

## Consulting practice
Discovery questions and same-day clarification email remain to be completed.
