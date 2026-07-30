import json
from typing import Any

from config import MODEL, client


def calcular_porcentaje(
    valor: float,
    porcentaje: float,
) -> dict[str, float]:
    incremento = valor * porcentaje / 100

    return {
        "valor_original": valor,
        "porcentaje": porcentaje,
        "incremento": incremento,
        "resultado": valor + incremento,
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calcular_porcentaje",
            "description": (
                "Calcula un incremento porcentual sobre un valor "
                "y devuelve el total."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "valor": {
                        "type": "number",
                        "description": "Valor base.",
                    },
                    "porcentaje": {
                        "type": "number",
                        "description": "Porcentaje que se aplicará.",
                    },
                },
                "required": ["valor", "porcentaje"],
                "additionalProperties": False,
            },
        },
    }
]


FUNCTIONS = {
    "calcular_porcentaje": calcular_porcentaje,
}


def ejecutar_herramienta(
    nombre: str,
    argumentos: dict[str, Any],
) -> Any:
    funcion = FUNCTIONS.get(nombre)

    if funcion is None:
        raise ValueError(f"Herramienta desconocida: {nombre}")

    return funcion(**argumentos)


def ejecutar_agente(pregunta: str) -> str:
    mensajes = [
        {
            "role": "system",
            "content": """
            Sos un agente financiero.
            Usá las herramientas disponibles para hacer cálculos.
            No calcules porcentajes mentalmente cuando exista una herramienta.
            Explicá el resultado en español.
            """,
        },
        {
            "role": "user",
            "content": pregunta,
        },
    ]

    print("============================================= Primer llamada")
    primera_respuesta = client.chat.completions.create(
        model=MODEL,
        messages=mensajes,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0,
    )

    mensaje_modelo = primera_respuesta.choices[0].message
    #print(f"Mensaje modelo: {mensaje_modelo}")
    mensajes.append(mensaje_modelo)
    print(f"==================== MENSAJE MODELO ========================= {mensaje_modelo}")
    if not mensaje_modelo.tool_calls:
        return mensaje_modelo.content or ""

    for llamada in mensaje_modelo.tool_calls:
        nombre = llamada.function.name
        argumentos = json.loads(llamada.function.arguments)
        #print(f"Nombre: {nombre}, Argumentos: {argumentos}")
        resultado = ejecutar_herramienta(
            nombre=nombre,
            argumentos=argumentos,
        )
        print(f"================= RESULTADO ============================ {resultado}")
        mensajes.append(
            {
                "role": "tool",
                "tool_call_id": llamada.id,
                "content": json.dumps(
                    resultado,
                    ensure_ascii=False,
                ),
            }
        )

    print(f"============================================= SEGUNDA LLAMADA AL MODELO")
    respuesta_final = client.chat.completions.create(
        model=MODEL,
        messages=mensajes,
        tools=TOOLS,
        temperature=0,
    )

    return respuesta_final.choices[0].message.content


if __name__ == "__main__":
    resultado = ejecutar_agente(
        "Un proyecto cuesta USD 18.500. "
        "Debemos agregarle un 30%. "
        "¿Cuál es el valor final?"
    )

    print(resultado)