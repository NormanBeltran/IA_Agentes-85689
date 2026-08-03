from openai import OpenAI
from dotenv import load_dotenv
from agent import Agent
import os

load_dotenv()

# Leer configuración externa
API_KEY = os.getenv("API_KEY_OPENAI")
MODEL = os.getenv("MODEL_OPENAI_TOOLS")

print("Mi primer agente de IA")

client = OpenAI(api_key=API_KEY)
agent = Agent()

while True:
    user_input = input("Tú: ").strip()
    
    #Validaciones
    if not user_input:
        continue
    
    if user_input.lower() in ("salir", "exit", "bye", "sayonara"):
        print("Hasta luego!")
        break
    
    #Agregar nuestro mensaje al historial
    agent.messages.append({"role": "user", "content": user_input})
    
    while True:
        response = client.responses.create(
            model=MODEL,
            input=agent.messages,
            tools=agent.tools
        )
        
        called_tool = agent.process_response(response)
        
        #Si no se llamo herramienta, tenemos la respuesta final
        if not called_tool:
            break
        
        