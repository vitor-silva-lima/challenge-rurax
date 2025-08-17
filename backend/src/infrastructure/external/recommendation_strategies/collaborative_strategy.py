from typing import List, Set, Tuple
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

from src.application.services.recommendation_service import (
    RecommendationStrategy
)
from src.domain.entities.user import User
from src.domain.value_objects.recommendation import RecommendationResult
from src.domain.repositories.like_repository import LikeRepository
from src.domain.repositories.movie_repository import MovieRepository


class CollaborativeFilteringStrategy(RecommendationStrategy):

    def __init__(
        self,
        like_repository: LikeRepository,
        movie_repository: MovieRepository,
        min_common_movies: int = 2,
        max_similar_users: int = 20
    ):
        self.like_repository = like_repository
        self.movie_repository = movie_repository
        self.min_common_movies = min_common_movies
        self.max_similar_users = max_similar_users

    def recommend(
        self,
        user: User,
        limit: int,
        page: int,
    ) -> RecommendationResult:

        # Get user's liked movies
        user_likes, _ = self.like_repository.get_by_user(
            user.id, page=1, per_page=1000
        )
        user_liked_movie_ids = {like.movie_id for like in user_likes}

        # If user has no likes, fall back to popularity
        if not user_liked_movie_ids:
            return self._fallback_to_popularity(limit, page)

        # Get all user-movie interactions
        all_likes = self.like_repository.get_user_movie_matrix()

        if len(all_likes) < self.min_common_movies:
            return self._fallback_to_popularity(limit, page)

        # Build user-item matrix for collaborative filtering
        user_movie_matrix = self._build_user_movie_matrix(all_likes)

        # Find similar users using cosine similarity
        similar_users = self._find_similar_users_sklearn(
            user.id, user_movie_matrix
        )

        # Generate recommendations from similar users
        recommended_movie_ids = self._get_recommendations_from_similar_users(
            user_liked_movie_ids, similar_users, user_movie_matrix
        )

        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_movie_ids = recommended_movie_ids[start_idx:end_idx]

        # Get movie details
        movies = []
        for movie_id in paginated_movie_ids:
            # Convert numpy int64 to Python int if needed
            movie_id_int = int(movie_id)
            movie = self.movie_repository.get_by_id(movie_id_int)
            if movie:
                movies.append(movie)

        total = len(recommended_movie_ids)

        return RecommendationResult(
            movies=movies,
            total=total,
            algorithm_used=self.get_name(),
            page=page,
            per_page=limit
        )

    def _build_user_movie_matrix(
        self,
        all_likes: List[Tuple[int, int]]
    ) -> pd.DataFrame:

        df = pd.DataFrame(all_likes, columns=['user_id', 'movie_id'])
        df['rating'] = 1  # Binary rating (like = 1)

        # Pivot to create user-movie matrix
        user_movie_matrix = df.pivot_table(
            index='user_id',
            columns='movie_id',
            values='rating',
            fill_value=0
        )

        return user_movie_matrix

    def _find_similar_users_sklearn(
        self,
        target_user_id: int,
        user_movie_matrix: pd.DataFrame
    ) -> List[Tuple[int, float]]:

        # Check if target user exists in matrix
        if target_user_id not in user_movie_matrix.index:
            return []

        # Get target user's preferences
        target_user_row = user_movie_matrix.loc[target_user_id].values.reshape(
            1, -1
        )

        # Calculate cosine similarity with all users
        similarities = cosine_similarity(
            target_user_row, user_movie_matrix.values
        )[0]

        # Create list of (user_id, similarity) pairs
        similar_users = []
        for idx, similarity in enumerate(similarities):
            user_id = user_movie_matrix.index[idx]

            # Skip self and users with low similarity
            if user_id != target_user_id and similarity > 0.1:
                similar_users.append((user_id, similarity))

        # Sort by similarity (descending) and limit results
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users[:self.max_similar_users]

    def _get_recommendations_from_similar_users(
        self,
        user_liked_movie_ids: Set[int],
        similar_users: List[Tuple[int, float]],
        user_movie_matrix: pd.DataFrame
    ) -> List[int]:

        movie_scores = defaultdict(float)

        for similar_user_id, similarity_score in similar_users:
            if similar_user_id not in user_movie_matrix.index:
                continue

            # Get movies liked by similar user
            similar_user_likes = user_movie_matrix.loc[similar_user_id]
            liked_movies = similar_user_likes[similar_user_likes == 1]\
                .index.tolist()

            # Score movies not yet liked by target user
            for movie_id in liked_movies:
                movie_id_int = int(movie_id)  # Ensure Python int
                if movie_id_int not in user_liked_movie_ids:
                    movie_scores[movie_id_int] += similarity_score

        # Sort movies by score
        recommended_movies = sorted(
            movie_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [movie_id for movie_id, _ in recommended_movies]

    def _fallback_to_popularity(
        self,
        limit: int,
        page: int
    ) -> RecommendationResult:

        movies, total = self.movie_repository.get_popular(
            page=page,
            per_page=limit
        )

        return RecommendationResult(
            movies=movies,
            total=total,
            algorithm_used=f"{self.get_name()} (fallback to popularity)",
            page=page,
            per_page=limit
        )

    def get_name(self) -> str:
        return "Collaborative Filtering"

    def get_description(self) -> str:
        return (
            "Recommends movies based on users with similar taste using "
            "collaborative filtering with cosine similarity"
        )
