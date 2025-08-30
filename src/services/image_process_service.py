from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes, ReadResult, ReadOperationResult
from azure.cognitiveservices.vision.computervision.models import ImageAnalysis
from msrest.authentication import CognitiveServicesCredentials
from config.azure_key_vault import load_keyvault
from ..models.image_insights import ImageInsights
import time
from io import BytesIO # image has binary data
from typing import List
from functools import lru_cache

# create a computer vision client once per app using caching
@lru_cache()
def get_computer_vision_client() -> ComputerVisionClient:
    secret_client = load_keyvault()
    endpoint = secret_client.get_secret("Azure--ComputerVisionEndpoint")
    key = secret_client.get_secret("Azure--ComputerVisionKey")
    return ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

def analyze_image(image_stream: BytesIO) -> ImageInsights:
    try:
        # load stream
        analysis: ImageAnalysis = get_computer_vision_client().analyze_image_in_stream(
            image_stream,
            visual_features=[
                VisualFeatureTypes.description,
                VisualFeatureTypes.tags,
                VisualFeatureTypes.color
            ]
        )
        
        description = (
            analysis.description.captions[0].text
            if analysis.description and analysis.description.captions
            else "Not available"
        )

        tags = [tag.name for tag in analysis.tags] if analysis.tags else []
        
        colors = analysis.color.dominant_colors if analysis.color and analysis.color.dominant_colors else []

        return ImageInsights(
            analysis=analysis,
            description=description,
            tags=tags,
            colors=colors
        )
    except Exception as e:
        raise RuntimeError(f"Azure vision failed: {e}")

def recognize_image(image_stream: BytesIO) -> List[str]: 
    try:   
        # --- Stage 1: Submit the OCR job to the cloud service ---
        # This sends the image for processing and retrieves a unique operation ID.
        ocr_result = get_computer_vision_client().read_in_stream(image_stream, raw=True)
        operation_location: str = ocr_result.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1] # the las element in the collection is id so [-1]

        timeout = 30
        start_time = time.time()

        # --- Stage 2: Poll the service until the OCR job is complete ---
        # The loop checks the status of the operation using its ID, waiting for it to finish.   
        while True:
            result: ReadOperationResult = get_computer_vision_client().get_read_result(operation_id)
            if result.status not in ['notStarted', 'running']:
                break
            if time.time() - start_time > timeout:
                raise TimeoutError("OCR operation timed out")
            time.sleep(1)
        
        # --- Stage 3: Extract and format the recognized text ---
        # This section retrieves the processed data and extracts the text lines from the results.
        lines = []
        if result.status == 'succeeded':
            for page in result.analyze_result.read_results:
                page: ReadResult
                for line in page.lines:
                    lines.append(line.text)
        
        return lines
    
    except Exception as e:
        raise RuntimeError(f"OCR operation failed: {e}")