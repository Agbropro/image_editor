from src.application.ports.image import ImageInspector, ImageRepository
from src.application.ports.resize import ResizeProcessor
from src.domain.schemas.resize import ResizeRequest, ResizeResponse


class ResizeService:
    def __init__(self, repository: ImageRepository, processor: ResizeProcessor, inspector: ImageInspector) -> None:
        self.repository = repository
        self.processor = processor
        self.inspector = inspector

    def resize(self, image_id: str, request: ResizeRequest) -> ResizeResponse:
        """Resize the current image and save the result as a new version."""
        content = self.repository.current_content(image_id)
        source = self.inspector.inspect(content)
        width, height = self._dimensions((source.width, source.height), request)
        edited, info = self.processor.resize(content, width, height)
        version = self.repository.save_version(image_id, edited, info, "resize")
        return ResizeResponse(image_id, version, info.width, info.height, info.frames)

    @staticmethod
    def _dimensions(size: tuple[int, int], request: ResizeRequest) -> tuple[int, int]:
        """Calculate target dimensions from width, height, or a scale factor."""
        width, height, scale = request.width, request.height, request.scale
        if any(value is not None and value <= 0 for value in (width, height, scale)):
            raise ValueError("Resize values must be greater than zero")
        if request.maintain_aspect_ratio:
            # One value determines the other dimension using the original aspect ratio.
            if sum(value is not None for value in (width, height, scale)) != 1:
                raise ValueError("Provide exactly one of width, height, or scale")
            if width is not None:
                return width, max(1, round(size[1] * width / size[0]))
            if height is not None:
                return max(1, round(size[0] * height / size[1])), height
            return max(1, round(size[0] * scale)), max(1, round(size[1] * scale))
        if width is None or height is None or scale is not None:
            raise ValueError("Provide width and height when aspect ratio is disabled")
        # Free resizing needs both dimensions because the original ratio is ignored.
        return width, height
