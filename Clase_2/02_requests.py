import requests

url = "https://jsonplaceholder.typicode.com/posts"
params = {
    "userId": 1
}

response = requests.get(url, params=params)

print(f"Status {response.status_code}")
print(f"JSON {response.json()}")
print(f"URL {response.url}")