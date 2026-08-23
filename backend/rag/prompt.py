# ============================================================
# DOC TRUST AI - PROMPT BUILDER
# ============================================================


def build_prompt(question: str, contexts: list) -> str:
    """
    Build a strict document-grounded prompt for the LLM.

    Args:
        question:
            User's question.

        contexts:
            Relevant document chunks retrieved from FAISS.

    Returns:
        A prompt containing the question and retrieved evidence.
    """

    if not question or not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )


    if not contexts:

        return f"""
You are DocTrust AI.

The user asked:

{question}

There is no relevant information available
from the provided documents.

Respond exactly with:

I don't know based on the provided documents.
"""


    # ========================================================
    # FORMAT RETRIEVED DOCUMENT CONTEXT
    # ========================================================

    context_parts = []


    for number, context in enumerate(
        contexts,
        start=1
    ):

        source = context.get(
            "source",
            "Unknown document"
        )

        page = context.get(
            "page"
        )

        text = context.get(
            "text",
            ""
        )


        if page is None:

            page_information = "Page: Not available"

        else:

            page_information = f"Page: {page}"


        context_parts.append(
            f"""
--- SOURCE {number} ---

Document: {source}

{page_information}

Content:
{text}
"""
        )


    context_text = "\n".join(
        context_parts
    )


    # ========================================================
    # STRICT GROUNDED PROMPT
    # ========================================================

    prompt = f"""
You are DocTrust AI, a trustworthy
document-grounded question answering assistant.

Your job is to answer the user's question
using ONLY the information provided in the
DOCUMENT CONTEXT below.

============================================================
STRICT RULES
============================================================

1. Use ONLY the provided document context.

2. Do NOT use your general knowledge.

3. Do NOT use information from the internet.

4. Do NOT make assumptions.

5. Do NOT guess.

6. Do NOT invent facts, names, dates, numbers,
   policies, rules, or other information.

7. If the answer is not clearly supported by
   the provided documents, respond exactly:

   "I don't know based on the provided documents."

8. If only part of the question can be answered,
   answer only the supported part and clearly
   state that the remaining information is not
   available in the provided documents.

9. Keep the answer clear and concise.

10. Do not mention information that is unrelated
    to the user's question.

11. Write a natural, user-friendly answer. Do NOT include
    citations, source names, page numbers, line references,
    footnotes, markdown links, or bracketed markers such as
    [L1-L3]. The application displays verified sources separately.

12. Do not create a source that does not exist.

============================================================
DOCUMENT CONTEXT
============================================================

{context_text}

============================================================
USER QUESTION
============================================================

{question}

============================================================
ANSWER
============================================================

Provide the answer now using ONLY the
document context above.
"""

    return prompt
