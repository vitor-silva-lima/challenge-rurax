from src.domain.entities.movie import Movie
from src.domain.repositories.movie_repository import MovieRepository
from src.domain.repositories.like_repository import LikeRepository
from src.application.dtos.movie_dto import (
    MovieListResponseDTO,
    MovieResponseDTO
)
from typing import Optional


class GetMoviesUseCase:

    def __init__(
        self,
        movie_repository: MovieRepository,
        like_repository: LikeRepository
    ):
        self.movie_repository = movie_repository
        self.like_repository = like_repository

    def execute(
        self,
        user_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
        search_query: str = None
    ) -> MovieListResponseDTO:

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # Get movies based on search query
        if search_query and search_query.strip():
            movies, total = self.movie_repository.search(
                query=search_query.strip(),
                page=page,
                per_page=per_page
            )
        else:
            movies, total = self.movie_repository.get_all(
                page=page,
                per_page=per_page
            )

        # Convert to DTOs
        movie_dtos = [self._movie_to_dto(movie, user_id) for movie in movies]

        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page

        return MovieListResponseDTO(
            movies=movie_dtos,
            total=total,
            page=page,
            total_pages=total_pages,
            per_page=per_page
        )

    def _movie_to_dto(
        self, movie: Movie, user_id: Optional[int] = None
    ) -> MovieResponseDTO:
        # Check if user liked this movie
        is_liked = None
        if user_id is not None:
            like = self.like_repository.get_by_user_and_movie(
                user_id, movie.id
            )
            is_liked = like is not None
        return MovieResponseDTO(
            id=movie.id,
            tmdb_id=movie.tmdb_id,
            title=movie.title,
            overview=movie.overview,
            release_date=movie.release_date,
            poster_path=movie.poster_path,
            backdrop_path=movie.backdrop_path,
            vote_average=movie.vote_average,
            vote_count=movie.vote_count,
            popularity=movie.popularity,
            genres=movie.get_genres_list(),
            runtime=movie.runtime,
            original_language=movie.original_language,
            year=movie.get_year(),
            created_at=movie.created_at,
            updated_at=movie.updated_at,
            is_liked=is_liked
        )
