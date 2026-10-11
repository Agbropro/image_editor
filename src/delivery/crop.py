from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.application.services.crop import CropService
from src.domain.schemas.crop import CropRequest as DomainCropRequest
from src.delivery.dependencies import get_crop_service
from src.delivery.schemas import CropRequest, EditResponse

router = APIRouter()


@router.post("/images/{image_id}/crop", response_model=EditResponse)
def crop_image(image_id: str, request: CropRequest, service: Annotated[CropService, Depends(get_crop_service)]):
    try:
        result = service.crop(image_id, DomainCropRequest(**request.model_dump()))
        return EditResponse.model_validate(result)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=f"Image not found: {image_id}") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
