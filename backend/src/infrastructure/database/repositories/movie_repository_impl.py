from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from src.domain.entities.movie import Movie
from src.domain.repositories.movie_repository import MovieRepository
from src.infrastructure.database.models.movie_model import MovieModel
from src.infrastructure.database.models.like_model import LikeModel


class MovieRepositoryImpl(MovieRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, movie: Movie) -> Movie:
        if movie.id is None:
            # Create new movie
            movie_model = MovieModel(
                tmdb_id=movie.tmdb_id,
                title=movie.title,
                overview=movie.overview,
                release_date=movie.release_date,
                poster_path=movie.poster_path,
                backdrop_path=movie.backdrop_path,
                vote_average=movie.vote_average,
                vote_count=movie.vote_count,
                popularity=movie.popularity,
                genres=movie.genres,
                runtime=movie.runtime,
                original_language=movie.original_language,
                created_at=movie.created_at,
                updated_at=movie.updated_at
            )
            self.db.add(movie_model)
            self.db.commit()
            self.db.refresh(movie_model)

            return self._model_to_entity(movie_model)
        else:
            # Update existing movie
            movie_model = self.db.query(MovieModel)\
                .filter(MovieModel.id == movie.id)\
                .first()
            if movie_model:
                movie_model.tmdb_id = movie.tmdb_id
                movie_model.title = movie.title
                movie_model.overview = movie.overview
                movie_model.release_date = movie.release_date
                movie_model.poster_path = movie.poster_path
                movie_model.backdrop_path = movie.backdrop_path
                movie_model.vote_average = movie.vote_average
                movie_model.vote_count = movie.vote_count
                movie_model.popularity = movie.popularity
                movie_model.genres = movie.genres
                movie_model.runtime = movie.runtime
                movie_model.original_language = movie.original_language
                movie_model.updated_at = movie.updated_at

                self.db.commit()
                self.db.refresh(movie_model)

                return self._model_to_entity(movie_model)

            raise ValueError(f"Movie with ID {movie.id} not found")

    def save_many(self, movies: List[Movie]) -> int:
        """Save multiple movies and return count of saved movies."""
        movie_models = []
        for movie in movies:
            # Check if movie already exists by tmdb_id
            existing = None
            if movie.tmdb_id:
                existing = self.db.query(MovieModel)\
                    .filter(MovieModel.tmdb_id == movie.tmdb_id)\
                    .first()

            if not existing:
                movie_model = MovieModel(
                    tmdb_id=movie.tmdb_id,
                    title=movie.title,
                    overview=movie.overview,
                    release_date=movie.release_date,
                    poster_path=movie.poster_path,
                    backdrop_path=movie.backdrop_path,
                    vote_average=movie.vote_average,
                    vote_count=movie.vote_count,
                    popularity=movie.popularity,
                    genres=movie.genres,
                    runtime=movie.runtime,
                    original_language=movie.original_language,
                    created_at=movie.created_at,
                    updated_at=movie.updated_at
                )
                movie_models.append(movie_model)

        if movie_models:
            self.db.add_all(movie_models)
            self.db.commit()

        return len(movie_models)

    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        movie_model = self.db.query(MovieModel)\
            .filter(MovieModel.id == movie_id)\
            .first()
        return self._model_to_entity(movie_model) if movie_model else None

    def get_by_tmdb_id(self, tmdb_id: int) -> Optional[Movie]:
        movie_model = self.db.query(MovieModel)\
            .filter(MovieModel.tmdb_id == tmdb_id)\
            .first()
        return self._model_to_entity(movie_model) if movie_model else None

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Movie], int]:
        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count
        total = self.db.query(MovieModel).count()

        # Get movies for current page
        movie_models = self.db.query(MovieModel)\
            .order_by(desc(MovieModel.created_at))\
            .offset(offset)\
            .limit(per_page)\
            .all()

        movies = [self._model_to_entity(model) for model in movie_models]
        return movies, total

    def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Movie], int]:
        # Calculate offset
        offset = (page - 1) * per_page

        # Create search filter
        search_filter = MovieModel.title.ilike(f"%{query}%")

        # Get total count
        total = self.db.query(MovieModel)\
            .filter(search_filter)\
            .count()

        # Get movies for current page
        movie_models = self.db.query(MovieModel)\
            .filter(search_filter)\
            .order_by(desc(MovieModel.popularity))\
            .offset(offset)\
            .limit(per_page)\
            .all()

        movies = [self._model_to_entity(model) for model in movie_models]
        return movies, total

    def get_popular(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Movie], int]:
        """Get movies ordered by number of likes (popularity among users)."""
        # Calculate offset
        offset = (page - 1) * per_page

        # Query movies with like count
        query = self.db.query(
            MovieModel,
            func.count(LikeModel.id).label('like_count')
        )\
            .outerjoin(LikeModel)\
            .group_by(MovieModel.id)\
            .order_by(desc('like_count'), desc(MovieModel.vote_average))

        # Get total count
        total = query.count()

        # Get movies for current page
        results = query.offset(offset).limit(per_page).all()

        movies = [self._model_to_entity(result[0]) for result in results]
        return movies, total

    def delete(self, movie_id: int) -> bool:
        movie_model = self.db.query(MovieModel)\
            .filter(MovieModel.id == movie_id)\
            .first()
        if movie_model:
            self.db.delete(movie_model)
            self.db.commit()
            return True
        return False

    def _model_to_entity(self, movie_model: MovieModel) -> Movie:
        return Movie(
            id=movie_model.id,
            tmdb_id=movie_model.tmdb_id,
            title=movie_model.title,
            overview=movie_model.overview,
            release_date=movie_model.release_date,
            poster_path=movie_model.poster_path,
            backdrop_path=movie_model.backdrop_path,
            vote_average=movie_model.vote_average,
            vote_count=movie_model.vote_count,
            popularity=movie_model.popularity,
            genres=movie_model.genres,
            runtime=movie_model.runtime,
            original_language=movie_model.original_language,
            created_at=movie_model.created_at,
            updated_at=movie_model.updated_at
        )
