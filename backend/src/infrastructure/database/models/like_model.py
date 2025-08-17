from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from src.infrastructure.database.connection import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # flake8: noqa: F401
    from src.infrastructure.database.models.user_model import UserModel
    from src.infrastructure.database.models.movie_model import MovieModel


class LikeModel(Base):

    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    user = relationship("UserModel", back_populates="likes")
    movie = relationship("MovieModel", back_populates="likes")

    # Constraint to ensure a user can only like a movie once
    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_like'),
    )
