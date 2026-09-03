from pathlib import Path
from typing import BinaryIO

from app.core.storage.interface import StorageService


class LocalStorageService(StorageService):
    def __init__(
        self,
        *,
        root_path: str | Path = "media",
        base_url: str = "/media",
    ) -> None:
        self.root_path = Path(root_path)
        self.base_url = base_url.rstrip("/")

        self.root_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    async def upload(
        self,
        *,
        file: BinaryIO,
        path: str,
        content_type: str,
    ) -> str:
        destination = self._get_safe_path(path)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with destination.open("wb") as output:
            while chunk := file.read(1024 * 1024):
                output.write(chunk)

        return path

    async def delete(self, *, path: str) -> None:
        file_path = self._get_safe_path(path)

        if file_path.exists():
            file_path.unlink()

    def get_url(self, *, path: str) -> str:
        return f"{self.base_url}/{path}"

    def _get_safe_path(self, path: str) -> Path:
        """
        Prevent path traversal such as ../../some-file.
        """
        root = self.root_path.resolve()
        destination = (self.root_path / path).resolve()

        if not destination.is_relative_to(root):
            raise ValueError("Invalid storage path")

        return destination
