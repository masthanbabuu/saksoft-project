# Day 15 – Consulting Practice

## Project Objective

Build a secure AI-powered parcel assistant using n8n, Langflow, Ollama and FastAPI.

## Scope

- AI-based parcel question answering.
- API integration and conversation memory.
- Webhook authentication and execution-data pruning.
- Secure handling of customer information.
- Playground and API testing.

## Assumption Log

| ID | Assumption | Status |
|---|---|---|
| A01 | Ollama is suitable for local development. | Validated |
| A02 | FastAPI is the central business service. | Validated |
| A03 | PostgreSQL supports conversation memory. | Validated |
| A04 | Parcel source data will be available. | Pending |
| A05 | Python enforces access controls and PII protection. | Requires verification |

## Open Questions

- When will parcel source data be available?
- What customer roles and permissions are required?
- What are the production hosting requirements?
- What data retention policy must be followed?

## Acceptance Criteria

- Successful authenticated API requests.
- Dynamic questions passed to FastAPI.
- No fabricated parcel information.
- Verified access controls and PII protection.
- Mentor approval of project scope.

## Mentor Sign-off

Status: Pending

Mentor name:

Approval date:

Feedback:
