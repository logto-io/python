"""
Logto client storage abstract class and the default implementation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Literal, Optional

PersistKey = Literal["idToken", "accessTokenMap", "refreshToken", "signInSession"]
"""
The keys literal for the persistent storage.
"""


class Storage(ABC):
    """
    The storage interface for the Logto client. Logto client will use this
    interface to store and retrieve the logto session data.

    Usually this should be implemented as a persistent storage, such as a
    session or a database, since the page will be redirected to Logto and
    then back to the original page.
    """

    @abstractmethod
    def get(self, key: PersistKey) -> Optional[str]:
        """
        Get the stored string for the given key, return None if not found.
        """
        ...

    @abstractmethod
    def set(self, key: PersistKey, value: Optional[str]) -> None:
        """
        Set the stored value (string or None) for the given key.
        """
        ...

    @abstractmethod
    def delete(self, key: PersistKey) -> None:
        ...
        """
        Delete the stored value for the given key.
        """


class MemoryStorage(Storage):
    """
    The in-memory storage implementation for the Logto client. Note this should
    only be used for testing, since the data will be lost after the page is
    redirected.

    See `Storage` for the interface.
    """

    def printWarning() -> None:
        print(
            "WARNING: Using MemoryStorage for Logto client, this should only be used for testing.",
            "Replace with a persistent storage for production.",
        )

    def __init__(self) -> None:
        self._data: Dict[str, str] = {}

    def get(self, key: str) -> Optional[str]:
        MemoryStorage.printWarning()
        return self._data.get(key, None)

    def set(self, key: str, value: Optional[str]) -> None:
        MemoryStorage.printWarning()
        self._data[key] = value

    def delete(self, key: str) -> None:
        MemoryStorage.printWarning()
        self._data.pop(key, None)
