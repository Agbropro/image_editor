from pathlib import Path
from uuid import uuid4

from src.application.ports.image import ImageInspector, ImageRepository
from src.domain.schemas.image import ImageMetadata, UploadResponse


class ImageService:
    def __init__(self, repository: ImageRepository, inspector: ImageInspector) -> None:
        self.repository = repository
        self.inspector = inspector

    def upload(self, filename: str, content: bytes) -> UploadResponse:
        info = self.inspector.inspect(content)
        image_id = uuid4().hex
        self.repository.save_original(image_id, filename, content, info)
        return UploadResponse(image_id, filename, info.format, info.width, info.height, info.frames)

    def details(self, image_id: str) -> ImageMetadata:
        return self.repository.load_metadata(image_id)

    def current_path(self, image_id: str) -> Path:
        return self.repository.current_path(image_id)

    def reset(self, image_id: str) -> ImageMetadata:
        """Make the original upload the current image again."""
        return self.repository.set_current_version(image_id, 0)
