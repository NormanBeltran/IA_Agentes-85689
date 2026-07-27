# Interfaces con otros modelos

## HuggingFace

- https://huggingface.co/docs/inference-providers/index
- https://huggingface.co/models?inference_provider=hf-inference&sort=trending (Modelos de HF para conectar por API)
- https://huggingface.co/settings/tokens (como obtener access tokens por API)
- Modelo del Ejemplo: Qwen/Qwen2.5-Coder-7B-Instruct

## Ollama

- ollama list (muestra los modelos en el equipo)
- ollama pull [nombre_modelo]
- ollama run [nombre_modelo] 
- Modelo para bajos recursos de hardware: gemma3:270m

## LMS 

- Requiere API que se genera a traves de la plataforma de LMS
- La URL de conexión es http://localhost:1234/v1
- El modelo se descarga desde la pltaforma
