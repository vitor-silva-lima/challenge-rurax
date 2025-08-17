from src.domain.entities.like import Like
from src.domain.repositories.like_repository import LikeRepository
from src.domain.repositories.movie_repository import MovieRepository
from src.application.dtos.like_dto import (
    LikeCreateDTO,
    LikeToggleResponseDTO,
    LikeResponseDTO
)
from src.shared.exceptions.movie_exceptions import (
    MovieNotFoundException
)


class LikeMovieUseCase:

    def __init__(
        self,
        like_repository: LikeRepository,
        movie_repository: MovieRepository
    ):
        self.like_repository = like_repository
        self.movie_repository = movie_repository

    def execute(
        self,
        user_id: int,
        like_data: LikeCreateDTO
    ) -> LikeToggleResponseDTO:

        # Verify movie exists
        movie = self.movie_repository.get_by_id(like_data.movie_id)
        if not movie:
            raise MovieNotFoundException(
                f"Movie with ID {like_data.movie_id} not found"
            )

        # Check if user already liked this movie
        existing_like = self.like_repository.get_by_user_and_movie(
            user_id=user_id,
            movie_id=like_data.movie_id
        )

        if existing_like:
            # User already liked this movie, so remove the like (unlike)
            self.like_repository.delete(existing_like.id)
            return LikeToggleResponseDTO(
                movie_id=like_data.movie_id,
                is_liked=False,
                like=None
            )
        else:
            # User hasn't liked this movie, so add a like
            like = Like(
                id=None,
                user_id=user_id,
                movie_id=like_data.movie_id
            )

            saved_like = self.like_repository.save(like)

            like_dto = LikeResponseDTO(
                id=saved_like.id,
                user_id=saved_like.user_id,
                movie_id=saved_like.movie_id,
                created_at=saved_like.created_at
            )

            return LikeToggleResponseDTO(
                movie_id=like_data.movie_id,
                is_liked=True,
                like=like_dto
            )
