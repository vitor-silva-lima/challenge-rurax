from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreateDTO(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email",
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username",
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Password",
    )


class UserResponseDTO(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLoginDTO(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


@dataclass
class UserUpdatePasswordDTO:
    user_id: int
    current_password: str
    new_password: str
