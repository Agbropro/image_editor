from dataclasses import dataclass

#frozen mean the object is read only and can only be assigned initialy
# there are loopholes for frozen, we can modify mutable object such as list, dict, and sets we can add new content like using .append for the initialized variable

@dataclass(frozen = True,slots = True)
class UploadResponse:
    image_id:  str | None = None
    filename:  str | None = None
    format:    str | None = None
    width:     int | None = None
    height:    int | None = None
    frames:    int | None = None

@dataclass(slots=True)
class ImageVersion:
    version:    int
    file:       str
    operation:  str
    format:     str
    width:      int
    height:     int
    frames:     int

@dataclass(slots=True)
class ImageMetadata:
    image_id:           str
    current_version:    int
    versions:           list[ImageVersion]

@dataclass(slots=True)
class ImageInfo:
    format: str
    width: int
    height: int
    frames: int
