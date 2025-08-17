from typing import Dict
from sqlalchemy.orm import Session

from src.application.services.recommendation_service import (
    RecommendationService,
    RecommendationStrategy
)
from src.domain.value_objects.recommendation import (
    RecommendationRequest,
    RecommendationResult,
    RecommendationAlgorithm
)
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.external.factories\
    .recommendation_strategy_factory import RecommendationStrategyFactory


class RecommendationServiceImpl(RecommendationService):

    def __init__(
        self,
        db_session: Session,
        user_repository: UserRepository,
        default_algorithm: RecommendationAlgorithm = (
            RecommendationAlgorithm.CONTENT_BASED
        )
    ):
        self.db_session = db_session
        self.user_repository = user_repository
        self.strategy_factory = RecommendationStrategyFactory(db_session)
        self._strategies: Dict[
            RecommendationAlgorithm, RecommendationStrategy
        ] = {}
        self._default_algorithm = default_algorithm

        # Initialize all strategies
        self._initialize_strategies()

    def _initialize_strategies(self):
        """Initialize all available recommendation strategies."""
        self._strategies = self.strategy_factory.get_all_strategies()

    def register_strategy(
        self,
        algorithm: RecommendationAlgorithm,
        strategy: RecommendationStrategy,
    ):

        self._strategies[algorithm] = strategy

    def get_recommendations(
        self, request: RecommendationRequest
    ) -> RecommendationResult:

        # Get the requested strategy
        strategy = self._strategies.get(request.algorithm)

        if not strategy:
            # Fallback to default strategy
            strategy = self._strategies.get(self._default_algorithm)

        if not strategy:
            raise ValueError("No recommendation strategy available")

        # Get user entity
        user = self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError(f"User with ID {request.user_id} not found")

        # Generate recommendations using the strategy
        return strategy.recommend(user, request.limit, request.page)

    def get_available_algorithms(self) -> Dict[str, Dict[str, str]]:

        return {
            algorithm.value: {
                "name": strategy.get_name(),
                "description": strategy.get_description()
            }
            for algorithm, strategy in self._strategies.items()
        }

    def set_default_algorithm(self, algorithm: RecommendationAlgorithm):

        if algorithm not in self._strategies:
            raise ValueError(f"Algorithm {algorithm} is not available")
        self._default_algorithm = algorithm

    def get_strategy(
        self,
        algorithm: RecommendationAlgorithm
    ) -> RecommendationStrategy:

        strategy = self._strategies.get(algorithm)
        if not strategy:
            raise ValueError(f"Strategy for {algorithm} is not available")
        return strategy
