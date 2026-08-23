import os
from pathlib import Path

import fitz
from docx import Document as DocxDocument


# ============================================================
# PDF LOADER
# ============================================================

def load_pdf(file_path: str) -> list:
    """
    Extract text from a PDF file page by page.

    Returns:
        [
            {
                "text": "...",
                "page": 1
            },
            ...
        ]
    """

    pages = []

    try:
        document = fitz.open(file_path)

        for page_number, page in enumerate(document):

            text = page.get_text("text").strip()

            if text:

                pages.append({
                    "text": text,
                    "page": page_number + 1
                })

        document.close()

    except Exception as e:

        raise RuntimeError(
            f"Failed to read PDF: {str(e)}"
        )

    return pages


# ============================================================
# DOCX LOADER
# ============================================================

def load_docx(file_path: str) -> list:
    """
    Extract text from a DOCX file.

    DOCX does not have reliable page information
    using simple python-docx extraction, so page
    is returned as None.
    """

    try:

        document = DocxDocument(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        full_text = "\n".join(paragraphs)

    except Exception as e:

        raise RuntimeError(
            f"Failed to read DOCX: {str(e)}"
        )

    if not full_text.strip():

        return []

    return [
        {
            "text": full_text,
            "page": None
        }
    ]


# ============================================================
# TXT LOADER
# ============================================================

def load_txt(file_path: str) -> list:
    """
    Extract text from a TXT file.
    """

    try:

        text = Path(file_path).read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        # Try another common encoding
        try:

            text = Path(file_path).read_text(
                encoding="latin-1"
            )

        except Exception as e:

            raise RuntimeError(
                f"Failed to read TXT file: {str(e)}"
            )

    except Exception as e:

        raise RuntimeError(
            f"Failed to read TXT file: {str(e)}"
        )

    text = text.strip()

    if not text:
        return []

    return [
        {
            "text": text,
            "page": None
        }
    ]


# ============================================================
# MAIN DOCUMENT LOADER
# ============================================================

def load_document(file_path: str) -> list:
    """
    Automatically detect the document type and
    extract its text.

    Supported:
        PDF
        DOCX
        TXT
    """

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = Path(
        file_path
    ).suffix.lower()


    if extension == ".pdf":

        return load_pdf(file_path)


    elif extension == ".docx":

        return load_docx(file_path)


    elif extension == ".txt":

        return load_txt(file_path)


    else:

        raise ValueError(
            f"Unsupported file type: {extension}. "
            "Supported formats are PDF, DOCX and TXT."
        )