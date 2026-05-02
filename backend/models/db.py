from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
from uuid import uuid4

from sqlmodel import Field, Session, SQLModel, create_engine


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BACKEND_DIR / "auto_idea_combiner.db"
DATABASE_URL = os.getenv(
    "AUTO_IDEA_COMBINER_DB_URL",
    f"sqlite:///{DEFAULT_DB_PATH.as_posix()}",
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


class Concept(SQLModel, table=True):
    __tablename__ = "concepts"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    text: str = Field(index=True, sa_column_kwargs={"unique": True})
    source: str = Field(default="unknown")
    embedding_id: str = Field(index=True)
    frequency: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utc_now)


class IdeaCard(SQLModel, table=True):
    __tablename__ = "idea_cards"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str
    concept_a: str
    concept_b: str
    summary: str
    why_interesting: str
    target_user: str
    main_tech: str
    mvp_outline: str
    differentiator: str
    fun_point: str
    risks: str
    novelty_score: float = Field(default=0.0)
    relevance_score: float = Field(default=0.0)
    distance_score: float = Field(default=0.0)
    feasibility_score: float = Field(default=0.0)
    fun_score: float = Field(default=0.0)
    api_fit_score: float = Field(default=0.0)
    total_score: float = Field(default=0.0, index=True)
    detail_level: str = Field(default="standard")
    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    idea_card_id: str = Field(foreign_key="idea_cards.id", index=True)
    rating: str
    created_at: datetime = Field(default_factory=utc_now, index=True)


class ScoreWeights(SQLModel, table=True):
    __tablename__ = "score_weights"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    novelty: float
    relevance: float
    distance: float
    feasibility: float
    fun: float
    api_fit: float
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class AppSettings(SQLModel, table=True):
    __tablename__ = "app_settings"

    id: str = Field(default="default", primary_key=True)
    llm_provider: str = Field(default="anthropic")
    embedding_provider: str = Field(default="local")
    local_scan_dirs_raw: str = Field(default="")
    external_api_enabled: bool = Field(default=True)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
