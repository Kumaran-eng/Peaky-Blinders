from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List


# ============================================================
# CHAT SCHEMAS
# ============================================================

class ChatRequest(BaseModel):
    """
    Data received when a user asks a question.
    """

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question"
    )

    @field_validator("question")
    @classmethod
    def question_must_not_be_whitespace(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question cannot be empty.")
        return value


class SourceResponse(BaseModel):
    """
    Source information used to generate an answer.
    """

    document: str

    page: Optional[int] = None

    score: float


class ChatResponse(BaseModel):
    """
    Response returned by the chatbot.
    """

    answer: str

    sources: List[SourceResponse] = []

    answered: bool = True


class AdminLoginRequest(BaseModel):
    """Password submitted from the admin sign-in form."""

    password: str = Field(..., min_length=1, max_length=256)


# ============================================================
# DOCUMENT SCHEMAS
# ============================================================

class DocumentResponse(BaseModel):
    """
    Information about an uploaded document.
    """

    id: int

    filename: str

    file_type: str

    status: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# KNOWLEDGE GAP SCHEMAS
# ============================================================

class KnowledgeGapResponse(BaseModel):
    """
    Question that the system could not answer
    from the provided documents.
    """

    id: int

    question: str

    reason: Optional[str] = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# FEEDBACK SCHEMAS
# ============================================================

class FeedbackRequest(BaseModel):
    """
    User feedback for an AI answer.
    """

    question_id: int

    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating from 1 to 5"
    )

    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    """
    Response after storing feedback.
    """

    message: str

    success: bool


# ============================================================
# ANALYTICS SCHEMAS
# ============================================================

class AnalyticsResponse(BaseModel):
    """
    Statistics displayed on the admin dashboard.
    """

    total_documents: int

    total_questions: int

    answered_questions: int

    unanswered_questions: int

    total_knowledge_gaps: int

    average_rating: float
