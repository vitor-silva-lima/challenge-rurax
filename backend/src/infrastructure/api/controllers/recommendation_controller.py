from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from src.application.use_cases.recommendations\
    .get_recommendations_use_case import GetRecommendationsUseCase
from src.application.dtos.movie_dto import MovieListResponseDTO
from src.domain.value_objects.recommendation import (
    RecommendationAlgorithm
)
from src.infrastructure.api.dependencies.recommendation_dependencies import (
    get_recommendations_use_case
)
from src.infrastructure.api.dependencies\
    .auth_dependencies import get_current_user
from src.domain.entities.user import User

router = APIRouter()


@router.get(
    path="/",
    response_model=MovieListResponseDTO,
    summary="Get movie recommendations",
    description="Get personalized movie recommendations using "
    "different algorithms"
)
def get_recommendations(
    algorithm: Optional[RecommendationAlgorithm] = Query(
        RecommendationAlgorithm.COLLABORATIVE,
        description="Recommendation algorithm to use"
    ),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(
        20, ge=1, le=100, description="Number of movies per page"
    ),
    current_user: User = Depends(get_current_user),
    use_case: GetRecommendationsUseCase = Depends(get_recommendations_use_case)
):
    try:
        return use_case.execute(
            user_id=current_user.id,
            algorithm=algorithm,
            page=page,
            per_page=per_page
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get(
    path="/algorithms",
    summary="Get available algorithms",
    description="Get information about available recommendation algorithms"
)
def get_available_algorithms(
    use_case: GetRecommendationsUseCase = Depends(get_recommendations_use_case)
):

    try:
        return use_case.get_available_algorithms()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving algorithms: {str(e)}"
        )
