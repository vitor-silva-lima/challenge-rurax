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
        similarity_threshold: float = 0.05,  # Reduzido para ser mais inclusivo
        max_recommendations: int = 100,
        min_recommendations: int = 10  # Garantir um mínimo de recomendações
    ):
        self.like_repository = like_repository
        self.movie_repository = movie_repository
        self.similarity_threshold = similarity_threshold
        self.max_recommendations = max_recommendations
        self.min_recommendations = min_recommendations

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

        # Calcular similaridade máxima ao invés de média
        # Isso ajuda quando usuário tem gostos diversos
        for idx, movie_id in enumerate(movie_features['movie_id']):
            movie_id = int(movie_id)
            if movie_id not in liked_movie_ids_set:
                max_similarity = 0

                for liked_idx in liked_indices:
                    similarity = cosine_similarity(
                        tfidf_matrix[liked_idx:liked_idx+1],
                        tfidf_matrix[idx:idx+1]
                    )[0][0]
                    max_similarity = max(max_similarity, similarity)

                movie_similarities[movie_id] = max_similarity

        # Se a similaridade TF-IDF for muito baixa para todos os filmes,
        # combinar com similaridade de gêneros para aumentar diversidade
        if movie_similarities and max(movie_similarities.values()) < 0.1:
            genre_similarities = self._calculate_genre_similarity(
                all_movies, liked_movies
            )

            # Combinar as duas abordagens (70% TF-IDF, 30% gêneros)
            for movie_id in movie_similarities:
                if movie_id in genre_similarities:
                    combined_score = (
                        0.7 * movie_similarities[movie_id] +
                        0.3 * genre_similarities[movie_id]
                    )
                    movie_similarities[movie_id] = combined_score

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

        # Extract genres from liked movies with weights
        liked_genres = Counter()
        for movie in liked_movies:
            if movie.genres:
                try:
                    genres = json.loads(movie.genres)
                    liked_genres.update(genres)
                except (json.JSONDecodeError, TypeError):
                    continue

        if not liked_genres:
            return {}

        # Calculate similarity for all movies
        movie_similarities = {}
        total_liked_genres = sum(liked_genres.values())

        for movie in all_movies:
            movie_id = int(movie.id)  # Ensure Python int
            similarity = 0

            if movie.genres:
                try:
                    movie_genres = set(json.loads(movie.genres))

                    # Calcular similaridade baseada na freq dos gêneros
                    # Quanto mais um gênero foi curtido, maior o peso
                    for genre in movie_genres:
                        if genre in liked_genres:
                            # Peso do gênero baseado na frequência
                            weight = liked_genres[genre] / total_liked_genres
                            similarity += weight

                    # Normalizar pela quantidade de gêneros do filme
                    # para não penalizar filmes com muitos gêneros
                    if movie_genres:
                        similarity = similarity / len(movie_genres)

                    # Bonus para filmes com pelo menos um gênero comum
                    if similarity > 0:
                        similarity = min(1.0, similarity * 1.2)

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

        # Filter out already liked movies
        candidates = []
        for movie_id, similarity in movie_similarities.items():
            if movie_id not in liked_movie_ids:
                candidates.append((movie_id, similarity))

        # Sort by similarity score (descending)
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Estratégia adaptativa: se não temos recomendações suficientes
        # com o threshold padrão, reduzimos gradualmente
        recommendations = []
        current_threshold = self.similarity_threshold

        while (len(recommendations) < self.min_recommendations
               and current_threshold > 0.01
               and candidates):

            recommendations = [
                movie_id for movie_id, similarity in candidates
                if similarity > current_threshold
            ]

            if len(recommendations) < self.min_recommendations:
                current_threshold *= 0.5  # Reduz threshold pela metade

        # Se ainda não temos recomendações suficientes,
        # pegamos as melhores disponíveis
        if (len(recommendations) < self.min_recommendations
                and candidates):
            recommendations = [movie_id for movie_id, _ in candidates]

        # Return top recommendations (max_recommendations)
        return recommendations[:self.max_recommendations]

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
            "cosine similarity. Adaptively adjusts similarity thresholds "
            "to handle diverse user preferences and ensures minimum "
            "recommendation counts."
        )
