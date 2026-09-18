from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse 
from src.services.image import ImageService
from src.domain.schemas.image import UploadResponse, ImageMetadata

router = APIRouter()
image_service = ImageService()

#generate image id -> save original image -> inspect the image -> create metadata -> return the response
@router.post("/images",response_model=UploadResponse) # set the response to be UploadResponse from schemas
async def upload_image(file: UploadFile = File(...),): # image multipart, (...) means required data
    """Upload image and create image editing session"""
    try:
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
            filename = file.filename,
            format = inspect_result.format,
            width = inspect_result.width,
            height = inspect_result.height,
            frames = inspect_result.frames
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
@router.get("/images/{image_id}",response_model=ImageMetadata)
def get_image(image_id:str):
    """Get image data from id"""
    try:
        metadata = image_service.load_metadata(image_id=image_id)
        return metadata
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Image not found : {image_id}"
        )

@router.get("/images/{image_id}/view")
def view(image_id:str)->FileResponse:
    try:

        current_image = image_service.get_current_image(image_id=image_id)
        
        return FileResponse(
            path=current_image,
            filename=current_image.name,
            content_disposition_type="inline"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail = f"file not found : {image_id}"
        )

@router.get("/images/{image_id}/download")
def view(image_id:str)->FileResponse:
    try:

        current_image = image_service.get_current_image(image_id=image_id)
        
        return FileResponse(
            path=current_image,
            filename=current_image.name,
            content_disposition_type="attachment"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail = f"file not found : {image_id}"
        )
# # POST   /api/v1/images
# GET    /api/v1/images/{image_id}
# POST   /api/v1/images/{image_id}/resize
# GET    /api/v1/images/{image_id}/download