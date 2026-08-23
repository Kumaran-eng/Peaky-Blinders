"""Groq answer generation for retrieved, document-grounded context."""

import re

from groq import Groq

from ..config import GROQ_API_KEY, GROQ_MODEL


def generate_answer(prompt: str) -> str:
    """Generate a concise answer using Groq only after evidence has been retrieved."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured on the server.")
    if not GROQ_MODEL:
        raise RuntimeError("GROQ_MODEL is not configured on the server.")
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Use only supplied document context. Never use outside knowledge, "
                        "guess, or invent facts or citations."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=700,
        )
    except Exception as exc:
        raise RuntimeError("Groq answer generation failed.") from exc

    answer = clean_answer(response.choices[0].message.content or "")
    return answer or "I don't know based on the provided documents."


def clean_answer(answer: str) -> str:
    """Remove model citation decorations; verified sources are returned separately."""
    answer = re.sub(
        r"\s*[【\[][^】\]]*(?:†\s*L\d+|L\d+\s*[-–]\s*L?\d+)[^】\]]*[】\]]",
        "",
        answer,
    )
    return answer.replace("**", "").strip()
