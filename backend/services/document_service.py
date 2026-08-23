import os

from ..rag.document_loader import load_document
from ..rag.chunker import create_chunks
from ..rag.embeddings import create_embeddings
from ..rag.vector_store import add_vectors


# ============================================================
# PROCESS DOCUMENT
# ============================================================

def process_document(file_path: str) -> dict:
    """
    Process an uploaded document and add it to the
    FAISS vector database.

    Pipeline:

    Document
        ↓
    Text Extraction
        ↓
    Chunking
        ↓
    Embeddings
        ↓
    FAISS Vector Database
    """

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not file_path:

        raise ValueError(
            "File path cannot be empty."
        )


    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )


    # --------------------------------------------------------
    # Get filename
    # --------------------------------------------------------

    filename = os.path.basename(
        file_path
    )


    # --------------------------------------------------------
    # STEP 1: Extract text
    # --------------------------------------------------------

    pages = load_document(
        file_path
    )


    if not pages:

        raise ValueError(
            "No readable text was found in the document."
        )


    # --------------------------------------------------------
    # STEP 2: Create chunks
    # --------------------------------------------------------

    chunks = create_chunks(
        pages=pages,
        filename=filename
    )


    if not chunks:

        raise ValueError(
            "No text chunks could be created from the document."
        )


    # --------------------------------------------------------
    # STEP 3: Extract chunk text
    # --------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]


    # --------------------------------------------------------
    # STEP 4: Generate embeddings
    # --------------------------------------------------------

    embeddings = create_embeddings(
        texts
    )


    # --------------------------------------------------------
    # STEP 5: Add vectors to FAISS
    # --------------------------------------------------------

    vector_result = add_vectors(
        chunks=chunks,
        embeddings=embeddings
    )


    # --------------------------------------------------------
    # Return processing information
    # --------------------------------------------------------

    return {

        "filename": filename,

        "pages": len(pages),

        "chunks": len(chunks),

        "vectors": vector_result[
            "total_vectors"
        ],

        "status": "indexed"

    }