from dataclasses import dataclass
from typing import List, TypeVar, Generic

T = TypeVar('T')


@dataclass(frozen=True)
class PaginationRequest:
    page: int = 1
    per_page: int = 20

    def __post_init__(self):
        if self.page < 1:
            object.__setattr__(self, 'page', 1)
        if self.per_page < 1:
            object.__setattr__(self, 'per_page', 20)
        if self.per_page > 100:
            object.__setattr__(self, 'per_page', 100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1
