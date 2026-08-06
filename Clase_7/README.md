# Clase 7 - IA Creación de contenido multimedia

## Estrategias de aplicación de modelos de IA en ambientes corporativos

- Información Pública (no privada) 
- Información Privada (no quiere exportar a un modelo de IA)
    - Trabajar con modelos locales 
        - Hostear en nube privada (VM) ¿? **Sizing de hardware**
          - Subir documentos pdf / txt y crear un chatbot que responda sobre esa información
            - Cuantos usuarios van a acceder a ese chatbot? Concurrencia ?
          - Crear un agente que trate información multimedia (imagenes / audio)
            - Procesos automáticos / Cuantos procesos son? Frecuencia ?
        - MaaS (Model as a Service)
          - Hosting de modelos (API)
          - https://support.huaweicloud.com/intl/en-us/productdesc-maas/productdesc_maas_0002.html
          
    - Trabajar con modelos "Publicos" (ChatGPT, Claude, etc) con información privada
        - RAG Retrieval Augmented Generation
    - Trabajar con modelos entrenados de la compañía
        - Fine Tunning + Entrenamiento de modelos

## Bases de Datos Vectoriales
    - Postgres + Vector
    - Casandra 
    - PinneCone 
    - SQL Server (2025) 

## Open Router

- https://openrouter.ai/
- MODEL_OR_IMG = "perceptron/perceptron-mk1"

## Tratamiento de imagenes 

- pip install pillow

### Modelo gratuito tratamiento de imagenes
- Pollinations

## Embeddings
- Proceso que parte un texto / pdf en chuncks para generar vectores y guardarlos en la BD vectorial
- Parametros: el tamaño de cada chunk

## STT Speech to text
- Vosk 
- pip install  vosk sounddevice
- https://alphacephei.com/vosk/models 
    - El modelo de 1.4G en Español es mucho mas fidedigno