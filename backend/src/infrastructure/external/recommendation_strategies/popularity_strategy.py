from src.application.services.recommendation_service import (
    RecommendationStrategy
)
from src.domain.entities.user import User
from src.domain.value_objects.recommendation import RecommendationResult
from src.domain.repositories.movie_repository import MovieRepository


class PopularityRecommendationStrategy(RecommendationStrategy):

    def __init__(self, movie_repository: MovieRepository):
        self.movie_repository = movie_repository

    def recommend(
        self,
        user: User,
        limit: int,
        page: int,
    ) -> RecommendationResult:

        # Get popular movies using repository
        movies, total = self.movie_repository.get_popular(
            page=page,
            per_page=limit
        )

        return RecommendationResult(
            movies=movies,
            total=total,
            algorithm_used=self.get_name(),
            page=page,
            per_page=limit
        )

    def get_name(self) -> str:
        return "Popularity-Based"

    def get_description(self) -> str:
        return (
            "Recommends movies based on overall popularity "
            "(number of likes from all users)"
        )
