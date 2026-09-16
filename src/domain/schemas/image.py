from pydantic import BaseModel

class UploadResponse(BaseModel):
    image_id:  str | None = None
    filename:  str | None = None
    format:    str | None = None
    width:     int | None = None
    height:    int | None = None
    frames:    int | None = None



class ImageVersion(BaseModel):
    version:    int
    file:       str
    operation: str
    format:     str
    width:      int
    height:     int
    frames:     int


class ImageMetadata(BaseModel):
    image_id:           str
    current_version:    int
    versions:           list[ImageVersion]