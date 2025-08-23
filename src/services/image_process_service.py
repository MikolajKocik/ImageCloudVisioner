from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from config.azure_key_vault import secret_client
from typing import Dict
import time

def get_computer_vision_client() -> ComputerVisionClient:
    endpoint = secret_client.get_secret("VAULT_URL")
    key = secret_client.get_secret("Azure--subscriptionIdentifier")
    return ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

def analyze_image(image_path) -> Dict:
    # load image
    with open(image_path, "rb") as image_stream:
        analysis = get_computer_vision_client().analyze_image_in_stream(
            image_stream,
            visual_features=[
                VisualFeatureTypes.description,
                VisualFeatureTypes.tags,
                VisualFeatureTypes.color
            ]
        )
    
    # result is dict
    result = {}

    # Safely print description
    if analysis.description and analysis.description.captions:
        result["description"] = analysis.description.captions[0].text
    else:
        result["description"] = "Not available"

    # Safely print tags
    if hasattr(analysis, 'tags') and analysis.tags: 
        result["tags"] = [tag.name for tag in analysis.tags]
    else:
        result["tags"] = []
    # Safely print dominant colors
    if hasattr(analysis, 'color') and hasattr(analysis.color, 'dominant_colors'):
        result["colors"] = analysis.color.dominant_colors
    else:
        result["colors"] = []

    return result

def recognize_image(image_path) -> None:
    with open(image_path, "rb") as image_stream: 
        ocr_result = get_computer_vision_client().read_in_stream(image_stream, raw=True)

    # get operation by id
    operation_location = ocr_result.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    # wait for result
    while True:
        result = get_computer_vision_client().get_read_result(operation_id)
        if result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)
    
    # show text
    if result.status == 'succeeded':
        for page in result.analyze_result.read_results:
            for line in page.lines:
                print(line.text)