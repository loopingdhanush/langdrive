import shutil
from pathlib import Path

from storage.base import StorageProvider


class LocalStorage(StorageProvider):

    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _resolve(self, storage_key: str) -> Path:
        path = self.root / storage_key

        resolved = path.resolve()

        if self.root.resolve() not in resolved.parents:
            raise ValueError("Invalid storage key")

        return resolved

    def save(self, source: Path, storage_key: str) -> None:
        destination = self._resolve(storage_key)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(source, destination)

    def get(self, storage_key: str) -> Path:
        path = self._resolve(storage_key)

        if not path.exists():
            raise FileNotFoundError(storage_key)

        return path

    def delete(self, storage_key: str) -> None:
        path = self._resolve(storage_key)

        if path.exists():
            path.unlink()

    def exists(self, storage_key: str) -> bool:
        return self._resolve(storage_key).exists()