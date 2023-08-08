from abc import ABC, abstractmethod
from typing import Optional


class Storage(ABC):
    """
    The storage interface for the Logto client.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        ...

    @abstractmethod
    def set(self, key: str, value: Optional[str]) -> None:
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        ...
