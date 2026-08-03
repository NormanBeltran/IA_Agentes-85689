import whisper

# Cargar el modelo (existen: tiny, base, small, medium, large)
# El modelo 'base' es rápido y consume poca memoria
model = whisper.load_model("base")

# Transcribir el archivo
result = model.transcribe("audio.mp3", fp16=False)

print(f"Texto detectado: {result['text']}")