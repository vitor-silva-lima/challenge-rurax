from src.domain.entities.movie import Movie
from src.domain.repositories.movie_repository import MovieRepository
from src.shared.exceptions.movie_exceptions import MovieNotFoundException


class GetMovieByIdUseCase:

    def __init__(self, movie_repository: MovieRepository):
        self.movie_repository = movie_repository

    def execute(self, movie_id: int) -> Movie:

        movie = self.movie_repository.get_by_id(movie_id)

        if not movie:
            raise MovieNotFoundException(f"Movie with ID {movie_id} not found")

        return movie
