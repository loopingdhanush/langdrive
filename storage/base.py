from abc import ABC, abstractmethod
from pathlib import Path

class StorageProvider(ABC):

    @abstractmethod
    def save(self, source: Path, storage_key: str) -> None:
        pass

    @abstractmethod
    def get(self, storage_key: str) -> Path:
        pass

    @abstractmethod
    def delete(self, storage_key: str) -> None:
        pass

    @abstractmethod
    def exists(self, storage_key: str) -> bool:
        pass