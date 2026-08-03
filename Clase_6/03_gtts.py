from gtts import gTTS

def crear_audiolibro(nombre_archivo):
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        tts = gTTS(text=contenido, lang='es', tld="com.co")
        tts.save("audiolibro.mp3")
        print("Lectura completada con éxito.")
    except FileNotFoundError:
        print("El archivo no existe.")

# Uso
crear_audiolibro("mi_cuento.txt")