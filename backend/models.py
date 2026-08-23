from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from .database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    file_type = Column(String)

    status = Column(String, default="processing")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Question(Base):

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)

    question = Column(Text, nullable=False)

    answer = Column(Text)

    answered = Column(Integer, default=0)

    confidence = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class KnowledgeGap(Base):

    __tablename__ = "knowledge_gaps"

    id = Column(Integer, primary_key=True)

    question = Column(Text, nullable=False)

    reason = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Feedback(Base):

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)

    question_id = Column(Integer)

    rating = Column(Integer)

    comment = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )