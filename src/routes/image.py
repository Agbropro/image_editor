from fastapi import Router, UploadFile, File

router = Router()

POST   /api/v1/images
GET    /api/v1/images/{image_id}
POST   /api/v1/images/{image_id}/resize
GET    /api/v1/images/{image_id}/download