import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables desde el archivo .env
load_dotenv()

# Leer configuración externa
API_KEY = os.getenv("API_KEY_OPENAI")
MODEL = os.getenv("MODEL_OPENAI")

# Validar que existan las variables
if not API_KEY:
    raise ValueError("❌ API_KEY_OPENAI no está definida en el archivo .env")
if not MODEL:
    raise ValueError("❌ MODEL_OPENAI no está definida en el archivo .env")

# Inicializar cliente
client = OpenAI(api_key=API_KEY)

def consultar_modelo(mensaje_usuario: str, system_prompt: str = None) -> str:
    """
    Envía un mensaje al modelo de OpenAI y retorna la respuesta.
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
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error al consultar OpenAI: {e}"

# --- Ejemplo de uso ---
if __name__ == "__main__":
    system = "Eres un asistente útil y conciso. Responde siempre en español."
    pregunta = "¿Qué es la inteligencia artificial en una oración?"
    
    print(f"🧑 Usuario: {pregunta}\n")
    respuesta = consultar_modelo(pregunta, system_prompt=system)
    print(f"🤖 {MODEL}: {respuesta}")