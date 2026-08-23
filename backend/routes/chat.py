import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ChatRequest, ChatResponse
from ..services import chat_service

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


@router.post(
    "/",
    response_model=ChatResponse
)
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    try:

        result = chat_service.ask_question(
            request.question, db
        )

        return result

    except RuntimeError as exc:
        logger.exception("Chat generation failed")
        raise HTTPException(
            status_code=503,
            detail="The answer service is temporarily unavailable. Please try again later.",
        ) from exc
    except Exception as exc:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=500, detail="Unable to process the question.") from exc
