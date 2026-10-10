from fastapi import APIRouter, HTTPException
from src.domain.schemas.crop import CropResponse, CropRequest
from PIL import Image
from src.routes.image import ImageService
from src.routes.crop import CropService

router = APIRouter()
image_service = ImageService()
crop_service = CropService()

@router.post("/images/{image_id}/crop",response_model=CropResponse)
def crop(image_id= str,request=CropRequest)->Image:
    """Crop image"""
    try:
        image_path = image_service.get_current_image(image_id=image_id)
        with Image.open(image_path) as image:
            cropped_frames = crop_service.crop(image=image,request=request)
            if image_path.suffix.lower() == ".gif":
                cropped_image = cropped_frames.cropped_frames
                frames = len(cropped_image.cropped_image)
            else:
                cropped_image = cropped_frames.copy()
                frames = getattr(cropped_image,"n_frames",1)
            version = image_service.save_version(image_id=image_id,image=cropped_image,operation="cropped")
                    
    #     with open Image.open(image_path) as image:
    #         cropped_image = crop_service.crop(image=image, request=request)
            
    # except:

