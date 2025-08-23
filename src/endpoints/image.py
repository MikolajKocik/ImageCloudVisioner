from fastapi import APIRouter, UploadFile
from src.services.image_process_service import analyze_image
from src.models.image_insights import ImageInsights
from io import BytesIO

router = APIRouter()

@router.post("/analyze", response_model=ImageInsights)
async def analyze(file: UploadFile):
    image_stream = BytesIO(await file.read())
    return analyze_image(image_stream)