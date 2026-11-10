# High-Level Design: Parcel Policy Answering Service

## 1. Problem statement

Working problem statement — inferred, not a direct client quote:

Users need a reliable way to ask questions about parcel delivery policies and procedures and receive answers supported by relevant source documents. They need to know where an answer came from and should receive an honest "I don't know" when the available documents do not support an answer.

## 2. Data used and why

The project uses parcel-related Markdown documents covering policies, procedures and FAQs.

The evaluation dataset contains 24 documents covering eight parcel topics:
- Delivery windows
- Failed delivery attempts
- Damage claims
- Parcel weight
- Insurance value
- Same-day scanning
- Route changes
- Hazardous goods

Each document has tenant and role-access information. This allows retrieval to respect document permissions.

The 15-question golden set measures retrieval quality and expected source-chunk recall.

## 3. Users

The dataset defines three roles:
- Dispatcher
- Driver
- Customer

Access to documents depends on the user's authorized role and tenant.

## 4. Main system components

1. Document collection: Stores parcel policies, procedures and FAQs.
2. Retrieval component: Finds relevant document chunks for a question.
3. Permission filtering: Restricts retrieval by tenant and role before ranking.
4. Context builder: Selects complete passages within a token budget.
5. Answer generator: Produces an answer using the selected context.
6. Citation validator: Checks that cited source IDs belong to selected passages.
7. FastAPI endpoint: Accepts questions and returns answers with source names and passages.

If sources are missing, unauthorized, or do not support valid citations, the service returns an "I don't know" response.

## 5. Out of scope

- Production database integration
- Live LLM provider integration
- Authentication and authorization wiring into the API
- Frontend source-passage display
- Production deployment and monitoring

These remain future integration tasks. The current API still uses a safe no-source fallback.

## 6. Key decisions and reasons

| Decision | Reason |
|---|---|
| Retrieve only authorized documents | Prevent access to restricted information |
| Filter permissions before ranking | Avoid exposing unauthorized content during retrieval |
| Use a token budget | Keep context within model limits |
| Return exact source passages | Let users verify answers |
| Validate citation IDs | Prevent citations to sources that were not selected |
| Abstain when support is missing | Avoid unsupported answers |
| Evaluate with a golden set | Measure retrieval quality consistently |

## 7. Current evaluation

Offline retrieval evaluation:
- Recall@1: 0.500
- Recall@3: 0.938
- Recall@5: 1.000

The full automated test suite has 34 passing tests.

These results demonstrate retrieval performance on the supplied evaluation dataset. They do not establish live production performance or answer correctness.
