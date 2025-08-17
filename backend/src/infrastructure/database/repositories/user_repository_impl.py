from typing import Optional

from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        if user.id is None:
            # Create new user
            user_model = UserModel(
                email=user.email,
                username=user.username,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            self.db.add(user_model)
            self.db.commit()
            self.db.refresh(user_model)

            # Convert back to entity
            return self._model_to_entity(user_model)
        else:
            # Update existing user
            user_model = self.db.query(UserModel)\
                .filter(UserModel.id == user.id)\
                .first()
            if user_model:
                user_model.email = user.email
                user_model.username = user.username
                user_model.hashed_password = user.hashed_password
                user_model.is_active = user.is_active
                user_model.updated_at = user.updated_at

                self.db.commit()
                self.db.refresh(user_model)

                return self._model_to_entity(user_model)

            raise ValueError(f"User with ID {user.id} not found")

    def get_by_id(self, user_id: int) -> Optional[User]:
        user_model = self.db.query(UserModel)\
            .filter(UserModel.id == user_id)\
            .first()
        return self._model_to_entity(user_model) if user_model else None

    def get_by_email(self, email: str) -> Optional[User]:
        user_model = self.db.query(UserModel)\
            .filter(UserModel.email == email)\
            .first()
        return self._model_to_entity(user_model) if user_model else None

    def get_by_username(self, username: str) -> Optional[User]:
        user_model = self.db.query(UserModel)\
            .filter(UserModel.username == username)\
            .first()
        return self._model_to_entity(user_model) if user_model else None

    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        user_model = self.db.query(UserModel)\
            .filter(
                (UserModel.username == identifier) |
                (UserModel.email == identifier)
            )\
            .first()
        return self._model_to_entity(user_model) if user_model else None

    def delete(self, user_id: int) -> bool:
        user_model = self.db.query(UserModel)\
            .filter(UserModel.id == user_id)\
            .first()
        if user_model:
            self.db.delete(user_model)
            self.db.commit()
            return True
        return False

    def _model_to_entity(self, user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            email=user_model.email,
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )
