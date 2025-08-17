from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LikeCreateDTO(BaseModel):
    movie_id: int = Field(..., description="Movie ID")


class LikeResponseDTO(BaseModel):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LikeToggleResponseDTO(BaseModel):
    movie_id: int
    is_liked: bool
    like: Optional[LikeResponseDTO] = None
