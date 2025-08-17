from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class MovieCreateDTO(BaseModel):
    title: str = Field(
        ...,
        description="Movie title"
    )
    overview: Optional[str] = Field(
        None,
        description="Movie overview",
    )
    release_date: Optional[str] = Field(
        None,
        description="Release date (YYYY-MM-DD)",
    )
    poster_path: Optional[str] = Field(
        None,
        description="Poster path",
    )
    backdrop_path: Optional[str] = Field(
        None,
        description="Backdrop path",
    )
    genres: Optional[str] = Field(
        None,
        description="Genres (JSON)",
    )
    runtime: Optional[int] = Field(
        None,
        description="Runtime in minutes",
    )
    original_language: Optional[str] = Field(
        None,
        description="Original language",
    )
    tmdb_id: Optional[int] = Field(
        None,
        description="TMDB ID",
    )
    vote_average: Optional[float] = Field(
        0.0,
        description="Average vote",
    )
    vote_count: Optional[int] = Field(
        0,
        description="Number of votes",
    )
    popularity: Optional[float] = Field(
        0.0,
        description="Popularity",
    )


class MovieResponseDTO(BaseModel):
    id: int
    title: str
    overview: Optional[str]
    release_date: Optional[str]
    poster_path: Optional[str]
    backdrop_path: Optional[str]
    vote_average: float
    vote_count: int
    popularity: float
    genres: List[str] = Field(default_factory=list, description="Movie genres")
    runtime: Optional[int]
    original_language: Optional[str]
    tmdb_id: Optional[int]
    year: Optional[str] = Field(None, description="Release year")
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MovieListResponseDTO(BaseModel):
    movies: List[MovieResponseDTO]
    total: int
    page: int
    total_pages: int
    per_page: int
