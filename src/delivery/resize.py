from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.application.services.resize import ResizeService
from src.domain.schemas.resize import ResizeRequest as DomainResizeRequest
from src.delivery.dependencies import get_resize_service
from src.delivery.schemas import EditResponse, ResizeRequest

router = APIRouter()


@router.post("/images/{image_id}/resize", response_model=EditResponse)
def resize_image(image_id: str, request: ResizeRequest, service: Annotated[ResizeService, Depends(get_resize_service)]):
    try:
        result = service.resize(image_id, DomainResizeRequest(**request.model_dump()))
        return EditResponse.model_validate(result)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=f"Image not found: {image_id}") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
