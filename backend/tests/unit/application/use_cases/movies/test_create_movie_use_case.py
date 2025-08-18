import pytest
from unittest.mock import Mock
from src.application.use_cases.movies.create_movie_use_case\
    import CreateMovieUseCase
from src.application.dtos.movie_dto import MovieCreateDTO
from src.domain.entities.movie import Movie


class TestCreateMovieUseCase:

    def setup_method(self):
        self.movie_repository_mock = Mock()
        self.use_case = CreateMovieUseCase(
            movie_repository=self.movie_repository_mock
        )

    def test_create_movie_success_with_all_fields(self):
        movie_data = MovieCreateDTO(
            title="Test Movie",
            overview="A test movie overview",
            release_date="2023-01-01",
            poster_path="/poster.jpg",
            backdrop_path="/backdrop.jpg",
            genres='["Action", "Drama"]',
            runtime=120,
            original_language="en",
            tmdb_id=12345,
            vote_average=8.5,
            vote_count=100,
            popularity=75.2
        )
        created_movie = Movie(
            id=1,
            title="Test Movie",
            overview="A test movie overview",
            release_date="2023-01-01",
            poster_path="/poster.jpg",
            backdrop_path="/backdrop.jpg",
            genres='["Action", "Drama"]',
            runtime=120,
            original_language="en",
            tmdb_id=12345,
            vote_average=8.5,
            vote_count=100,
            popularity=75.2
        )
        self.movie_repository_mock.save.return_value = created_movie
        result = self.use_case.execute(movie_data)
        assert result == created_movie
        assert result.id == 1
        assert result.title == "Test Movie"
        assert result.overview == "A test movie overview"
        assert result.release_date == "2023-01-01"
        assert result.poster_path == "/poster.jpg"
        assert result.backdrop_path == "/backdrop.jpg"
        assert result.genres == '["Action", "Drama"]'
        assert result.runtime == 120
        assert result.original_language == "en"
        assert result.tmdb_id == 12345
        assert result.vote_average == 8.5
        assert result.vote_count == 100
        assert result.popularity == 75.2
        self.movie_repository_mock.save.assert_called_once()

    def test_create_movie_success_with_minimal_fields(self):
        movie_data = MovieCreateDTO(
            title="Minimal Movie"
        )
        created_movie = Movie(
            id=1,
            title="Minimal Movie",
            overview=None,
            release_date=None,
            poster_path=None,
            backdrop_path=None,
            vote_average=0.0,
            vote_count=0,
            popularity=0.0,
            genres=None,
            runtime=None,
            original_language=None,
            tmdb_id=None
        )
        self.movie_repository_mock.save.return_value = created_movie
        result = self.use_case.execute(movie_data)
        assert result == created_movie
        assert result.id == 1
        assert result.title == "Minimal Movie"
        assert result.overview is None
        assert result.release_date is None
        assert result.poster_path is None
        assert result.backdrop_path is None
        assert result.vote_average == 0.0
        assert result.vote_count == 0
        assert result.popularity == 0.0
        assert result.genres is None
        assert result.runtime is None
        assert result.original_language is None
        assert result.tmdb_id is None
        self.movie_repository_mock.save.assert_called_once()

    def test_create_movie_passed_to_repository_correctly(self):
        movie_data = MovieCreateDTO(
            title="Repository Test Movie",
            overview="Testing repository interaction",
            vote_average=7.5,
            vote_count=50
        )

        def capture_save_argument(movie):
            assert movie.id is None
            assert movie.title == "Repository Test Movie"
            assert movie.overview == "Testing repository interaction"
            assert movie.vote_average == 7.5
            assert movie.vote_count == 50
            assert movie.created_at is not None
            assert movie.updated_at is not None
            movie.id = 1
            return movie

        self.movie_repository_mock.save.side_effect = capture_save_argument
        result = self.use_case.execute(movie_data)
        assert result.id == 1
        assert result.title == "Repository Test Movie"
        assert result.overview == "Testing repository interaction"

    def test_create_movie_with_zero_ratings(self):
        movie_data = MovieCreateDTO(
            title="Zero Rating Movie",
            vote_average=0.0,
            vote_count=0,
            popularity=0.0
        )
        created_movie = Movie(
            id=1,
            title="Zero Rating Movie",
            vote_average=0.0,
            vote_count=0,
            popularity=0.0
        )
        self.movie_repository_mock.save.return_value = created_movie
        result = self.use_case.execute(movie_data)
        assert result.vote_average == 0.0
        assert result.vote_count == 0
        assert result.popularity == 0.0

    def test_create_movie_with_high_ratings(self):
        movie_data = MovieCreateDTO(
            title="High Rating Movie",
            vote_average=9.8,
            vote_count=10000,
            popularity=100.0
        )
        created_movie = Movie(
            id=1,
            title="High Rating Movie",
            vote_average=9.8,
            vote_count=10000,
            popularity=100.0
        )
        self.movie_repository_mock.save.return_value = created_movie
        result = self.use_case.execute(movie_data)
        assert result.vote_average == 9.8
        assert result.vote_count == 10000
        assert result.popularity == 100.0

    @pytest.mark.parametrize("title,vote_average,vote_count", [
        ("Action Movie", 8.0, 150),
        ("Comedy Film", 7.5, 200),
        ("Drama Series", 9.0, 500),
        ("Horror Flick", 6.5, 75),
    ])
    def test_create_movie_with_different_data(
        self,
        title: str,
        vote_average: float,
        vote_count: int
    ):
        movie_data = MovieCreateDTO(
            title=title,
            vote_average=vote_average,
            vote_count=vote_count
        )
        created_movie = Movie(
            id=1,
            title=title,
            vote_average=vote_average,
            vote_count=vote_count
        )
        self.movie_repository_mock.save.return_value = created_movie
        result = self.use_case.execute(movie_data)
        assert result.title == title
        assert result.vote_average == vote_average
        assert result.vote_count == vote_count

    def test_create_movie_with_special_characters_in_title(self):
        movie_data = MovieCreateDTO(
            title="Filme: O Início! (2023) - Edição Especial"
        )
        created_movie = Movie(
            id=1,
            title="Filme: O Início! (2023) - Edição Especial"
        )
        self.movie_repository_mock.save.return_value = created_movie
        result = self.use_case.execute(movie_data)
        assert result.title == "Filme: O Início! (2023) - Edição Especial"

    def test_create_movie_with_long_overview(self):
        long_overview = "Este é um overview muito longo " * 50
        movie_data = MovieCreateDTO(
            title="Long Overview Movie",
            overview=long_overview
        )
        created_movie = Movie(
            id=1,
            title="Long Overview Movie",
            overview=long_overview
        )
        self.movie_repository_mock.save.return_value = created_movie
        result = self.use_case.execute(movie_data)
        assert result.overview == long_overview
        assert len(result.overview) > 1000

    def test_create_movie_repository_error_handling(self):
        movie_data = MovieCreateDTO(
            title="Error Test Movie"
        )
        self.movie_repository_mock.save\
            .side_effect = Exception("Database error")
        with pytest.raises(Exception) as exc_info:
            self.use_case.execute(movie_data)
        assert str(exc_info.value) == "Database error"
        self.movie_repository_mock.save.assert_called_once()

    def test_create_movie_model_dump_integration(self):
        movie_data = MovieCreateDTO(
            title="Model Dump Test",
            overview="Testing model dump",
            vote_average=8.0
        )

        def capture_save_argument(movie):
            assert movie.title == "Model Dump Test"
            assert movie.overview == "Testing model dump"
            assert movie.vote_average == 8.0
            movie.id = 1
            return movie

        self.movie_repository_mock.save.side_effect = capture_save_argument
        result = self.use_case.execute(movie_data)
        assert result.id == 1
        assert result.title == "Model Dump Test"

    def test_create_movie_with_optional_fields_none(self):
        movie_data = MovieCreateDTO(
            title="Optional None Movie",
            overview=None,
            release_date=None,
            poster_path=None,
            backdrop_path=None,
            genres=None,
            runtime=None,
            original_language=None,
            tmdb_id=None
        )
        created_movie = Movie(
            id=1,
            title="Optional None Movie",
            overview=None,
            release_date=None,
            poster_path=None,
            backdrop_path=None,
            genres=None,
            runtime=None,
            original_language=None,
            tmdb_id=None
        )
        self.movie_repository_mock.save.return_value = created_movie
        result = self.use_case.execute(movie_data)
        assert result.title == "Optional None Movie"
        assert result.overview is None
        assert result.release_date is None
        assert result.poster_path is None
        assert result.backdrop_path is None
        assert result.genres is None
        assert result.runtime is None
        assert result.original_language is None
        assert result.tmdb_id is None
