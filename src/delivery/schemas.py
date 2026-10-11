from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UploadResponse(APIModel):
    image_id: str
    filename: str
    format: str
    width: int
    height: int
    frames: int


class ImageVersion(APIModel):
    version: int
    file: str
    operation: str
    format: str
    width: int
    height: int
    frames: int


class ImageMetadata(APIModel):
    image_id: str
    current_version: int
    versions: list[ImageVersion]


class ResizeRequest(APIModel):
    width: int | None = None
    height: int | None = None
    scale: float | None = None
    maintain_aspect_ratio: bool = True


class EditResponse(APIModel):
    image_id: str
    version: int
    width: int
    height: int
    frames: int


class CropRequest(APIModel):
    top_left_point: tuple[int, int] = Field(description="Left and top coordinates")
    bottom_right_point: tuple[int, int] = Field(description="Right and bottom coordinates")
