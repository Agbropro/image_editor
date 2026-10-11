from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.application.services.crop import CropService
from src.application.services.image import ImageService
from src.application.services.resize import ResizeService
from src.infrastructure.file_image import FileImageRepository
from src.infrastructure.pillow_image import PillowImageProcessor


@lru_cache
def get_repository() -> FileImageRepository:
    return FileImageRepository()


@lru_cache
def get_processor() -> PillowImageProcessor:
    return PillowImageProcessor()


def get_image_service(repository: Annotated[FileImageRepository, Depends(get_repository)], processor: Annotated[PillowImageProcessor, Depends(get_processor)]) -> ImageService:
    return ImageService(repository, processor)


def get_resize_service(repository: Annotated[FileImageRepository, Depends(get_repository)], processor: Annotated[PillowImageProcessor, Depends(get_processor)]) -> ResizeService:
    return ResizeService(repository, processor, processor)


def get_crop_service(repository: Annotated[FileImageRepository, Depends(get_repository)], processor: Annotated[PillowImageProcessor, Depends(get_processor)]) -> CropService:
    return CropService(repository, processor, processor)
