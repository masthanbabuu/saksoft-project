"""The /ask endpoint: the place where you build the grounded assistant (days 9 to 14)."""

from fastapi import APIRouter, Depends

from app.models.schemas import AskRequest, AskResponse
from app.services import answering
from app.services.auth_security import require_reader

router = APIRouter(dependencies=[Depends(require_reader)])


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest) -> AskResponse:
    """Thin router: validate (done by Pydantic), call the service, return the result."""
    return answering.answer_question(body.question)
