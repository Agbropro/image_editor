from typing import Any
from dataclasses import dataclass

@dataclass(frozen=True,slots=True)
class CropResponse:
    image_id :  str | None
    version:    int | None
    width:      int | None
    height:     int | None
    frames :    int | None

@dataclass(slots=True)
class CropRequest:
    top_left_point :        tuple[int, int]
    bottom_right_point :    tuple[int, int]

@dataclass(slots=True)
class CroppedGIF:
    cropped_frames: list[Any]
    durations :     list[int]
    disposals :     int
    loop :          int
