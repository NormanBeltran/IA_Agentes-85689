import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("API_KEY_GROQ")

if not api_key:
    raise RuntimeError(
        "No se encontró API_KEY_GROQ. "
        "Creá un archivo .env con tu clave de Groq."
    )

MODEL = os.getenv("MODEL_GROQ", "llama-3.3-70b-versatile")

#print(f"Using model: {MODEL} with API key: {api_key}")
client = Groq(api_key=api_key)