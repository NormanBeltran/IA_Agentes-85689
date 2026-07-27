from openai import OpenAI

def consultar_lm_studio(pregunta):
    # 1. Configurar el cliente apuntando al servidor local de LM Studio
    # La API Key no es necesaria para LM Studio, pero la librería pide un string cualquiera
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="sk-lm-MuDxnem2:7IINKzxBKyx4bF0msdOh")

    try:
        # 2. Realizar la consulta
        # Nota: El parámetro 'model' puede ser cualquier texto en LM Studio 
        # siempre que ya tengas un modelo cargado en el servidor.
        completion = client.chat.completions.create(
            model="liquid/lfm2.5-1.2b", 
            messages=[
                {"role": "system", "content": "Eres un profesor de IA experto y conciso."},
                {"role": "user", "content": pregunta}
            ],
            temperature=0,
        )

        # 3. Extraer y retornar el texto de la respuesta
        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Error de conexión: Asegúrate de que el servidor de LM Studio esté encendido. {e}"

# --- Ejemplo de uso ---
if __name__ == "__main__":
    usuario_input = "Explicame que es la cuantizacion de una manera muy simple"
    
    print("🤖 Procesando respuesta...")
    respuesta = consultar_lm_studio(usuario_input)
    
    print("-" * 30)
    print(f"🤖 Respuesta del modelo:\n{respuesta}")
    print("-" * 30)