import pyttsx3

engine = pyttsx3.init()

# --- VELOCIDAD (Rate) ---
rate = engine.getProperty('rate')   # Obtener velocidad actual (por defecto suele ser 200)
engine.setProperty('rate', 150)     # Bajarla a 150 para que sea más claro

# --- VOLUMEN (Volume) ---
volume = engine.getProperty('volume') # Nivel actual
engine.setProperty('volume', 0.8)     # Configurar al 80%

engine.say("Estoy hablando un poco más lento y con volumen moderado.")
engine.runAndWait()