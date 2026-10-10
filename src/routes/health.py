from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status : bool
    message : str

router = APIRouter()

@router.get("/health",response_model=HealthResponse)
def get_health()->HealthResponse:

    status = True
    message = "API is healthy"
    return HealthResponse(
        status=status,
        message = message
    )
