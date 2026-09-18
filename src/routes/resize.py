from fastapi import APIRouter, HTTPException
from src.domain.schemas.resize import ResizeRequest, ResizeResponse
from src.services.image import ImageService
from src.services.resize import ResizeService
from PIL import Image

router = APIRouter()
resize_service = ResizeService()
image_service = ImageService()

# get current image -> calculate new size based on request -> resize ->  set new version -> return response
@router.post(
    "/images/{image_id}/resize",
    response_model = ResizeResponse
)
def resize_image(
    image_id: str,
    request: ResizeRequest
):
    """Resize the current image version"""
    try:
        image_path = image_service.get_current_image(image_id=image_id)
        
        with Image.open(image_path) as image:
            new_w, new_h = resize_service.calc_new_dimension(
                image=image,
                request=request
            )
            if image_path.suffix.lower() == ".gif":
                resized_image = resize_service.resize_gif(
                                    image=image,
                                    width = new_w,
                                    height= new_h
                                )
                frames = len(resized_image.resized_frames)
            else: 
                resized_image = resize_service.resize_image(
                                    image=image,
                                    width = new_w,
                                    height= new_h
                                )
                frames = getattr(resized_image, "n_frames",1)
        
        version = image_service.save_version(image_id=image_id,image=resized_image,operation="resize")
        
        return ResizeResponse(
            image_id= image_id,
            version = version,
            width = new_w,
            height = new_h,
            frames = frames
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code = 404,
            detail=f"Image not found: {image_id}"
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )