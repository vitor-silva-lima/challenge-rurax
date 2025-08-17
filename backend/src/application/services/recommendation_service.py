from abc import ABC, abstractmethod
from typing import Dict

from src.domain.entities.user import User
from src.domain.value_objects.recommendation import (
    RecommendationRequest,
    RecommendationResult,
    RecommendationAlgorithm
)


class RecommendationStrategy(ABC):
    """Abstract base class for recommendation strategies."""

    @abstractmethod
    def recommend(
        self,
        user: User,
        limit: int,
        page: int,
    ) -> RecommendationResult:
        """
        Generate recommendations for a user.

        Args:
            user: User to generate recommendations for
            limit: Number of recommendations per page
            page: Page number (1-based)

        Returns:
            RecommendationResult with recommended movies
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the strategy name."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get the strategy description."""
        pass


class RecommendationService(ABC):
    """Abstract base class for recommendation service."""

    @abstractmethod
    def register_strategy(
        self,
        algorithm: RecommendationAlgorithm,
        strategy: RecommendationStrategy,
    ):
        """Register a recommendation strategy."""
        pass

    @abstractmethod
    def get_recommendations(
        self, request: RecommendationRequest
    ) -> RecommendationResult:
        """Generate recommendations using the specified strategy."""
        pass

    @abstractmethod
    def get_available_algorithms(self) -> Dict[str, Dict[str, str]]:
        """Get information about available algorithms."""
        pass
