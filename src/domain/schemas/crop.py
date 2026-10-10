from pydantic import BaseModel
from typing import Any

class CropResponse(BaseModel):
    image_id :  str | None
    version:    int | None
    width:      int | None
    height:     int | None
    frames :    int | None

class CropRequest(BaseModel):
    top_left_point :        tuple[int] | None
    bottom_right_point :    tuple[int] | None

class CroppedGIF(BaseModel):
    cropped_frames: list[Any]
    durations :     list[int]
    disposals :     int
    loop :          int