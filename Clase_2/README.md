# Clase 2

## Virtual Enviroments en Python

- Entornos aislados que nos permiten trabajar sin afectar el entorno de nuestro equipo
    - python -m venv [nombre_entorno]  (venv)
- Activar el entorno virtual
    - env\Scripts\activate
- Instalación de librerias dentro del venv
    - pip install requests
    - pip install -r requirements.txt (desde un archivo)
    - pip uninstall requests (desinstala la libreria requests)
    - pip freeze  
    - pip freeze > requirements.txt
    - pip list (lista todas las librerias de nuestro entorno)

## requests (libreria)

- Importar la libreria
- Crear una URL 
- Invocar a requests.get()  o el metodo HTTP correspondiente
    - timeout = 10 (quiere decir que voy a esperar 10 segundos)
- Si vamos a enviar parametros usar el atributo params
- Chequear el status code, usar el response.json(), y eventualmente la URL generada

## Ejemplo: requests.post

A continuación se muestra un ejemplo de cómo enviar un objeto JSON mediante una petición `POST` con `requests`.

```python
import requests

url = 'https://httpbin.org/post'
payload = {
    'nombre': 'Juan',
    'edad': 28,
    'ciudad': 'Buenos Aires'
}

response = requests.post(url, json=payload)

print('Código de estado:', response.status_code)
print('Encabezados de respuesta:', response.headers.get('Content-Type'))
print('Cuerpo de la respuesta JSON:')
print(response.json())
```

- `json=payload` envía los datos en formato JSON en el cuerpo de la petición.
- `response.status_code` permite verificar el resultado de la solicitud.
- `response.json()` parsea la respuesta JSON devuelta por el servidor.


## Modelos de IA

- Groq   https://groq.com/                          (Gratuito/Pago)
- Gemini https://aistudio.google.com                (Gratuito/Pago)
- OpenAI https://platform.openai.com/api-keys       (Pago)