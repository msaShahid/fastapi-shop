from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):

    @abstractmethod
    async def upload(
        self,
        *,
        file: BinaryIO,
        path: str,
        content_type: str,
    ) -> str:
        """
        Store a file and return its storage path.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *, path: str) -> None:
        """
        Delete a file from storage.
        """
        raise NotImplementedError

    @abstractmethod
    def get_url(self, *, path: str) -> str:
        """
        Return the public URL for a stored file.
        """
        raise NotImplementedError
