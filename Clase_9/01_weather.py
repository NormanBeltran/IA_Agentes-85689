# openweathermap.org 
import json
import requests

from openai import OpenAI
from dotenv import load_dotenv
import os

# =========================
# CARGAR VARIABLES DE ENTORNO
# =========================

load_dotenv()

OPENAI_API_KEY = os.getenv("API_KEY_OPENAI")
OPENWEATHER_API_KEY = os.getenv("API_KEY_WEATHER")

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# FUNCION REAL
# =========================

def obtener_clima(ciudad):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={ciudad}"
        f"&appid={OPENWEATHER_API_KEY}"
        f"&lang=es"
        f"&units=metric"
    )

    response = requests.get(url)

    data = response.json()

    print("\n=== RESPUESTA API CLIMA ===\n")
    print(data)

    # Validacion de errores
    if response.status_code != 200:

        return {
            "error": True,
            "status_code": response.status_code,
            "mensaje": data.get("message", "Error desconocido")
        }

    return {
        "ciudad": ciudad,
        "temperatura": data["main"]["temp"],
        "descripcion": data["weather"][0]["description"]
    }
# =========================
# TOOLS
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "obtener_clima", # Igual al nombre de la funcion creada en Python
            "description": "Obtiene el clima actual de una ciudad",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "Nombre de la ciudad"
                    }
                },
                "required": ["ciudad"]
            }
        }
    }
]

# =========================
# MENSAJES
# =========================

ciudad = input("De que ciudad quiere consultar el clima? ").strip()

messages = [
    {
        "role": "user",
        "content": f"¿Cómo está el clima en {ciudad}?"
    }
]

# =========================
# PRIMERA LLAMADA AL MODELO
# =========================

response = client.chat.completions.create(
    model="gpt-5.5",
    messages=messages,
    tools=tools
)

message = response.choices[0].message

print("\n=== TOOL CALL GENERADA ===\n")
print(message.tool_calls)

# =========================
# EJECUTAR TOOL
# =========================

tool_call = message.tool_calls[0]

function_name = tool_call.function.name

arguments = json.loads(tool_call.function.arguments)

resultado = obtener_clima(arguments["ciudad"])

print("\n=== RESULTADO TOOL ===\n")
print(resultado)

# =========================
# DEVOLVER RESULTADO AL MODELO
# =========================

messages.append(message)

messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": json.dumps(resultado)
})

# =========================
# RESPUESTA FINAL
# =========================

final_response = client.chat.completions.create(
    model="gpt-5.5",
    messages=messages
)

print("\n=== RESPUESTA FINAL ===\n")
print(final_response.choices[0].message.content)