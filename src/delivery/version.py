from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yaml

router = APIRouter()

class VersionResponse(BaseModel):
    version:    str
    desc:       str
    
@router.get("/versions", response_model=VersionResponse)
def get_version():
    try:
        with open ("config/config.yaml","r",encoding="utf-8") as file:
            config = yaml.safe_load(file)

        version = config.get("version").get("version")
        desc = config.get("version").get("desc")
        return VersionResponse(
            version = version,
            desc = desc
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code = 500,
            detail = f"config file not found {config}"
        )