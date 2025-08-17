"""Database models package."""

from .movie_model import MovieModel
from .user_model import UserModel
from .like_model import LikeModel

__all__ = ["MovieModel", "UserModel", "LikeModel"]
