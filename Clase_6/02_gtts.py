from gtts import gTTS
import os

tts = gTTS("Reproduciendo audio directamente.", lang='es', tld="com.mx")
tts.save("temp.mp3")

# En Windows
os.system("start temp.mp3")

# En Linux
# os.system("mpg321 ....")

# En Mac
# os.system("afplay ...")