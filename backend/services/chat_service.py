from sqlalchemy.orm import Session

from ..rag.retriever import retrieve_documents
from ..rag.prompt import build_prompt
from ..rag.answer_generator import generate_answer
from .knowledge_gap_service import save_knowledge_gap


UNKNOWN_ANSWER = "I don't know based on the provided documents."


# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(
    question: str,
    db: Session = None
) -> dict:
    """
    Complete RAG question-answering pipeline.

    Flow:

    User Question
        ↓
    FAISS Retrieval
        ↓
    Similarity Check
        ↓
    Grounded Prompt
        ↓
    Groq
        ↓
    Answer + Sources
    """

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question or not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )

    question = question.strip()


    # --------------------------------------------------------
    # Retrieve relevant documents
    # --------------------------------------------------------

    contexts = retrieve_documents(
        question
    )


    # --------------------------------------------------------
    # No relevant documents found
    # --------------------------------------------------------

    if not contexts:

        return _unknown_response(db, question, "No relevant document evidence was found.")


    # --------------------------------------------------------
    # Get best similarity score
    # --------------------------------------------------------

    best_score = max(
        context.get("score", 0.0)
        for context in contexts
    )


    # --------------------------------------------------------
    # Build grounded prompt
    # --------------------------------------------------------

    prompt = build_prompt(
        question=question,
        contexts=contexts
    )


    # --------------------------------------------------------
    # Generate answer using Groq
    # --------------------------------------------------------

    answer = generate_answer(
        prompt
    )


    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if not answer or answer.strip().lower().startswith(UNKNOWN_ANSWER.lower()):
        return _unknown_response(db, question, "The retrieved evidence did not support an answer.", best_score)

    answered = True


    # --------------------------------------------------------
    # Prepare source information
    # --------------------------------------------------------

    sources = []

    for context in contexts:

        source = {

            "document": context.get(
                "source",
                "Unknown"
            ),

            "page": context.get(
                "page"
            ),

            "score": round(
                float(
                    context.get(
                        "score",
                        0.0
                    )
                ),
                4
            )

        }

        sources.append(
            source
        )


    # --------------------------------------------------------
    # Save question to database
    # --------------------------------------------------------

    if db is not None:

        _save_question(
            db=db,
            question=question,
            answer=answer,
            answered=1 if answered else 0,
            confidence=f"{best_score:.2f}"
        )


    # --------------------------------------------------------
    # Return final response
    # --------------------------------------------------------

    return {

        "answer": answer,

        "sources": sources,

        "answered": answered

    }


# ============================================================
# SAVE QUESTION
# ============================================================

def _save_question(
    db: Session,
    question: str,
    answer: str,
    answered: int,
    confidence: str
):
    """
    Save a question and answer to the database.
    """

    from ..models import Question

    question_record = Question(

        question=question,

        answer=answer,

        answered=answered,

        confidence=confidence

    )

    db.add(
        question_record
    )

    db.commit()

    db.refresh(
        question_record
    )


def _unknown_response(
    db: Session | None,
    question: str,
    reason: str,
    confidence: float = 0.0,
) -> dict:
    """Persist unanswered questions and their deduplicated knowledge-gap record."""
    if db is not None:
        _save_question(db, question, UNKNOWN_ANSWER, 0, f"{confidence:.2f}")
        save_knowledge_gap(db, question, reason)
    return {"answer": UNKNOWN_ANSWER, "sources": [], "answered": False}
