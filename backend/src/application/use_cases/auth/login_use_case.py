from src.domain.repositories.user_repository import UserRepository
from src.application.dtos.user_dto import UserLoginDTO, TokenDTO
from src.application.services.security_service import SecurityService
from src.shared.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    UserInactiveException
)


class LoginUserUseCase:

    def __init__(
        self,
        user_repository: UserRepository,
        security_service: SecurityService
    ):
        self.user_repository = user_repository
        self.security_service = security_service

    def execute(self, login_data: UserLoginDTO) -> TokenDTO:

        user = self.user_repository.get_by_username_or_email(
            login_data.username)

        if not user:
            raise InvalidCredentialsException("Invalid credentials")

        if not self.security_service.verify_password(
            login_data.password,
            user.hashed_password,
        ):
            raise InvalidCredentialsException("Invalid credentials")

        if not user.is_active:
            raise UserInactiveException("User inactive")

        access_token = self.security_service.create_access_token(str(user.id))

        return TokenDTO(access_token=access_token)
