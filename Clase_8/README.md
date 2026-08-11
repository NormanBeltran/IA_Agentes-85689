# Gradio

- https://gradio.app/
- Rutas de aprendizaje: Basico, Intermedio, Avanzado, Integración
- Importar Gradio: pip install gradio

## Forma de trabajo con gradio

- Entrada de usuario
- Función de Python
- Salida / resultado

## Docker

- https://www.docker.com/
- Containers se puede bajar de: https://hub.docker.com/

## RAG / Gradio + ( Postgres + pgvector ) + Groq
##                [_______Container_____]

- Instalar las librerias desde requirements.txt
    - pip install -r requirements.txt
- Levantar Postgres: 
    - docker compose up -d

- Desarrollar la app.py con Gradio para que realice RAG y Chatbot sobre el contenido de información privada