# pip install openai pandas openpyxl matplotlib
import json
import pandas as pd
import traceback

import matplotlib.pyplot as plt
from openai import OpenAI

from dotenv import load_dotenv

import os

# =========================
# ENV
# =========================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY_OPENAI")
)

# ==================================================
# CONFIGURACIÓN
# ==================================================

MODEL = "gpt-5"


# ==================================================
# CARGA DEL EXCEL
# ==================================================

df = pd.read_excel("datos_ventas.xlsx")

# Convertimos fecha si existe

if "Fecha" in df.columns:
    df["Fecha"] = pd.to_datetime(df["Fecha"])

# ==================================================
# TOOL 1
# EJECUTAR PANDAS
# ==================================================

def ejecutar_query_pandas(codigo):

    """
    Ejecuta código pandas generado por GPT.

    Debe devolver el resultado en una variable llamada resultado.
    """

    try:

        entorno = {
            "pd": pd,
            "df": df.copy()
        }

        exec(codigo, {}, entorno)

        resultado = entorno.get("resultado")

        if resultado is None:
            return json.dumps({
                "error": "No se encontró variable resultado"
            })

        if isinstance(resultado, pd.DataFrame):
            return resultado.to_json(orient="records")

        if isinstance(resultado, pd.Series):
            return resultado.to_json()

        return json.dumps({
            "resultado": str(resultado)
        })

    except Exception as e:

        return json.dumps({
            "error": str(e),
            "traceback": traceback.format_exc()
        })

# ==================================================
# TOOL 2
# GENERAR GRÁFICOS
# ==================================================

def generar_grafico(codigo):

    """
    GPT genera código matplotlib.

    Debe crear un gráfico usando df.
    """

    try:

        entorno = {
            "pd": pd,
            "plt": plt,
            "df": df.copy()
        }

        exec(codigo, {}, entorno)

        archivo = "./grafico.png"

        plt.tight_layout()
        plt.savefig(archivo)
        plt.close()

        return json.dumps({
            "archivo": archivo,
            "mensaje": "Gráfico generado correctamente"
        })

    except Exception as e:

        return json.dumps({
            "error": str(e),
            "traceback": traceback.format_exc()
        })

# ==================================================
# TOOLS OPENAI
# ==================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "ejecutar_query_pandas",
            "description": """
            Ejecuta consultas Pandas sobre el dataframe df.
            Utilizar para responder preguntas analíticas.
            El código debe guardar la respuesta en una variable llamada resultado.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string"
                    }
                },
                "required": ["codigo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generar_grafico",
            "description": """
            Genera gráficos utilizando matplotlib.
            El dataframe disponible es df.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string"
                    }
                },
                "required": ["codigo"]
            }
        }
    }
]

# ==================================================
# REGISTRO DE FUNCIONES
# ==================================================

available_functions = {
    "ejecutar_query_pandas": ejecutar_query_pandas,
    "generar_grafico": generar_grafico
}

# ==================================================
# SYSTEM PROMPT
# ==================================================

SYSTEM_PROMPT = f"""
Eres un analista de negocios experto.

Dispones de un dataframe llamado df cargado desde Excel.

Columnas disponibles:

{list(df.columns)}

Reglas:

1. Para preguntas analíticas usa ejecutar_query_pandas.

2. El código debe guardar la respuesta
en una variable llamada resultado.

Ejemplo:

resultado = (
    df.groupby("Producto")["Cantidad"]
    .sum()
    .sort_values(ascending=False)
)

3. Si el usuario pide un gráfico,
usa generar_grafico.

Ejemplo:

ventas = (
    df.groupby("Producto")["Cantidad"]
    .sum()
)

ventas.plot(kind="bar")

4. Nunca inventes datos.

5. Siempre utiliza las herramientas disponibles.
"""

# ==================================================
# LOOP PRINCIPAL
# ==================================================

while True:

    pregunta = input("\nUsuario: ")

    if pregunta.lower() in ["salir", "exit", "quit"]:
        break

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": pregunta
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:

        messages.append(response_message)

        for tool_call in response_message.tool_calls:

            function_name = tool_call.function.name

            function_args = json.loads(
                tool_call.function.arguments
            )

            function_to_call = available_functions[
                function_name
            ]

            function_response = function_to_call(
                **function_args
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_response
                }
            )

        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )

        print(
            "\nAGENTE:\n",
            second_response.choices[0].message.content
        )

    else:

        print(
            "\nAGENTE:\n",
            response_message.content
        )