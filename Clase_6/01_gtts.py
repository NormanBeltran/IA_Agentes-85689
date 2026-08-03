from gtts import gTTS
from pydub import AudioSegment

texto = """
Bajo la luna de plata y de tul,
camina el gigante de piel y lucero,
un sabio elefante de tono azul
que cruza soñando el espeso sendero.
"""

# Crear el objeto gtts

tts = gTTS(text=texto, lang="es", slow="False", tld="com.ar") # tld="es", "com.mx", "com"

tts.save("audio.mp3")
