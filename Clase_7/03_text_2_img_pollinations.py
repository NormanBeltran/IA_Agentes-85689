import requests

prompt = "A mouse looking the moon in a sunset"
url = f"https://image.pollinations.ai/prompt/{prompt}"

response = requests.get(url)
with open("mouse.jpg", "wb") as f:
    f.write(response.content)