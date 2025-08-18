from fastapi import Depends
from sqlalchemy.orm import Session

from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories.movie_repository_impl import (
    MovieRepositoryImpl
)
from src.application.use_cases.movies.import_movies_csv_use_case import (
    ImportMoviesCsvUseCase
)


def get_movie_repository_for_csv(
    db: Session = Depends(get_db)
) -> MovieRepositoryImpl:
    """Get movie repository instance for CSV operations."""
    return MovieRepositoryImpl(db)


def get_import_movies_csv_use_case(
    movie_repository: MovieRepositoryImpl = Depends(
        get_movie_repository_for_csv
    )
) -> ImportMoviesCsvUseCase:
    """Get import movies CSV use case instance."""
    return ImportMoviesCsvUseCase(movie_repository)
