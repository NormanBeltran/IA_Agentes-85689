from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# leer configuracion

API_KEY = os.getenv("API_KEY_OR")
MODEL = os.getenv("MODEL_OR_IMG")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1",    
)

print(f"Modelo usado {MODEL}")

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  extra_body={},
  model=MODEL,
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          #"text": "Entregame un JSON con el modelo, marca, color y patente del vehiculo de la foto"
          "text": "Describir al mayor detalle la imagen"
        },
        {
          "type": "image_url",
          "image_url": {
           #"url": "https://www.clarin.com/img/2024/10/05/B9CttXYQX_2000x1500__1.jpg"
           #"url": "https://media.c5n.com/p/2f8e7db82718e5e4ce277459795d7653/adjuntos/326/imagenes/000/190/0000190067/790x0/smart/tapar-patente.png"
           "url": "https://www.lapaginaverdedigital.com.co/wp-content/uploads/2024/10/Screenshot_6.png"
          }
        }
      ]
    }
  ]
)

print(completion.choices[0].message.content)