import requests

url = "https://jsonplaceholder.typicode.com/posts"
data = {
    "title": "Demo de requests con Python",
    "body": "Esta es una prueba y el body",
    "userID": 1
}

# Diferencia es el método
response = requests.post(url, json=data)

print(f"Status {response.status_code}")
print(f"JSON {response.json()}")
print(f"URL {response.url}")