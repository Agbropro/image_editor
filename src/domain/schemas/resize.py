from pydantic import BaseModel, ConfigDict
from typing import Any

class ResizedGIF(BaseModel):
    resized_frames: list[Any]
    durations :     list[int]
    disposals :     int
    loop :          int
    
    
class ResizeRequest(BaseModel):
    width:                  int | None = None
    height:                 int | None = None
    scale:                  float | None = None
    maintain_aspect_ratio:  bool = True
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "width": None,
                "height": 500,
                "scale": None,
                "maintain_aspect_ratio": True
            }
        }
    )

class ResizeResponse(BaseModel):
    image_id:       str | None = None
    version:        int | None = None
    width:          int | None = None
    height:         int | None = None
    frames:         int | None = None

