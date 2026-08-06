import os
import requests
from openai import OpenAI
from PIL import Image 
from io import BytesIO
import base64
from  dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("API_KEY_OPENAI")
MODEL = "gpt-image-1"

client = OpenAI(api_key=API_KEY)

response = client.responses.create(
    model="gpt-5.5",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]
    
if image_data:
    image_base64 = image_data[0]
    with open("otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))