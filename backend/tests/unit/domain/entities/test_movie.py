import pytest
import json
from datetime import datetime, timezone
from src.domain.entities.movie import Movie


class TestMovie:

    def test_movie_creation_with_all_fields(self):
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        movie = Movie(
            id=1,
            title="Test Movie",
            overview="A test movie overview",
            release_date="2023-01-01",
            poster_path="/poster.jpg",
            backdrop_path="/backdrop.jpg",
            vote_average=8.5,
            vote_count=100,
            popularity=75.2,
            genres='["Action", "Drama"]',
            runtime=120,
            original_language="en",
            tmdb_id=12345,
            created_at=created_at,
            updated_at=updated_at
        )
        assert movie.id == 1
        assert movie.title == "Test Movie"
        assert movie.overview == "A test movie overview"
        assert movie.release_date == "2023-01-01"
        assert movie.poster_path == "/poster.jpg"
        assert movie.backdrop_path == "/backdrop.jpg"
        assert movie.vote_average == 8.5
        assert movie.vote_count == 100
        assert movie.popularity == 75.2
        assert movie.genres == '["Action", "Drama"]'
        assert movie.runtime == 120
        assert movie.original_language == "en"
        assert movie.tmdb_id == 12345
        assert movie.created_at == created_at
        assert movie.updated_at == updated_at

    def test_movie_creation_with_minimal_fields(self):
        movie = Movie(
            id=None,
            title="Minimal Movie"
        )
        assert movie.id is None
        assert movie.title == "Minimal Movie"
        assert movie.overview is None
        assert movie.release_date is None
        assert movie.poster_path is None
        assert movie.backdrop_path is None
        assert movie.vote_average == 0.0
        assert movie.vote_count == 0
        assert movie.popularity == 0.0
        assert movie.genres is None
        assert movie.runtime is None
        assert movie.original_language is None
        assert movie.tmdb_id is None
        assert movie.created_at is not None
        assert movie.updated_at is not None

    def test_movie_post_init_sets_timestamps(self):
        before_creation = datetime.now(timezone.utc)
        movie = Movie(
            id=None,
            title="Test Movie"
        )
        after_creation = datetime.now(timezone.utc)
        assert before_creation <= movie.created_at <= after_creation
        assert before_creation <= movie.updated_at <= after_creation

    def test_get_genres_list_with_valid_json(self):
        movie = Movie(
            id=1,
            title="Test Movie",
            genres='["Action", "Drama", "Thriller"]'
        )
        genres_list = movie.get_genres_list()
        assert genres_list == ["Action", "Drama", "Thriller"]
        assert isinstance(genres_list, list)

    def test_get_genres_list_with_empty_genres(self):
        movie_none = Movie(id=1, title="Test Movie", genres=None)
        movie_empty = Movie(id=2, title="Test Movie 2", genres="")
        assert movie_none.get_genres_list() == []
        assert movie_empty.get_genres_list() == []

    def test_get_genres_list_with_invalid_json(self):
        movie = Movie(
            id=1,
            title="Test Movie",
            genres='invalid json string'
        )
        genres_list = movie.get_genres_list()
        assert genres_list == []

    def test_set_genres_list(self):
        movie = Movie(id=1, title="Test Movie")
        old_updated_at = movie.updated_at
        genres = ["Comedy", "Romance"]
        import time
        time.sleep(0.001)
        movie.set_genres_list(genres)
        assert movie.genres == json.dumps(genres)
        assert movie.get_genres_list() == genres
        assert movie.updated_at > old_updated_at

    def test_update_rating(self):
        movie = Movie(
            id=1,
            title="Test Movie",
            vote_average=7.0,
            vote_count=50
        )
        old_updated_at = movie.updated_at
        import time
        time.sleep(0.001)
        movie.update_rating(8.5, 150)
        assert movie.vote_average == 8.5
        assert movie.vote_count == 150
        assert movie.updated_at > old_updated_at

    def test_get_year_with_valid_release_date(self):
        movie = Movie(
            id=1,
            title="Test Movie",
            release_date="2023-05-15"
        )
        year = movie.get_year()
        assert year == "2023"

    def test_get_year_with_short_release_date(self):
        movie = Movie(
            id=1,
            title="Test Movie",
            release_date="202"
        )
        year = movie.get_year()
        assert year is None

    def test_get_year_with_no_release_date(self):
        movie = Movie(
            id=1,
            title="Test Movie",
            release_date=None
        )
        year = movie.get_year()
        assert year is None

    def test_get_year_with_empty_release_date(self):
        movie = Movie(
            id=1,
            title="Test Movie",
            release_date=""
        )
        year = movie.get_year()
        assert year is None

    @pytest.mark.parametrize(
        "vote_average,vote_count,expected_avg,expected_count", [
            (8.5, 100, 8.5, 100),
            (7.2, 250, 7.2, 250),
            (9.0, 500, 9.0, 500),
            (0.0, 0, 0.0, 0),
        ])
    def test_update_rating_with_different_values(
        self,
        vote_average: float,
        vote_count: int,
        expected_avg: float,
        expected_count: int
    ):
        movie = Movie(id=1, title="Test Movie")
        movie.update_rating(vote_average, vote_count)
        assert movie.vote_average == expected_avg
        assert movie.vote_count == expected_count

    def test_movie_defaults(self):
        movie = Movie(id=None, title="Test Movie")
        assert movie.vote_average == 0.0
        assert movie.vote_count == 0
        assert movie.popularity == 0.0
        assert movie.created_at is not None
        assert movie.updated_at is not None

    def test_complex_genres_operations(self):
        movie = Movie(id=1, title="Test Movie")
        initial_genres = ["Action", "Adventure"]
        movie.set_genres_list(initial_genres)
        assert movie.get_genres_list() == initial_genres
        new_genres = ["Action", "Adventure", "Sci-Fi"]
        movie.set_genres_list(new_genres)
        assert movie.get_genres_list() == new_genres
        movie.set_genres_list([])
        assert movie.get_genres_list() == []
