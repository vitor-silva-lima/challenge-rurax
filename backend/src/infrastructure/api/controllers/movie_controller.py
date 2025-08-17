from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from src.application.use_cases.movies.get_movies_use_case import (
    GetMoviesUseCase
)
from src.application.dtos.movie_dto import MovieListResponseDTO
from src.infrastructure.api.dependencies.movie_dependencies import (
    get_movies_use_case
)

router = APIRouter()


@router.get(
    path="/",
    response_model=MovieListResponseDTO,
    summary="Get movies",
    description="Get paginated list of movies with optional search"
)
def get_movies(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(20, ge=1, le=100, description="Number of movies"),
    search: Optional[str] = Query(None, description="Search query to filter"),
    use_case: GetMoviesUseCase = Depends(get_movies_use_case)
):

    try:
        return use_case.execute(
            page=page,
            per_page=per_page,
            search_query=search
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving movies: {str(e)}"
        )
