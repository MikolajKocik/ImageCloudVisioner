from fastapi import HTTPException
from io import BytesIO
from PIL import Image, UnidentifiedImageError
 
def convert_to_pdf(image_stream: BytesIO) -> BytesIO:
    try:
        image = Image.open(image_stream)
        image.load()
        output_stream = BytesIO()
        image.convert("RGB").save(output_stream, format="PDF")
        output_stream.seek(0)

        return output_stream.read()
    
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image format")
 