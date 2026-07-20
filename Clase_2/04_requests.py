import requests

url = 'https://httpbin.org/post'
payload = {
    'nombre': 'Juan',
    'edad': 28,
    'ciudad': 'Buenos Aires'
}

# Enviar datos JSON en una petición POST
response = requests.post(url, json=payload)

print('Código de estado:', response.status_code)
print('Encabezados de respuesta:', response.headers.get('Content-Type'))
print('Cuerpo de la respuesta JSON:')
print(response.json())
