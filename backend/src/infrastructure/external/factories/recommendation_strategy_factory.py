from typing import Dict
from sqlalchemy.orm import Session

from src.application.services.recommendation_service import (
    RecommendationStrategy
)
from src.domain.value_objects.recommendation import RecommendationAlgorithm
from src.infrastructure.external.recommendation_strategies import (
    PopularityRecommendationStrategy,
    CollaborativeFilteringStrategy,
    ContentBasedStrategy
)
from src.infrastructure.database.repositories.like_repository_impl import (
    LikeRepositoryImpl
)
from src.infrastructure.database.repositories.movie_repository_impl import (
    MovieRepositoryImpl
)


class RecommendationStrategyFactory:

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.like_repository = LikeRepositoryImpl(db_session)
        self.movie_repository = MovieRepositoryImpl(db_session)

    def create_strategy(
        self,
        algorithm: RecommendationAlgorithm
    ) -> RecommendationStrategy:

        strategy_map = {
            RecommendationAlgorithm.POPULARITY: (
                self._create_popularity_strategy
            ),
            RecommendationAlgorithm.COLLABORATIVE: (
                self._create_collaborative_strategy
            ),
            RecommendationAlgorithm.CONTENT_BASED: (
                self._create_content_based_strategy
            ),
        }

        strategy_creator = strategy_map.get(algorithm)
        if not strategy_creator:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        return strategy_creator()

    def get_all_strategies(
        self
    ) -> Dict[RecommendationAlgorithm, RecommendationStrategy]:

        return {
            algorithm: self.create_strategy(algorithm)
            for algorithm in RecommendationAlgorithm
        }

    def _create_popularity_strategy(self) -> PopularityRecommendationStrategy:
        """Create popularity-based recommendation strategy."""
        return PopularityRecommendationStrategy(
            movie_repository=self.movie_repository
        )

    def _create_collaborative_strategy(self) -> CollaborativeFilteringStrategy:
        """Create collaborative filtering recommendation strategy."""
        return CollaborativeFilteringStrategy(
            like_repository=self.like_repository,
            movie_repository=self.movie_repository,
            min_common_movies=2,
            max_similar_users=20
        )

    def _create_content_based_strategy(self) -> ContentBasedStrategy:
        """Create content-based recommendation strategy."""
        return ContentBasedStrategy(
            like_repository=self.like_repository,
            movie_repository=self.movie_repository,
            similarity_threshold=0.1,
            max_recommendations=100
        )
