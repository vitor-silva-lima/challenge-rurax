from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.application.use_cases.auth.register_use_case import (
    RegisterUserUseCase
)
from src.application.use_cases.auth.login_use_case import LoginUserUseCase
from src.domain.entities.user import User
from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl
)
from src.infrastructure.external.security_service_impl import (
    SecurityServiceImpl
)

# Security scheme para JWT
security = HTTPBearer()


def get_security_service() -> SecurityServiceImpl:
    return SecurityServiceImpl()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryImpl:
    return UserRepositoryImpl(db)


def get_register_user_use_case(
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
    security_service: SecurityServiceImpl = Depends(get_security_service)
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repository, security_service)


def get_login_user_use_case(
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
    security_service: SecurityServiceImpl = Depends(get_security_service)
) -> LoginUserUseCase:
    return LoginUserUseCase(user_repository, security_service)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
    security_service: SecurityServiceImpl = Depends(get_security_service)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token
    token = credentials.credentials
    user_id = security_service.verify_token(token)

    if user_id is None:
        raise credentials_exception

    # Get user from database
    user = user_repository.get_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
