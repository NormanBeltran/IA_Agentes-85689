import os
from dotenv import load_dotenv
from groq import Groq


# Leer las variables del archivo .env

load_dotenv()

# Leer configuración externa para las variables que queremos usar en el programa

API_KEY = os.getenv("API_KEY_GROQ")
MODELO = os.getenv("MODEL_GROQ")

# Validar que existan las variables

if not API_KEY:
    raise ValueError("API_KEY no esta definida")
if not MODELO:
    raise ValueError("MODELO no esta definido")

# Inicializar el cliente (objeto que va a invocar al modelo de IA)
client = Groq(api_key=API_KEY)

## Funcion
def consultar_modelo(mensaje, system_prompt=None):
    """
    Envia un mensaje al modelo de Groq y retorna la respuesta

    Args: 
        mensaje: La pregunta o instruccion para el modelo
        system_prompt: (Opcional) Instrucción de comportamiento (rol o perfil del asistente)
    Return:
        El contenido de la respuesta del modelo
    """

    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": mensaje
    })

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODELO,
            temperature=0.7,
            max_tokens=400
        )
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        return f"Error al llamar al modelo {MODELO}: {e}"

## Main
if __name__ == "__main__":
    # Prompt de sistema opcional
    system = input("Ingresa el rol del modelo: ")

    # Consulta
    pregunta = input("Ingresa la pregunta o instruccion al modelo: ")

    print(f"Usuario: {pregunta}")
    respuesta = consultar_modelo(pregunta, system_prompt=system)
    print(f"Modelo de IA: {respuesta}")