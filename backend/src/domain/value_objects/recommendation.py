from dataclasses import dataclass
from enum import Enum
from typing import List

from src.domain.entities.movie import Movie


class RecommendationAlgorithm(str, Enum):
    POPULARITY = "popularity"
    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"


@dataclass(frozen=True)
class RecommendationRequest:
    user_id: int
    algorithm: RecommendationAlgorithm
    limit: int = 10
    page: int = 1


@dataclass(frozen=True)
class RecommendationResult:
    movies: List[Movie]
    total: int
    algorithm_used: str
    page: int
    per_page: int
