from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.application.use_cases.auth.register_use_case import (
    RegisterUserUseCase
)
from src.application.use_cases.auth.login_use_case import LoginUserUseCase
from src.application.dtos.user_dto import (
    UserCreateDTO,
    UserResponseDTO,
    UserLoginDTO,
    TokenDTO
)
from src.infrastructure.api.dependencies.auth_dependencies import (
    get_register_user_use_case,
    get_login_user_use_case
)
from src.shared.exceptions.auth_exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    InvalidCredentialsException,
    UserInactiveException
)

router = APIRouter()


@router.post(
    path="/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreateDTO,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    try:
        user = use_case.execute(user_data)
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except (EmailAlreadyExistsException, UsernameAlreadyExistsException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    path="/login",
    response_model=TokenDTO
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUserUseCase = Depends(get_login_user_use_case)
):
    try:
        login_dto = UserLoginDTO(
            username=form_data.username,
            password=form_data.password)
        return use_case.execute(login_dto)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserInactiveException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )


@router.post(
    path="/login-json",
    response_model=TokenDTO
)
def login_json(
    login_data: UserLoginDTO,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case)
):
    try:
        return use_case.execute(login_data)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except UserInactiveException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
