import requests

url = "https://jsonplaceholder.typicode.com/posts"

response = requests.get(url)

print(f"Status {response.status_code}")
print(f"JSON {response.json()}")
