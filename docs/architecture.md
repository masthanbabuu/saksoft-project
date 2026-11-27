# Architecture

Audience: Developers and technical reviewers.

## Components

User -> Caddy HTTPS proxy -> FastAPI -> PostgreSQL
                                |
                                -> LLM provider

LangGraph runs as a separate internal service.

## Data model
- Parcels, hubs and scan events.
- Documents and permitted roles.
- Authentication users, sessions and audit events.

## Request flow
1. User submits a request.
2. FastAPI validates the input and applicable permissions.
3. The service retrieves permitted information.
4. The answering service processes the question.
5. The application returns a response.

## Security
- Authentication and authorization.
- Password hashing and session management.
- Request size and rate limits.
- Non-root application container.
- HTTPS and security headers.
