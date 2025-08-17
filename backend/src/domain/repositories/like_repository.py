from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from src.domain.entities.like import Like


class LikeRepository(ABC):
    @abstractmethod
    def save(self, like: Like) -> Like:
        pass

    @abstractmethod
    def get_by_user_and_movie(
        self, user_id: int, movie_id: int
    ) -> Optional[Like]:
        pass

    @abstractmethod
    def get_by_user(
        self, user_id: int, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Like], int]:
        pass

    @abstractmethod
    def get_user_movie_matrix(self) -> List[Tuple[int, int]]:
        pass

    @abstractmethod
    def delete(self, like_id: int) -> bool:
        pass

    @abstractmethod
    def delete_by_user_and_movie(self, user_id: int, movie_id: int) -> bool:
        pass
