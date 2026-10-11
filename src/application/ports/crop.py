from abc import ABC, abstractmethod

from src.domain.schemas.crop import CropRequest
from src.domain.schemas.image import ImageInfo


class CropProcessor(ABC):
    @abstractmethod
    def crop(self, content: bytes, request: CropRequest) -> tuple[bytes, ImageInfo]:
        """Return edited bytes and their image information."""
