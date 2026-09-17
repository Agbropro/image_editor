from fastapi import APIRouter
from src.domain.schemas.resize import ResizeRequest, ResizeResponse
from src.services.image import ImageService
from src.services.resize import ResizeService
from PIL import Image

router = APIRouter()
resize_service = ResizeService()
image_service = ImageService()

@router.post(
    "/image/{image_id}/resize",
    response_model = ResizeResponse
)
async def resize_image(
    image_id: str,
    request: ResizeRequest
):
    """Resize the current image version"""
    image_path = image_service.get_current_image(image_id=image_id)
    with Image.open(image_path) as image:
        new_w, new_h = resize_service.calc_new_dimension(
            image=image,
            request=request
        )
        resized_image = resize_service.resize_image(
            image=image,
            width = new_w,
            height= new_h
        )
    
    version = image_service.save_version(image_id=image_id,image=resized_image,operation="resize")
    frames = getattr(resized_image, "n_frames",1)
    return ResizeResponse(
        image_id= image_id,
        version = version,
        width = new_w,
        height = new_h,
        frames = frames
    )