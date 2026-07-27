import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Cargar variables desde el archivo .env
load_dotenv()

# Leer configuración externa
API_KEY = os.getenv("API_KEY_HF")
MODEL = os.getenv("MODEL_HF")

# Validar que existan las variables
if not API_KEY:
    raise ValueError("❌ API_KEY_HF no está definida en el archivo .env")
if not MODEL:
    raise ValueError("❌ MODEL_HF no está definida en el archivo .env")

# Inicializar cliente
client = InferenceClient(model=MODEL, token=API_KEY)

def consultar_modelo(mensaje_usuario: str, system_prompt: str = None) -> str:
    """
    Envía un mensaje al modelo de Hugging Face y retorna la respuesta.
    """
    messages = []
    
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    messages.append({
        "role": "user",
        "content": mensaje_usuario
    })
    
    try:
        response = client.chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error al consultar Hugging Face: {e}"

# --- Ejemplo de uso ---
if __name__ == "__main__":
    system = "Eres un asistente útil y conciso. Responde siempre en español."
    pregunta = "¿Qué es el aprendizaje automático en una oración?"
    
    print(f"🧑 Usuario: {pregunta}\n")
    respuesta = consultar_modelo(pregunta, system_prompt=system)
    print(f"🤖 {MODEL}: {respuesta}")