from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.likes.like_movie_use_case import (
    LikeMovieUseCase
)
from src.application.dtos.like_dto import (
    LikeCreateDTO,
    LikeToggleResponseDTO
)
from src.infrastructure.api.dependencies.movie_dependencies import (
    get_like_movie_use_case
)
from src.infrastructure.api.dependencies\
    .auth_dependencies import get_current_user
from src.domain.entities.user import User
from src.shared.exceptions.movie_exceptions import (
    MovieNotFoundException
)
from src.shared.exceptions.like_exceptions import (
    LikeAlreadyExistsException
)

router = APIRouter()


@router.post(
    path="/toggle",
    response_model=LikeToggleResponseDTO,
    summary="Toggle like on movie",
    description="Like or unlike a movie. If already liked, removes "
    "the like. If not liked, adds a like."
)
def toggle_like(
    like_data: LikeCreateDTO,
    current_user: User = Depends(get_current_user),
    use_case: LikeMovieUseCase = Depends(get_like_movie_use_case)
):

    try:
        return use_case.execute(
            user_id=current_user.id,
            like_data=like_data
        )
    except MovieNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {like_data.movie_id} not found"
        )
    except LikeAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing like: {str(e)}"
        )
