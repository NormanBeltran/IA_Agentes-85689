import pyttsx3

engine = pyttsx3.init()

texto_largo = "Este audio se guardará directamente en un archivo de sonido local."

# Guardar a archivo
engine.save_to_file(texto_largo, 'salida_pyttsx3.mp3') # 'salida_pyttsx3.wav'

engine.runAndWait()
print("Audio exportado correctamente.")