from fastapi import APIRouter, UploadFile, File, HTTPException
from services.image_process_service import analyze_image, recognize_image
from models.image_insights import ImageInsights
from io import BytesIO
from typing import List

router = APIRouter()

@router.post("/analyze", response_model=ImageInsights)
async def analyze(file: UploadFile = File(...)) -> ImageInsights:
    try:
        image_stream = BytesIO(await file.read())
        return analyze_image(image_stream)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Invalid image or request")
    
@router.post("/ocr", response_model=List[str])
async def ocr(file: UploadFile = File(...)) -> List[str]:
    try:
        image_stream = BytesIO(await file.read())
        return recognize_image(image_stream)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Invalid image or request")
    