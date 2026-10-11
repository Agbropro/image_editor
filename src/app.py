from fastapi import FastAPI
from src.delivery.image import router as image_router
from src.delivery.resize import router as resize_router
from src.delivery.health import router as health_router
from src.delivery.version import router as version_router
from src.delivery.crop import router as crop_router

app = FastAPI(
    title= "Image Editor API",
    version = "1.0.0"
)

prefix = "/api/v1"
app.include_router(image_router, prefix=prefix)
app.include_router(resize_router, prefix=prefix)
app.include_router(health_router,prefix=prefix)
app.include_router(version_router,prefix=prefix)
app.include_router(crop_router,prefix=prefix)
