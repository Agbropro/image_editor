from fastapi import FastAPI
from src.routes.image import router as image_router
from src.routes.resize import router as resize_router
from src.routes.health import router as health_router
from src.routes.version import router as version_router

app = FastAPI(
    title= "Image Editor API",
    version = "1.0.0"
)

prefix = "/api/v1"
app.include_router(image_router, prefix=prefix)
app.include_router(resize_router, prefix=prefix)
app.include_router(health_router,prefix=prefix)
app.include_router(version_router,prefix=prefix)