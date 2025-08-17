from fastapi import Depends
from sqlalchemy.orm import Session

from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories\
    .user_repository_impl import UserRepositoryImpl
from src.infrastructure.database.repositories\
    .like_repository_impl import LikeRepositoryImpl
from src.infrastructure.external\
    .recommendation_service_impl import RecommendationServiceImpl
from src.application.use_cases.recommendations\
    .get_recommendations_use_case import GetRecommendationsUseCase
from src.domain.value_objects.recommendation import RecommendationAlgorithm


def get_user_repository_for_recommendations(
    db: Session = Depends(get_db)
) -> UserRepositoryImpl:
    """Get user repository instance for recommendations."""
    return UserRepositoryImpl(db)


def get_recommendation_service(
    db: Session = Depends(get_db),
    user_repository: UserRepositoryImpl = (
        Depends(get_user_repository_for_recommendations)
    )
) -> RecommendationServiceImpl:
    """Get recommendation service instance."""
    return RecommendationServiceImpl(
        db_session=db,
        user_repository=user_repository,
        default_algorithm=RecommendationAlgorithm.COLLABORATIVE
    )


def get_like_repository_for_recommendations(
    db: Session = Depends(get_db)
) -> LikeRepositoryImpl:
    """Get like repository instance for recommendations."""
    return LikeRepositoryImpl(db)


def get_recommendations_use_case(
    recommendation_service: RecommendationServiceImpl = (
        Depends(get_recommendation_service)
    ),
    like_repository: LikeRepositoryImpl = (
        Depends(get_like_repository_for_recommendations)
    )
) -> GetRecommendationsUseCase:
    """Get enhanced recommendations use case instance."""
    return GetRecommendationsUseCase(recommendation_service, like_repository)
