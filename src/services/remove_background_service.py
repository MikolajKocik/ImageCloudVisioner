import requests
from io import BytesIO
import os

def remove_background(image_stream: BytesIO) -> BytesIO:
    api_key = os.getenv("REMOVE_BG_API_KEY")
    response = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": image_stream},
        data={"size": "auto"},
        headers={"X-Api-Key": api_key},
    )
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise RuntimeError(f"Remove.bg error: {response.status_code} - {response.text}")
    