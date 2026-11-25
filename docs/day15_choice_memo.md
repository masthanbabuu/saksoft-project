# Day 15 – Technology Choice Memo

## Objective

Select a suitable technology for building secure, maintainable AI-powered parcel assistants.

## Weighted Decision Matrix

Scoring: 1 = Poor, 5 = Excellent.

| Criteria | Weight | Plain Python | LangGraph | n8n | Langflow |
|---|---:|---:|---:|---:|---:|
| Security | 35% | 5 | 4 | 3 | 2 |
| Maintainability | 25% | 4 | 3 | 5 | 4 |
| Licence | 20% | 5 | 5 | 3 | 5 |
| Suitability | 20% | 4 | 5 | 4 | 4 |
| Weighted score | 100% | 4.55 | 4.15 | 3.70 | 3.50 |

## Technology Comparison

**Plain Python**
- Licence: Python PSF licence; dependencies require separate review.
- Security: Fine-grained control, but requires secure coding and dependency patching.
- Maintainers: Python developers.
- Best for: Production APIs, business logic and sensitive data processing.

**LangGraph**
- Licence: MIT for the core library.
- Security: Published authentication and deserialization vulnerabilities require patch management.
- Maintainers: Python and AI engineers.
- Best for: Complex stateful agents and multi-step workflows.

**n8n**
- Licence: Sustainable Use License with commercial usage restrictions.
- Security: Published code execution and SSRF vulnerabilities require regular updates.
- Maintainers: Automation engineers and trained business users.
- Best for: Workflow automation, webhooks and application integration.

**Langflow**
- Licence: MIT.
- Security: Published code execution and access-control vulnerabilities require patching and infrastructure isolation.
- Maintainers: AI engineers and trained low-code developers.
- Best for: Rapid AI prototyping and visual demonstrations.

## Recommendation

Use plain Python and FastAPI for core production services, n8n for workflow integration, Langflow for AI prototyping and LangGraph when complex agent orchestration is required.

Keep access controls, validation and PII protection within the Python service.

## Validation

Successfully integrated n8n and Langflow with Ollama and FastAPI. Langflow Playground and authenticated curl testing passed. Dynamic tool input was confirmed. Actual parcel retrieval remains unverified because no sources are available.

## References

- https://docs.n8n.io/sustainable-use-license/
- https://github.com/n8n-io/n8n/security/advisories
- https://github.com/langchain-ai/langgraph/security/advisories
- https://docs.langflow.org/security

Assessment: The weights are agreed by the trainee. Scores are qualitative engineering estimates, not formal security audit results. Mentor approval and installed-version security verification remain pending.
