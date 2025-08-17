from src.domain.repositories.movie_repository import MovieRepository
from src.application.dtos.movie_dto import (
    MovieListResponseDTO,
    MovieResponseDTO
)
from src.domain.entities.movie import Movie


class GetPopularMoviesUseCase:

    def __init__(self, movie_repository: MovieRepository):
        self.movie_repository = movie_repository

    def execute(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> MovieListResponseDTO:

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # Get popular movies
        movies, total = self.movie_repository.get_popular(
            page=page,
            per_page=per_page
        )

        # Convert to DTOs
        movie_dtos = [self._movie_to_dto(movie) for movie in movies]

        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page

        return MovieListResponseDTO(
            movies=movie_dtos,
            total=total,
            page=page,
            total_pages=total_pages,
            per_page=per_page
        )

    def _movie_to_dto(self, movie: Movie) -> MovieResponseDTO:
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
            updated_at=movie.updated_at
        )
