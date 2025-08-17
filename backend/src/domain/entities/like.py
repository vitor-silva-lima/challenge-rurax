from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Like:
    id: Optional[int]
    user_id: int
    movie_id: int
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
