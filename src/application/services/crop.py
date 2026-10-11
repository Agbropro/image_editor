from src.application.ports.crop import CropProcessor
from src.application.ports.image import ImageInspector, ImageRepository
from src.domain.schemas.crop import CropRequest, CropResponse


class CropService:
    def __init__(self, repository: ImageRepository, processor: CropProcessor, inspector: ImageInspector) -> None:
        self.repository = repository
        self.processor = processor
        self.inspector = inspector

    def crop(self, image_id: str, request: CropRequest) -> CropResponse:
        """Crop the current image and save the result as a new version."""
        content = self.repository.current_content(image_id)
        source = self.inspector.inspect(content)
        left, top = request.top_left_point
        right, bottom = request.bottom_right_point
        # Crop coordinates form (left, top, right, bottom), measured from the image's top-left corner.
        if min(left, top, right, bottom) < 0 or left >= right or top >= bottom:
            raise ValueError("Crop points must form a rectangle with positive area")
        if right > source.width or bottom > source.height:
            raise ValueError("Crop points must be within the image")
        edited, info = self.processor.crop(content, request)
        version = self.repository.save_version(image_id, edited, info, "crop")
        return CropResponse(image_id, version, info.width, info.height, info.frames)
