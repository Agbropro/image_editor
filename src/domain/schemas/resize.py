from typing import Any
from dataclasses import dataclass

@dataclass(slots=True)
class ResizedGIF:
    resized_frames: list[Any]
    durations :     list[int]
    disposals :     int
    loop :          int

@dataclass(slots=True)
class ResizeRequest:
    width:                  int | None = None
    height:                 int | None = None
    scale:                  float | None = None
    maintain_aspect_ratio:  bool = True

@dataclass(slots=True)
class ResizeResponse:
    image_id:       str | None = None
    version:        int | None = None
    width:          int | None = None
    height:         int | None = None
    frames:         int | None = None

