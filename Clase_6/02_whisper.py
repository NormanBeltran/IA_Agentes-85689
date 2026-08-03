import whisper

model = whisper.load_model("small")

# Usamos la tarea 'translate'
result = model.transcribe("audio.mp3", task="translate", fp16=False)

print(f"Traducción al inglés: {result['text']}")