from fastapi import FastAPI
from src.routes.image import router as image_router
from src.routes.resize import router as resize_router
app = FastAPI(
    title= "Image Editor API",
    version = "1.0.0"
)

app.include_router(image_router, prefix="/api/v1")
app.include_router(resize_router, prefix="/api/v1")