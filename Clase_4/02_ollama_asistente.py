import ollama

response = ollama.chat(
    model="gemma3:270m",
    messages=[
        {
        'role': 'user',
        'content': 'Cual es la capital de España?',
        'temperature': 0
        }
    ]                       
)

print(response['message']['content'])