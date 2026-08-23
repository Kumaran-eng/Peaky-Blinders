from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import KnowledgeGap


# ============================================================
# SAVE KNOWLEDGE GAP
# ============================================================

def save_knowledge_gap(
    db: Session,
    question: str,
    reason: str = "Information not found in the provided documents."
) -> KnowledgeGap:
    """
    Save a question that could not be answered
    from the provided knowledge base.
    """

    if not question or not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )

    question = question.strip()


    # --------------------------------------------------------
    # Check whether the same question already exists
    # --------------------------------------------------------

    existing_gap = (
        db.query(KnowledgeGap)
        .filter(
            func.lower(
                KnowledgeGap.question
            ) == question.lower()
        )
        .first()
    )


    # --------------------------------------------------------
    # If it already exists, return the existing record
    # --------------------------------------------------------

    if existing_gap:

        return existing_gap


    # --------------------------------------------------------
    # Create new knowledge gap
    # --------------------------------------------------------

    gap = KnowledgeGap(

        question=question,

        reason=reason

    )


    db.add(gap)

    db.commit()

    db.refresh(gap)


    return gap


# ============================================================
# GET ALL KNOWLEDGE GAPS
# ============================================================

def get_knowledge_gaps(
    db: Session
) -> list:
    """
    Return all knowledge gaps.
    """

    gaps = (
        db.query(KnowledgeGap)
        .order_by(
            KnowledgeGap.created_at.desc()
        )
        .all()
    )

    return gaps


# ============================================================
# GET KNOWLEDGE GAP BY ID
# ============================================================

def get_knowledge_gap(
    db: Session,
    gap_id: int
):
    """
    Return a specific knowledge gap.
    """

    gap = (
        db.query(KnowledgeGap)
        .filter(
            KnowledgeGap.id == gap_id
        )
        .first()
    )

    return gap


# ============================================================
# DELETE KNOWLEDGE GAP
# ============================================================

def delete_knowledge_gap(
    db: Session,
    gap_id: int
) -> bool:
    """
    Delete a knowledge gap.
    """

    gap = (
        db.query(KnowledgeGap)
        .filter(
            KnowledgeGap.id == gap_id
        )
        .first()
    )


    if not gap:

        return False


    db.delete(gap)

    db.commit()


    return True


# ============================================================
# COUNT KNOWLEDGE GAPS
# ============================================================

def count_knowledge_gaps(
    db: Session
) -> int:
    """
    Return the total number of knowledge gaps.
    """

    count = (
        db.query(KnowledgeGap)
        .count()
    )

    return count