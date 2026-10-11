from abc import ABC, abstractmethod

from src.domain.schemas.image import ImageInfo


class ResizeProcessor(ABC):
    @abstractmethod
    def resize(self, content: bytes, width: int, height: int) -> tuple[bytes, ImageInfo]:
        """Return edited bytes and their image information."""
