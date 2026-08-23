from .embeddings import create_single_embedding
from .vector_store import load_vectors

from ..config import TOP_K, SIMILARITY_THRESHOLD


NON_EVIDENCE_FILENAME_MARKERS = (
    "test_question",
    "test_set",
    "evaluator",
    "evaluation",
)


def is_evidence_source(source: str) -> bool:
    """Exclude test/evaluation fixtures from user-facing document evidence."""
    return not any(marker in source.lower() for marker in NON_EVIDENCE_FILENAME_MARKERS)


# ============================================================
# RETRIEVE RELEVANT DOCUMENTS
# ============================================================

def retrieve_documents(question: str) -> list:
    """
    Search the FAISS vector database and return
    the most relevant document chunks.

    Args:
        question:
            User's natural-language question.

    Returns:
        List of relevant document chunks with
        similarity scores.
    """

    if not question or not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )


    # ========================================================
    # LOAD FAISS INDEX
    # ========================================================

    try:

        index, metadata = load_vectors()

    except FileNotFoundError:

        # No documents have been indexed yet
        return []

    except Exception as e:

        raise RuntimeError(
            f"Failed to load vector database: {str(e)}"
        )


    # ========================================================
    # CHECK VECTOR DATABASE
    # ========================================================

    if index.ntotal == 0:

        return []


    # ========================================================
    # CREATE QUESTION EMBEDDING
    # ========================================================

    question_embedding = create_single_embedding(
        question
    )


    # ========================================================
    # SEARCH FAISS
    # ========================================================

    scores, indices = index.search(
        question_embedding,
        min(TOP_K * 4, index.ntotal)
    )


    results = []


    # ========================================================
    # PROCESS SEARCH RESULTS
    # ========================================================

    for score, index_number in zip(
        scores[0],
        indices[0]
    ):

        # FAISS can return -1 when no result exists
        if index_number == -1:
            continue


        # Make sure metadata exists
        if index_number >= len(metadata):
            continue


        similarity_score = float(score)


        # ----------------------------------------------------
        # Apply similarity threshold
        # ----------------------------------------------------

        if similarity_score < SIMILARITY_THRESHOLD:
            continue


        # ----------------------------------------------------
        # Get document metadata
        # ----------------------------------------------------

        result = metadata[index_number].copy()

        if not is_evidence_source(str(result.get("source", ""))):
            continue

        result["score"] = similarity_score


        results.append(result)

        if len(results) == TOP_K:
            break


    return results
