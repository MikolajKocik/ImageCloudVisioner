from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from fastapi.responses import StreamingResponse
from ..services.image_process_service import analyze_image, recognize_image
from ..services.remove_background_service import remove_background
from ..services.convert_to_pdf_service import convert_to_pdf
from ..models.image_insights import ImageInsights
from io import BytesIO
from typing import List
from PIL import Image, UnidentifiedImageError

router = APIRouter()

ALLOWED_TYPES = [".jpg", ".png", ".bmp", ".tiff"]

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
    
@router.post("/remove-bg", response_model=Response)
async def remove_bg(file: UploadFile = File(...)) -> Response:
    # check MIME type 
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")
    
    image_stream = BytesIO(await file.read())
    try:
        image = Image.open(image_stream)
        image.verify()

        result_stream = remove_background(BytesIO(image_stream))

        return Response(
            content=result_stream.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=removed-bg.png"}
        )
    
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during image processing - {e}")
    
@router.post("/convert", response_model=BytesIO)
async def convert_format_to_pdf(file: UploadFile = File(...)) -> StreamingResponse:
    try:
        image_stream = BytesIO(await file.read())
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported image format")
        
        pdf_stream = convert_to_pdf(image_stream)
        return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={file.filename.rsplit('.', 1)[0]}.pdf"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ocurred while converting image - {e}")
        
     