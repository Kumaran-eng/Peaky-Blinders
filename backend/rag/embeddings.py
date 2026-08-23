from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from ..config import EMBEDDING_MODEL


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Load the model on first use so the API can start without model I/O."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings(texts: Sequence[str]) -> np.ndarray:
    """
    Convert a list of text chunks into vector embeddings.

    Args:
        texts:
            List of text strings.

    Returns:
        NumPy array containing embeddings.
    """

    if not texts:

        raise ValueError(
            "Cannot create embeddings from empty text."
        )


    embeddings = get_embedding_model().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )


    return np.asarray(embeddings, dtype=np.float32)


# ============================================================
# CREATE SINGLE EMBEDDING
# ============================================================

def create_single_embedding(text: str) -> np.ndarray:
    """
    Convert a single text string into an embedding.
    """

    if not text or not text.strip():

        raise ValueError(
            "Text cannot be empty."
        )


    embedding = get_embedding_model().encode(
        [text],
        normalize_embeddings=True,
        show_progress_bar=False
    )


    return np.asarray(embedding, dtype=np.float32)
