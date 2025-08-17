from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional


class SecurityService(ABC):

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        pass

    @abstractmethod
    def create_access_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[str]:
        pass
