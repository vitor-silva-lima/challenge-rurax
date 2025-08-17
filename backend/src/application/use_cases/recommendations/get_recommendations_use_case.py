from src.application.services.recommendation_service import (
    RecommendationService
)
from src.application.dtos.movie_dto import (
    MovieListResponseDTO,
    MovieResponseDTO
)
from src.domain.value_objects.recommendation import (
    RecommendationRequest,
    RecommendationAlgorithm
)
from src.domain.entities.movie import Movie
from src.domain.repositories.like_repository import LikeRepository


class GetRecommendationsUseCase:

    def __init__(
        self,
        recommendation_service: RecommendationService,
        like_repository: LikeRepository
    ):
        self.recommendation_service = recommendation_service
        self.like_repository = like_repository

    def execute(
        self,
        user_id: int,
        algorithm: RecommendationAlgorithm = (
            RecommendationAlgorithm.COLLABORATIVE
        ),
        page: int = 1,
        per_page: int = 20
    ) -> MovieListResponseDTO:

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # Create recommendation request
        request = RecommendationRequest(
            user_id=user_id,
            algorithm=algorithm,
            limit=per_page,
            page=page
        )

        # Get recommendations from service
        result = self.recommendation_service.get_recommendations(request)

        # Convert to DTOs
        movie_dtos = [
            self._movie_to_dto(movie, user_id) for movie in result.movies
        ]

        # Calculate pagination info
        total_pages = (result.total + per_page - 1) // per_page

        return MovieListResponseDTO(
            movies=movie_dtos,
            total=result.total,
            page=result.page,
            total_pages=total_pages,
            per_page=result.per_page
        )

    def get_available_algorithms(self) -> dict:

        return self.recommendation_service.get_available_algorithms()

    def _movie_to_dto(self, movie: Movie, user_id: int) -> MovieResponseDTO:
        # Check if user liked this movie
        like = self.like_repository.get_by_user_and_movie(user_id, movie.id)
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
