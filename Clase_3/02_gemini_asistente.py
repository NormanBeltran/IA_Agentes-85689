import os
from dotenv import load_dotenv
from google import  genai
from google.genai import  types

# Cargar variables desde el archivo .env
load_dotenv()

# Leer configuración externa
API_KEY = os.getenv("API_KEY_GEMINI")
MODEL = os.getenv("MODEL_GEMINI")

# Validar que existan las variables
if not API_KEY:
    raise ValueError("❌ API_KEY_GEMINI no está definida en el archivo .env")
if not MODEL:
    raise ValueError("❌ MODEL_GEMINI no está definida en el archivo .env")

# Configurar la API key globalmente
client = genai.Client(api_key=API_KEY)

def consultar_modelo(mensaje_usuario: str, system_prompt: str = None) -> str:
    """
    Envía un mensaje al modelo de Gemini y retorna la respuesta.
    """
    try:
        # Crear configuración del modelo (system instruction es opcional)
        #model_kwargs = {"model_name": MODEL}
        #if system_prompt:
        #    model_kwargs["system_instruction"] = system_prompt
                       
        response = client.models.generate_content(
            model = MODEL,
            contents = mensaje_usuario,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=800
            )
        )
        
        return response.text
        
    except Exception as e:
        return f"Error al consultar Gemini: {e}"

# --- Ejemplo de uso ---
if __name__ == "__main__":
    system = "Eres un asistente útil y conciso. Responde siempre en español."
    pregunta = "Explicame que es un Agente de IA y su diferencia con un Asistente."
    
    print(f"🧑 Usuario: {pregunta}\n")
    respuesta = consultar_modelo(pregunta, system_prompt=system)
    print(f"🤖 {MODEL}: {respuesta}")