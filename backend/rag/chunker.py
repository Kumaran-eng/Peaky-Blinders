from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# TEXT CHUNKER
# ============================================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    length_function=len,
    separators=[
        "\n\n",
        "\n",
        ". ",
        "? ",
        "! ",
        " ",
        ""
    ]
)


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks(pages: list, filename: str) -> list:
    """
    Split extracted document text into smaller chunks.

    Each chunk contains:
    - text
    - source document
    - page number
    """

    chunks = []


    for page in pages:

        text = page.get("text", "").strip()

        page_number = page.get("page")


        # ----------------------------------------------------
        # Skip empty pages
        # ----------------------------------------------------

        if not text:
            continue


        # ----------------------------------------------------
        # Split page text into chunks
        # ----------------------------------------------------

        split_texts = text_splitter.split_text(
            text
        )


        # ----------------------------------------------------
        # Store chunk information
        # ----------------------------------------------------

        for chunk_number, chunk_text in enumerate(
            split_texts
        ):

            chunk_text = chunk_text.strip()


            if not chunk_text:
                continue


            chunks.append({

                "text": chunk_text,

                "source": filename,

                "page": page_number,

                "chunk_number": chunk_number

            })


    return chunks