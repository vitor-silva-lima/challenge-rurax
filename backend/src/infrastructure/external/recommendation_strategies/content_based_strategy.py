from typing import List, Dict, Set
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import json

from src.application.services.recommendation_service import (
    RecommendationStrategy
)
from src.domain.entities.user import User
from src.domain.value_objects.recommendation import RecommendationResult
from src.domain.repositories.like_repository import LikeRepository
from src.domain.repositories.movie_repository import MovieRepository


class ContentBasedStrategy(RecommendationStrategy):

    def __init__(
        self,
        like_repository: LikeRepository,
        movie_repository: MovieRepository,
        similarity_threshold: float = 0.1,
        max_recommendations: int = 100
    ):
        self.like_repository = like_repository
        self.movie_repository = movie_repository
        self.similarity_threshold = similarity_threshold
        self.max_recommendations = max_recommendations

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
        liked_movie_ids = {like.movie_id for like in user_likes}

        # If user has no likes, fall back to popularity
        if not liked_movie_ids:
            return self._fallback_to_popularity(limit, page)

        # Get all movies for similarity calculation
        all_movies, _ = self.movie_repository.get_all(page=1, per_page=10000)

        if len(all_movies) < 2:
            return self._fallback_to_popularity(limit, page)

        # Get liked movies details
        liked_movies = [
            movie for movie in all_movies
            if movie.id in liked_movie_ids
        ]

        # Calculate movie similarities
        movie_similarities = self._calculate_movie_similarities(
            all_movies, liked_movies
        )

        # Generate recommendations based on similar movies
        recommended_movie_ids = self._generate_content_recommendations(
            movie_similarities, liked_movie_ids
        )

        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_movie_ids = recommended_movie_ids[start_idx:end_idx]

        # Get movie details
        movies = []
        for movie_id in paginated_movie_ids:
            # Convert numpy int64 to Python int
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

    def _calculate_movie_similarities(
        self,
        all_movies: List,
        liked_movies: List
    ) -> Dict[int, float]:

        # Create feature vectors for all movies
        movie_features = self._create_movie_features(all_movies)

        if movie_features.empty:
            return {}

        # Create TF-IDF vectors
        tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )

        try:
            tfidf_matrix = tfidf.fit_transform(movie_features['features'])
        except ValueError:
            # Fallback if TF-IDF fails
            return self._calculate_genre_similarity(
                all_movies, liked_movies
            )

        # Calculate similarities between liked movies and all movies
        movie_similarities = {}
        liked_movie_ids_set = {m.id for m in liked_movies}
        liked_indices = [
            idx for idx, movie_id in enumerate(movie_features['movie_id'])
            if int(movie_id) in liked_movie_ids_set
        ]

        for liked_idx in liked_indices:
            # Calculate cosine similarity between
            # this liked movie and all others
            similarities = cosine_similarity(
                tfidf_matrix[liked_idx:liked_idx+1],
                tfidf_matrix
            )[0]

            for idx, similarity in enumerate(similarities):
                movie_id = int(movie_features['movie_id'].iloc[idx])
                # Accumulate similarity scores
                if movie_id not in movie_similarities:
                    movie_similarities[movie_id] = 0
                movie_similarities[movie_id] += similarity

        # Normalize by number of liked movies
        if liked_indices:
            for movie_id in movie_similarities:
                movie_similarities[movie_id] /= len(liked_indices)

        return movie_similarities

    def _create_movie_features(self, movies: List) -> pd.DataFrame:

        movie_data = []

        for movie in movies:
            # Combine genres, title, and overview for features
            genres = []
            if movie.genres:
                try:
                    genres = json.loads(movie.genres)
                except (json.JSONDecodeError, TypeError):
                    genres = []

            # Create feature string
            feature_parts = []

            # Add genres (with higher weight by repeating)
            feature_parts.extend(genres * 3)  # Repeat genres 3 times

            # Add title words
            if movie.title:
                title_words = movie.title.lower().split()
                feature_parts.extend(title_words * 2)  # Repeat title 2 times

            # Add overview words
            if movie.overview:
                overview_words = movie.overview.lower().split()
                feature_parts.extend(overview_words)

            # Add original language
            if movie.original_language:
                feature_parts.append(f"lang_{movie.original_language}")

            features = ' '.join(feature_parts)

            movie_data.append({
                'movie_id': int(movie.id),  # Ensure Python int
                'features': features
            })

        return pd.DataFrame(movie_data)

    def _calculate_genre_similarity(
        self,
        all_movies: List,
        liked_movies: List
    ) -> Dict[int, float]:

        # Extract genres from liked movies
        liked_genres = Counter()
        for movie in liked_movies:
            if movie.genres:
                try:
                    genres = json.loads(movie.genres)
                    liked_genres.update(genres)
                except (json.JSONDecodeError, TypeError):
                    continue

        # Calculate similarity for all movies
        movie_similarities = {}
        for movie in all_movies:
            movie_id = int(movie.id)  # Ensure Python int
            if movie.genres:
                try:
                    movie_genres = set(json.loads(movie.genres))
                    # Calculate Jaccard similarity with liked genres
                    common_genres = len(
                        movie_genres.intersection(liked_genres.keys())
                    )
                    total_genres = len(
                        movie_genres.union(liked_genres.keys())
                    )
                    if total_genres > 0:
                        similarity = common_genres / total_genres
                        movie_similarities[movie_id] = similarity
                except (json.JSONDecodeError, TypeError):
                    movie_similarities[movie_id] = 0
            else:
                movie_similarities[movie_id] = 0

        return movie_similarities

    def _generate_content_recommendations(
        self,
        movie_similarities: Dict[int, float],
        liked_movie_ids: Set[int]
    ) -> List[int]:

        # Filter out already liked movies and low similarity scores
        recommendations = []
        for movie_id, similarity in movie_similarities.items():
            if (
                movie_id not in liked_movie_ids
                and similarity > self.similarity_threshold
            ):
                recommendations.append((movie_id, similarity))

        # Sort by similarity score (descending)
        recommendations.sort(key=lambda x: x[1], reverse=True)

        # Return top recommendations (max_recommendations)
        return [
            movie_id for movie_id, _
            in recommendations[:self.max_recommendations]
        ]

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
        return "Content-Based Filtering"

    def get_description(self) -> str:
        return (
            "Recommends movies similar to those you've already liked "
            "based on genres, title, and overview using TF-IDF and "
            "cosine similarity"
        )
