from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..admin_auth import is_admin, require_admin, sign_in, sign_out
from ..models import Document, Question, KnowledgeGap, Feedback
from ..schemas import (
    DocumentResponse,
    KnowledgeGapResponse,
    AnalyticsResponse
    , AdminLoginRequest
)


auth_router = APIRouter(prefix="/api/admin", tags=["Admin access"])

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@auth_router.get("/session")
def get_admin_session(request: Request):
    """Allow the admin frontend to determine whether a valid session exists."""
    return {"authenticated": is_admin(request)}


@auth_router.post("/login")
def admin_login(payload: AdminLoginRequest, response: Response):
    sign_in(payload.password, response)
    return {"success": True}


@auth_router.post("/logout")
def admin_logout(request: Request, response: Response):
    sign_out(request, response)
    return {"success": True}


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@router.get(
    "/documents",
    response_model=list[DocumentResponse]
)
def get_documents(
    db: Session = Depends(get_db)
):
    """
    Return all uploaded documents.
    """

    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    return documents


# ============================================================
# GET KNOWLEDGE GAPS
# ============================================================

@router.get(
    "/knowledge-gaps",
    response_model=list[KnowledgeGapResponse]
)
def get_knowledge_gaps(
    db: Session = Depends(get_db)
):
    """
    Return questions that the AI could not answer
    from the provided documents.
    """

    gaps = (
        db.query(KnowledgeGap)
        .order_by(KnowledgeGap.created_at.desc())
        .all()
    )

    return gaps


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete(
    "/documents/{document_id}"
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document record from the database.

    Note:
    Physical file and FAISS index handling will be
    added later.
    """

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(document)

    db.commit()

    return {
        "success": True,
        "message": (
            "Document record deleted. The uploaded file and its FAISS vectors were retained; "
            "vector-level deletion is not implemented."
        )
    }


@router.get("/questions")
def get_recent_questions(db: Session = Depends(get_db)):
    """Return recent question history for the admin dashboard."""
    questions = db.query(Question).order_by(Question.created_at.desc()).limit(20).all()
    return [
        {
            "id": question.id,
            "question": question.question,
            "answered": bool(question.answered),
            "created_at": question.created_at,
        }
        for question in questions
    ]


# ============================================================
# ANALYTICS
# ============================================================

@router.get(
    "/analytics",
    response_model=AnalyticsResponse
)
def get_analytics(
    db: Session = Depends(get_db)
):
    """
    Return basic system statistics.
    """

    total_documents = (
        db.query(Document)
        .count()
    )

    total_questions = (
        db.query(Question)
        .count()
    )

    answered_questions = (
        db.query(Question)
        .filter(Question.answered == 1)
        .count()
    )

    unanswered_questions = (
        total_questions -
        answered_questions
    )

    total_knowledge_gaps = (
        db.query(KnowledgeGap)
        .count()
    )

    average_rating = (
        db.query(
            func.avg(Feedback.rating)
        )
        .scalar()
    )

    if average_rating is None:
        average_rating = 0.0

    return {
        "total_documents": total_documents,
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "unanswered_questions": unanswered_questions,
        "total_knowledge_gaps": total_knowledge_gaps,
        "average_rating": round(
            float(average_rating),
            2
        )
    }
