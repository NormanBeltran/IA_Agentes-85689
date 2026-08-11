import gradio as gr
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Carga las variables del archivo .env
load_dotenv()
# Asegúrate de tener OPENAI_API_KEY en tu archivo .env
api_key = os.getenv('API_KEY_GROQ')
model = os.getenv('MODEL_GROQ')

# 2. Inicializa el cliente de OpenAI
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def responder(mensaje, historial):
    # 1. Configuración del sistema
    mensajes_ia = [{"role": "system", "content": "Eres un asistente inteligente, siempre respondes en español con respuestas concisas."}]
    
    # 2. Limpiamos el historial para OpenAI
    for entrada in historial:
        if isinstance(entrada, dict):
            # Extraemos SOLO role y content, ignorando metadatos de Gradio
            mensajes_ia.append({
                "role": entrada.get("role"),
                "content": entrada.get("content")
            })
        elif isinstance(entrada, (list, tuple)):
            # Soporte para versiones antiguas de Gradio
            mensajes_ia.append({"role": "user", "content": entrada[0]})
            mensajes_ia.append({"role": "assistant", "content": entrada[1]})
    
    # 3. Añadimos el mensaje actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    # 4. Llamada a la API
    try:
        response = client.chat.completions.create(
            model=model, 
            messages=mensajes_ia,
            temperature=0.7,
            stream=True
        )

        respuesta_completa = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                respuesta_completa += chunk.choices[0].delta.content
                #print(respuesta_completa, "\n")
                yield respuesta_completa
    except Exception as e:
        yield f"Error al conectar con la API: {str(e)}"

# 3. Interfaz de Gradio (ChatInterface maneja el historial por ti)
demo = gr.ChatInterface(
    fn=responder,
    title="Chatbot con Groq + Gradio",
    description="Interfaz profesional con memoria de conversación.",
    examples=["¿Qué es Python?", "Dame un ejemplo de bucle for"],
    cache_examples=False,
)

if __name__ == "__main__":
    demo.launch(share=False)