from config import MODEL, client


SYSTEM_PROMPT = """
Sos un agente de soporte técnico especializado en Python.

Tu objetivo es ayudar a diagnosticar problemas técnicos o de ejecución.

Reglas:
1. Analizá el síntoma antes de sugerir una solución.
2. Explicá las posibles causas de mayor a menor probabilidad.
3. Proponé comandos seguros para comprobar cada hipótesis.
4. No inventes resultados de comandos.
5. Antes de sugerir una acción destructiva, advertí al usuario.
6. Respondé en español.
7. Si te consultan algo fuera de tu perfil y tu objetivo, contesta amablemente que no estas habilitado a responder esa pregunta.
"""


def ejecutar_agente(mensaje_usuario: str) -> str:
    respuesta = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": mensaje_usuario,
            },
        ],
        temperature=0.2,
        max_completion_tokens=1000,
    )

    return respuesta.choices[0].message.content


if __name__ == "__main__":
    consulta = input("¿En qué te puedo ayudar? ")

    resultado = ejecutar_agente(consulta)
    print(resultado)