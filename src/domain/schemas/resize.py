from pydantic import BaseModel

class ResizeRequest(BaseModel):
    width:                  int | None = None
    height:                 int | None = None
    scale:                  float | None = None
    maintain_aspect_ratio:  bool = True

class ResizeResponse(BaseModel):
    image_id:       str | None = None
    version:        int | None = None
    width:          int | None = None
    height:         int | None = None
    frames:         int | None = None
    