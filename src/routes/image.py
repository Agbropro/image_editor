from fastapi import APIRouter, UploadFile, File
from src.services.image import ImageService
from src.domain.schemas.image import UploadResponse

router = APIRouter()
image_service = ImageService()

@router.post("/images",response_model=UploadResponse) # set the response to be UploadResponse from schemas
async def upload_image(file: UploadFile = File(...),): # image multipart, (...) means required data
    """Upload image and create image editing session"""
    image_id = image_service.generate_image_id()
    content = await file.read()
    saved_path = image_service.save_original(
        image_id = image_id,
        filename = file.filename,
        content = content
    )
    
    inspect_result = image_service.inspect_image(image_path = saved_path)
    image_service.create_metadata(
        image_id = image_id, 
        inspect_result = inspect_result, 
        saved_path = saved_path
    )
    
    return UploadResponse(
        image_id = image_id,
        filename = saved_path.name,
        format = inspect_result.format,
        width = inspect_result.width,
        height = inspect_result.height,
        frames = inspect_result.frames
    )
    
    
# # POST   /api/v1/images
# GET    /api/v1/images/{image_id}
# POST   /api/v1/images/{image_id}/resize
# GET    /api/v1/images/{image_id}/download