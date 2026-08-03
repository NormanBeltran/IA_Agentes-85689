import pyttsx3

engine = pyttsx3.init()

engine.say("Hola, soy una voz que funciona sin internet, puedo trabajar sin conexion.")

engine.runAndWait()