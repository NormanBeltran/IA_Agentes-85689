# LLMs Grandes Modelos de Lenguaje

- LM STUDIO https://lmstudio.ai/
- Ollama https://ollama.com/

## Requemientos mínimos recomendables para correr modelos locales

- Intel generación 12 - Pentium 7 - Cores / AMD Ryzen 7 en adelante
- Con GPU
- 32 GB RAM 

## Como se calculan los token de input / output

https://platform.openai.com/tokenizer

# Conexión con APIs de diferentes modelos de IA

## GROQ

- pip install python-dotenv
- pip install groq
- Crear en el .env la variable MODEL_GROQ con "openai/gpt-oss-20b"

## GEMINI

- pip install google-genai
- Crear en el .env la variable API_KEY_GEMINI="xxxxxxxx"
- Crear en el .env la variable MODEL_GEMINI con "gemini-3-flash-preview"

## OPENAI

- pip install openai
- Crear en el .env la variable API_KEY_OPENAI="xxxxxxxx"
- Crear en el .env la variable MODEL_OPENAI con "gpt-4o-mini"

## HUGGING FACE

- El sitio donde se publican diferentes modelos de IA
- https://huggingface.co