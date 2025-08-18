from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from src.domain.entities.movie import Movie


class MovieRepository(ABC):
    @abstractmethod
    def save(self, movie: Movie) -> Movie:
        pass

    @abstractmethod
    def save_many(self, movies: List[Movie]) -> int:
        pass

    @abstractmethod
    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        pass

    @abstractmethod
    def get_by_tmdb_id(self, tmdb_id: int) -> Optional[Movie]:
        pass

    @abstractmethod
    def get_by_title(self, title: str) -> Optional[Movie]:
        pass

    @abstractmethod
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Movie], int]:
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Movie], int]:
        pass

    @abstractmethod
    def get_popular(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Movie], int]:
        pass

    @abstractmethod
    def delete(self, movie_id: int) -> bool:
        pass
