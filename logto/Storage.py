from abc import ABC, abstractmethod


class Storage(ABC):
    """
    The storage interface for the Logto client.
    """

    @abstractmethod
    def get(self, key: str) -> str | None:
        ...

    @abstractmethod
    def set(self, key: str, value: str | None) -> None:
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        ...
