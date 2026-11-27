# Day 14 – Knowledge Assistant Consulting Plan

## 1. Confirmed Requirements

- Build a Knowledge Assistant page using FastAPI, Jinja2 and HTMX.
- Provide a question input field with a clear label.
- Submit questions using HTMX without a full-page reload.
- Display generated answers and supporting citations.
- Enable Jinja2 autoescaping to protect against XSS.
- Implement CSRF token validation for form submissions.
- Configure Content Security Policy (CSP) and security headers.
- Ensure keyboard accessibility and visible focus indicators.
- Provide clear status messages and actionable error guidance.
- Add automated acceptance tests for critical functionality.

## 2. Suggestions

- Integrate an approved organizational knowledge source.
- Add authentication and role-based access control.
- Display source names and relevant passages alongside answers.
- Add loading indicators while the assistant processes questions.
- Provide clear messages when no supporting citations are available.
- Use WCAG accessibility guidelines when reviewing the interface.
- Monitor response time, errors and application usage.
- Keep templates, routers and business logic in separate layers.

## 3. Risks and Caveats

- The current answering service returns a placeholder response until a real knowledge retrieval integration is connected.
- Answers must not be presented as verified facts without supporting sources.
- CSRF protection depends on secure session configuration and secret management.
- Production deployments must use HTTPS and a strong session secret.
- External JavaScript dependencies introduce supply-chain risks.
- CSP must be reviewed whenever new scripts, styles or external services are introduced.
- Sensitive organizational information must be protected through authentication and authorization.
- Accessibility and contrast should be validated in real browsers and assistive technologies.
- Performance and scalability must be tested with realistic workloads.

## Acceptance Test Evidence

The following automated checks are passing:

1. Knowledge Assistant page loads successfully.
2. Accessibility labels and keyboard focus styles are present.
3. Security headers are returned.
4. Invalid CSRF tokens are rejected.
5. Answers and citations render correctly.
6. Script tags are escaped by Jinja2 autoescaping.

Test suite result: 50 passed.
Ruff formatting and linting: Passed.
