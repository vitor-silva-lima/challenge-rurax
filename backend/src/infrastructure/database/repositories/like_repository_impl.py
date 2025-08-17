from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.domain.entities.like import Like
from src.domain.repositories.like_repository import LikeRepository
from src.infrastructure.database.models.like_model import LikeModel


class LikeRepositoryImpl(LikeRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, like: Like) -> Like:
        if like.id is None:
            # Create new like
            like_model = LikeModel(
                user_id=like.user_id,
                movie_id=like.movie_id,
                created_at=like.created_at
            )
            self.db.add(like_model)
            self.db.commit()
            self.db.refresh(like_model)

            return self._model_to_entity(like_model)
        else:
            # Update existing like (though usually likes don't get updated)
            like_model = self.db.query(LikeModel)\
                .filter(LikeModel.id == like.id)\
                .first()
            if like_model:
                like_model.user_id = like.user_id
                like_model.movie_id = like.movie_id
                like_model.created_at = like.created_at

                self.db.commit()
                self.db.refresh(like_model)

                return self._model_to_entity(like_model)

            raise ValueError(f"Like with ID {like.id} not found")

    def get_by_user_and_movie(
        self, user_id: int, movie_id: int
    ) -> Optional[Like]:
        like_model = self.db.query(LikeModel)\
            .filter(
                LikeModel.user_id == user_id,
                LikeModel.movie_id == movie_id
            )\
            .first()
        return self._model_to_entity(like_model) if like_model else None

    def get_by_user(
        self, user_id: int, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Like], int]:
        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count
        total = self.db.query(LikeModel)\
            .filter(LikeModel.user_id == user_id)\
            .count()

        # Get likes for current page
        like_models = self.db.query(LikeModel)\
            .filter(LikeModel.user_id == user_id)\
            .order_by(desc(LikeModel.created_at))\
            .offset(offset)\
            .limit(per_page)\
            .all()

        likes = [self._model_to_entity(model) for model in like_models]
        return likes, total

    def get_user_movie_matrix(self) -> List[Tuple[int, int]]:
        """Get all user-movie like combinations for recommendation engine."""
        results = self.db.query(LikeModel.user_id, LikeModel.movie_id).all()
        return [(result.user_id, result.movie_id) for result in results]

    def delete(self, like_id: int) -> bool:
        like_model = self.db.query(LikeModel)\
            .filter(LikeModel.id == like_id)\
            .first()
        if like_model:
            self.db.delete(like_model)
            self.db.commit()
            return True
        return False

    def delete_by_user_and_movie(self, user_id: int, movie_id: int) -> bool:
        like_model = self.db.query(LikeModel)\
            .filter(
                LikeModel.user_id == user_id,
                LikeModel.movie_id == movie_id
            )\
            .first()
        if like_model:
            self.db.delete(like_model)
            self.db.commit()
            return True
        return False

    def _model_to_entity(self, like_model: LikeModel) -> Like:
        return Like(
            id=like_model.id,
            user_id=like_model.user_id,
            movie_id=like_model.movie_id,
            created_at=like_model.created_at
        )
