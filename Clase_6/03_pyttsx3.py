import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for index, voice in enumerate(voices):
    # Forzamos la inicialización en cada vuelta
    engine = pyttsx3.init() 
    
    # IMPORTANTE: Usamos el ID exacto del registro
    engine.setProperty('voice', voice.id)
    
    print(f"Hablando con: {voice.name}")
    engine.say(f"Probando la voz número {index}")
    
    engine.runAndWait()
    # Liberamos el motor completamente antes de la siguiente vuelta
    del engine

print("\nPrueba de voces finalizada.")