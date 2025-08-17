from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.application.dtos.user_dto import UserCreateDTO
from src.application.services.security_service import SecurityService
from src.shared.exceptions.auth_exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)


class RegisterUserUseCase:

    def __init__(
        self,
        user_repository: UserRepository,
        security_service: SecurityService
    ):
        self.user_repository = user_repository
        self.security_service = security_service

    def execute(self, user_data: UserCreateDTO) -> User:
        if self.user_repository.get_by_email(user_data.email):
            raise EmailAlreadyExistsException("Email already exists")

        if self.user_repository.get_by_username(user_data.username):
            raise UsernameAlreadyExistsException(
                "Username already exists"
            )

        hashed_password = self.security_service.hash_password(
            user_data.password)
        user = User(
            id=None,
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )

        return self.user_repository.save(user)
