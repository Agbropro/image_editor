from abc import ABC, abstractmethod
from pathlib import Path

from src.domain.schemas.image import ImageInfo, ImageMetadata


class ImageInspector(ABC):
    @abstractmethod
    def inspect(self, content: bytes) -> ImageInfo:
        """Inspect image bytes, raising ValueError for invalid images."""


class ImageRepository(ABC):
    @abstractmethod
    def save_original(self, image_id: str, filename: str, content: bytes, info: ImageInfo) -> ImageMetadata:
        """Store an upload and its initial metadata."""

    @abstractmethod
    def load_metadata(self, image_id: str) -> ImageMetadata:
        """Load all versions for an image."""

    @abstractmethod
    def current_path(self, image_id: str) -> Path:
        """Get the current image path for HTTP delivery."""

    @abstractmethod
    def current_content(self, image_id: str) -> bytes:
        """Read the current image bytes."""

    @abstractmethod
    def save_version(self, image_id: str, content: bytes, info: ImageInfo, operation: str) -> int:
        """Persist an edited image and return its new version."""

    @abstractmethod
    def set_current_version(self, image_id: str, version: int) -> ImageMetadata:
        """Select a saved version without deleting any versions."""