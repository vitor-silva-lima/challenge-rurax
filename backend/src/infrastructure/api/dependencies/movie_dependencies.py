from fastapi import Depends
from sqlalchemy.orm import Session

from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories\
    .movie_repository_impl import MovieRepositoryImpl
from src.infrastructure.database.repositories\
    .like_repository_impl import LikeRepositoryImpl
from src.application.use_cases.movies\
    .get_movies_use_case import GetMoviesUseCase
from src.application.use_cases.movies\
    .get_popular_movies_use_case import GetPopularMoviesUseCase
from src.application.use_cases.likes\
    .like_movie_use_case import LikeMovieUseCase
from src.application.use_cases.recommendations\
    .get_recommendations_use_case import GetRecommendationsUseCase


def get_movie_repository(db: Session = Depends(get_db)) -> MovieRepositoryImpl:
    """Get movie repository instance."""
    return MovieRepositoryImpl(db)


def get_like_repository(db: Session = Depends(get_db)) -> LikeRepositoryImpl:
    """Get like repository instance."""
    return LikeRepositoryImpl(db)


def get_movies_use_case(
    movie_repository: MovieRepositoryImpl = Depends(get_movie_repository),
    like_repository: LikeRepositoryImpl = Depends(get_like_repository)
) -> GetMoviesUseCase:
    """Get movies use case instance."""
    return GetMoviesUseCase(movie_repository, like_repository)


def get_popular_movies_use_case(
    movie_repository: MovieRepositoryImpl = Depends(get_movie_repository)
) -> GetPopularMoviesUseCase:
    """Get popular movies use case instance."""
    return GetPopularMoviesUseCase(movie_repository)


def get_like_movie_use_case(
    like_repository: LikeRepositoryImpl = Depends(get_like_repository),
    movie_repository: MovieRepositoryImpl = Depends(get_movie_repository)
) -> LikeMovieUseCase:
    """Get like movie use case instance."""
    return LikeMovieUseCase(like_repository, movie_repository)


def get_recommendations_use_case(
    like_repository: LikeRepositoryImpl = Depends(get_like_repository),
    movie_repository: MovieRepositoryImpl = Depends(get_movie_repository)
) -> GetRecommendationsUseCase:
    """Get recommendations use case instance."""
    return GetRecommendationsUseCase(like_repository, movie_repository)
