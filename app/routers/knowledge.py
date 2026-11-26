"""Knowledge Assistant HTML routes with session-backed CSRF protection."""

import secrets
from hmac import compare_digest

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services import answering
from app.services.auth_security import require_reader

router = APIRouter(dependencies=[Depends(require_reader)])
templates = Jinja2Templates(directory="app/templates")

# Explicitly enable autoescaping for all template output.
templates.env.autoescape = True


@router.get("/knowledge", response_class=HTMLResponse)
def knowledge_page(request: Request) -> HTMLResponse:
    """Render the Knowledge Assistant page and create a CSRF token."""
    csrf_token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = csrf_token

    return templates.TemplateResponse(
        request=request,
        name="knowledge.html",
        context={"csrf_token": csrf_token},
    )


@router.post("/knowledge/ask", response_class=HTMLResponse)
def knowledge_ask(
    request: Request,
    question: str = Form(min_length=1, max_length=2000),
    csrf_token: str = Form(min_length=1),
) -> HTMLResponse:
    """Validate the CSRF token and return an answer HTML fragment."""
    expected_token = request.session.get("csrf_token", "")

    if not expected_token or not compare_digest(csrf_token, expected_token):
        raise HTTPException(
            status_code=403, detail="Your session expired. Reload the page and try again."
        )

    if not question.strip():
        raise HTTPException(status_code=422, detail="Please enter a question.")

    result = answering.answer_question(question.strip())

    return templates.TemplateResponse(
        request=request,
        name="partials/answer.html",
        context={"result": result},
    )
