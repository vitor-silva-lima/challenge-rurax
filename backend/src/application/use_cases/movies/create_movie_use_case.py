from src.domain.entities.movie import Movie
from src.domain.repositories.movie_repository import MovieRepository
from src.application.dtos.movie_dto import MovieCreateDTO


class CreateMovieUseCase:

    def __init__(self, movie_repository: MovieRepository):
        self.movie_repository = movie_repository

    def execute(self, movie_data: MovieCreateDTO) -> Movie:
        movie = Movie(
            id=None,
            **movie_data.model_dump()
        )

        return self.movie_repository.save(movie)
