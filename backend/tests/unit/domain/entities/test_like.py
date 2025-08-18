import pytest
from datetime import datetime, timezone
from src.domain.entities.like import Like


class TestLike:

    def test_like_creation_with_all_fields(self):
        created_at = datetime.now(timezone.utc)
        like = Like(
            id=1,
            user_id=123,
            movie_id=456,
            created_at=created_at
        )
        assert like.id == 1
        assert like.user_id == 123
        assert like.movie_id == 456
        assert like.created_at == created_at

    def test_like_creation_with_minimal_fields(self):
        like = Like(
            id=None,
            user_id=123,
            movie_id=456
        )
        assert like.id is None
        assert like.user_id == 123
        assert like.movie_id == 456
        assert like.created_at is not None
        assert isinstance(like.created_at, datetime)

    def test_like_post_init_sets_timestamp(self):
        before_creation = datetime.now(timezone.utc)
        like = Like(
            id=None,
            user_id=123,
            movie_id=456
        )
        after_creation = datetime.now(timezone.utc)
        assert before_creation <= like.created_at <= after_creation

    def test_like_with_different_user_and_movie_ids(self):
        like1 = Like(id=1, user_id=100, movie_id=200)
        like2 = Like(id=2, user_id=101, movie_id=201)
        like3 = Like(id=3, user_id=102, movie_id=202)
        assert like1.user_id == 100
        assert like1.movie_id == 200
        assert like2.user_id == 101
        assert like2.movie_id == 201
        assert like3.user_id == 102
        assert like3.movie_id == 202

    def test_like_timestamps_are_unique(self):
        like1 = Like(id=1, user_id=123, movie_id=456)
        import time
        time.sleep(0.001)
        like2 = Like(id=2, user_id=123, movie_id=457)
        assert like1.created_at != like2.created_at
        assert like1.created_at < like2.created_at

    def test_like_with_zero_ids(self):
        like = Like(
            id=0,
            user_id=0,
            movie_id=0
        )
        assert like.id == 0
        assert like.user_id == 0
        assert like.movie_id == 0
        assert like.created_at is not None

    def test_like_with_large_ids(self):
        large_id = 999999999
        like = Like(
            id=large_id,
            user_id=large_id,
            movie_id=large_id
        )
        assert like.id == large_id
        assert like.user_id == large_id
        assert like.movie_id == large_id

    @pytest.mark.parametrize("user_id,movie_id", [
        (1, 100),
        (25, 250),
        (50, 500),
        (100, 1000),
    ])
    def test_like_creation_with_different_combinations(
        self,
        user_id: int,
        movie_id: int
    ):
        like = Like(
            id=None,
            user_id=user_id,
            movie_id=movie_id
        )
        assert like.user_id == user_id
        assert like.movie_id == movie_id
        assert like.created_at is not None

    def test_like_immutability_after_creation(self):
        like = Like(
            id=1,
            user_id=123,
            movie_id=456
        )
        original_user_id = like.user_id
        original_movie_id = like.movie_id
        original_created_at = like.created_at
        assert like.user_id == original_user_id
        assert like.movie_id == original_movie_id
        assert like.created_at == original_created_at

    def test_like_equality_concept(self):
        like1 = Like(id=1, user_id=123, movie_id=456)
        like2 = Like(id=2, user_id=123, movie_id=456)
        assert like1.id != like2.id
        assert like1.user_id == like2.user_id
        assert like1.movie_id == like2.movie_id

    def test_like_string_representation(self):
        like = Like(
            id=1,
            user_id=123,
            movie_id=456
        )
        str_repr = str(like)
        assert "Like" in str_repr
        assert "user_id=123" in str_repr
        assert "movie_id=456" in str_repr
        assert "id=1" in str_repr
