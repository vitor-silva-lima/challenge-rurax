from typing import Optional, List
from pydantic import BaseModel, Field, validator
import json


class MovieCsvRowDTO(BaseModel):
    """DTO to validate a line of the CSV file."""

    title: str = Field(..., description="Movie title (required)")
    overview: Optional[str] = Field(None, description="Movie overview")
    release_date: Optional[str] = Field(
        None, description="Release date (YYYY-MM-DD)"
    )
    poster_path: Optional[str] = Field(None, description="Poster path")
    backdrop_path: Optional[str] = Field(None, description="Backdrop path")
    vote_average: Optional[float] = Field(
        0.0, description="Average vote", ge=0.0, le=10.0
    )
    vote_count: Optional[int] = Field(
        0, description="Number of votes", ge=0
    )
    popularity: Optional[float] = Field(
        0.0, description="Popularity", ge=0.0
    )
    genres: Optional[str] = Field(None, description="Genres (JSON array)")
    runtime: Optional[int] = Field(
        None, description="Runtime in minutes", ge=0
    )
    original_language: Optional[str] = Field(
        None, description="Original language"
    )
    tmdb_id: Optional[int] = Field(None, description="TMDB ID", ge=0)

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required and cannot be empty')
        return v.strip()

    @validator('release_date')
    def validate_release_date(cls, v):
        if v and v.strip():
            v = v.strip()
            # Basic date format validation
            if len(v) == 10 and v[4] == '-' and v[7] == '-':
                try:
                    year = int(v[:4])
                    month = int(v[5:7])
                    day = int(v[8:10])
                    if not (1900 <= year <= 2100):
                        raise ValueError('Year must be between 1900 and 2100')
                    if not (1 <= month <= 12):
                        raise ValueError('Month must be between 1 and 12')
                    if not (1 <= day <= 31):
                        raise ValueError('Day must be between 1 and 31')
                    return v
                except ValueError as e:
                    if "invalid literal" in str(e):
                        raise ValueError(
                            'Invalid date format. Use YYYY-MM-DD'
                        )
                    raise e
            else:
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
        return v

    @validator('genres')
    def validate_genres(cls, v):
        if v and v.strip():
            v = v.strip()
            try:
                genres = json.loads(v)
                if not isinstance(genres, list):
                    raise ValueError('Genres must be a JSON array')
                for genre in genres:
                    if not isinstance(genre, str):
                        raise ValueError(
                            'Each genre must be a string'
                        )
                return v
            except json.JSONDecodeError:
                raise ValueError(
                    'Genres must be a valid JSON array, '
                    'ex: ["Action", "Comedy"]'
                )
        return v

    class Config:
        str_strip_whitespace = True


class CsvUploadResponseDTO(BaseModel):
    """DTO to response of CSV upload."""

    success: bool = Field(..., description="If the upload was successful")
    message: str = Field(..., description="Result message")
    total_rows: int = Field(..., description="Total rows processed")
    created_count: int = Field(..., description="Movies created")
    updated_count: int = Field(..., description="Movies updated")
    errors: List[str] = Field(
        default_factory=list, description="List of errors found"
    )


class CsvValidationErrorDTO(BaseModel):
    """DTO to validation errors of CSV."""

    line_number: int = Field(..., description="Line number with error")
    field: Optional[str] = Field(None, description="Field with error")
    error_message: str = Field(..., description="Error message")
    line_content: Optional[str] = Field(
        None, description="Line content with error"
    )
