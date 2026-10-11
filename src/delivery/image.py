from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.application.services.image import ImageService
from src.delivery.dependencies import get_image_service
from src.delivery.schemas import ImageMetadata, UploadResponse

router = APIRouter()
ImageServiceDependency = Annotated[ImageService, Depends(get_image_service)]


@router.post("/images", response_model=UploadResponse)
async def upload_image(file: Annotated[UploadFile, File()], service: ImageServiceDependency):
    try:
        result = service.upload(file.filename or "image", await file.read())
        return UploadResponse.model_validate(result)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/images/{image_id}/details", response_model=ImageMetadata)
def get_image(image_id: str, service: ImageServiceDependency):
    try:
        return ImageMetadata.model_validate(service.details(image_id))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=f"Image not found: {image_id}") from error


@router.get("/images/{image_id}/view")
def view(image_id: str, service: ImageServiceDependency) -> FileResponse:
    return _file_response(image_id, service, "inline")


@router.get("/images/{image_id}/download")
def download(image_id: str, service: ImageServiceDependency) -> FileResponse:
    return _file_response(image_id, service, "attachment")


def _file_response(image_id: str, service: ImageService, disposition: str) -> FileResponse:
    try:
        path = service.current_path(image_id)
        return FileResponse(path=path, filename=path.name, content_disposition_type=disposition)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=f"Image not found: {image_id}") from error

@router.post("/images/{image_id}/reset", response_model=ImageMetadata)
def reset_image(image_id: str, service: ImageServiceDependency):
    try:
        return ImageMetadata.model_validate(service.reset(image_id))
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {image_id}",
        ) from error