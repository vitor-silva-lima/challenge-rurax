from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from src.infrastructure.database.connection import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # flake8: noqa: F401
    from src.infrastructure.database.models.like_model import LikeModel


class MovieModel(Base):

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True, nullable=True)
    title = Column(String, nullable=False, index=True)
    overview = Column(Text, nullable=True)
    release_date = Column(String, nullable=True)
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    popularity = Column(Float, default=0.0)
    genres = Column(String, nullable=True)
    runtime = Column(Integer, nullable=True)
    original_language = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    likes = relationship(
        "LikeModel",
        back_populates="movie",
        cascade="all, delete-orphan"
    )

    @property
    def like_count(self) -> int:
        return len(self.likes)
