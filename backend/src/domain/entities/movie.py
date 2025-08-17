from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List
import json


@dataclass
class Movie:
    id: Optional[int]
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    genres: Optional[str] = None  # JSON string
    runtime: Optional[int] = None
    original_language: Optional[str] = None
    tmdb_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)

    def get_genres_list(self) -> List[str]:
        if not self.genres:
            return []
        try:
            return json.loads(self.genres)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_genres_list(self, genres: List[str]) -> None:
        self.genres = json.dumps(genres)
        self.updated_at = datetime.now(timezone.utc)

    def update_rating(self, vote_average: float, vote_count: int) -> None:
        self.vote_average = vote_average
        self.vote_count = vote_count
        self.updated_at = datetime.now(timezone.utc)

    def get_year(self) -> Optional[str]:
        if self.release_date and len(self.release_date) >= 4:
            return self.release_date[:4]
        return None
