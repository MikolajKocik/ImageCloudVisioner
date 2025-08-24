from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import image

app = FastAPI(
    title="Image Cloud Visioner API",
    description="API for analyzing images and OCR recognizing depends on Azure Cognitive Services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(image.router, prefix="/image", tags=["Image Processing"])

@app.get("/")
async def root():
    return {"message": "Image Cloud Visioner API is running"}
