import json
import queue
import time

import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel


# ============================================================
# PARÁMETROS DE CONFIGURACIÓN
# ============================================================

# Ruta donde se encuentra el modelo de idioma de Vosk.
# La carpeta debe contener subcarpetas como am, conf, graph, etc.
MODEL_PATH = r"C:\EducacionIT\Python IA Agentes\85689\Clase_7\vosk-es"

# Frecuencia de muestreo del audio.
# Vosk suele trabajar correctamente con 16000 Hz para reconocimiento de voz.
SAMPLE_RATE = 16000

# Cantidad de segundos consecutivos de silencio necesarios
# para finalizar la grabación.
#
# Ejemplos:
# 1 segundo  → corte rápido.
# 2 segundos → permite pausas normales al hablar.
# 3 segundos → recomendable para dictado más pausado.
SILENCE_SECONDS = 2

# Nivel mínimo de energía para considerar que existe voz.
#
# Si el valor es demasiado bajo:
# puede interpretar ruido ambiente como si fuera voz.
#
# Si el valor es demasiado alto:
# puede no detectar una voz baja o lejana.
#
# Valores orientativos:
# 200 a 400  → ambiente silencioso.
# 500        → valor inicial recomendado.
# 700 a 1000 → ambiente con más ruido.
ENERGY_THRESHOLD = 500

# Cola utilizada para almacenar temporalmente
# los bloques de audio recibidos desde el micrófono.
audio_queue = queue.Queue()


def callback(indata, frames, callback_time, status):
    """
    Esta función se ejecuta automáticamente cada vez que
    el micrófono entrega un nuevo bloque de audio.
    """
    audio_queue.put(bytes(indata))


def calcular_energia(audio):
    """
    Calcula el nivel de energía del bloque de audio.

    Cuanto mayor sea el resultado, más fuerte es el sonido.
    """
    muestras = np.frombuffer(
        audio,
        dtype=np.int16
    ).astype(np.float32)

    return np.sqrt(np.mean(muestras**2))


# Oculta los mensajes internos de Vosk y Kaldi.
# -1 significa que prácticamente no se muestran logs.
SetLogLevel(-1)

# Carga el modelo de reconocimiento en español.
modelo = Model(MODEL_PATH)

# Crea el reconocedor indicando el modelo y la frecuencia de audio.
reconocedor = KaldiRecognizer(
    modelo,
    SAMPLE_RATE
)

# Lista donde se irán guardando los segmentos reconocidos.
texto_completo = []

# Indica si ya se detectó que la persona comenzó a hablar.
# Esto evita que el programa termine antes de que el usuario hable.
comenzo_a_hablar = False

# Guarda el momento exacto en el que se detectó voz por última vez.
ultimo_momento_con_voz = None

print(
    "Hable... El programa cortará después "
    "de 2 segundos de silencio."
)

with sd.RawInputStream(
    # Frecuencia de captura del micrófono.
    samplerate=SAMPLE_RATE,

    # Cantidad de muestras procesadas en cada bloque.
    #
    # Con 16000 Hz:
    # 4000 / 16000 = 0,25 segundos por bloque.
    #
    # Un número menor detecta el silencio más rápido,
    # pero procesa más bloques por segundo.
    blocksize=4000,

    # Formato de cada muestra de audio.
    # int16 es compatible con Vosk.
    dtype="int16",

    # Un solo canal porque trabajamos con audio mono.
    channels=1,

    # Función que recibirá cada bloque de audio.
    callback=callback,
):
    while True:
        # Espera hasta recibir un bloque desde el micrófono.
        audio = audio_queue.get()

        # Calcula el volumen o energía del bloque.
        energia = calcular_energia(audio)

        # Si la energía supera el umbral configurado,
        # consideramos que la persona está hablando.
        if energia > ENERGY_THRESHOLD:
            comenzo_a_hablar = True

            # Actualizamos el último instante donde hubo voz.
            ultimo_momento_con_voz = time.monotonic()

        # Envía el bloque de audio a Vosk.
        if reconocedor.AcceptWaveform(audio):
            resultado = json.loads(
                reconocedor.Result()
            )

            texto = resultado.get("text", "")

            if texto:
                texto_completo.append(texto)

        # Calcula cuánto tiempo pasó desde la última detección de voz.
        #
        # El programa solamente corta si:
        # 1. La persona ya comenzó a hablar.
        # 2. Existe un registro del último momento con voz.
        # 3. Pasaron al menos 2 segundos sin detectar voz.
        if (
            comenzo_a_hablar
            and ultimo_momento_con_voz is not None
            and time.monotonic() - ultimo_momento_con_voz
            >= SILENCE_SECONDS
        ):
            print(
                "\nSe detectaron "
                f"{SILENCE_SECONDS} segundos de silencio."
            )
            break


# Recupera cualquier texto que todavía haya quedado pendiente.
resultado_final = json.loads(
    reconocedor.FinalResult()
)

texto_final = resultado_final.get("text", "")

if texto_final:
    texto_completo.append(texto_final)

print(
    "Transcripción:",
    " ".join(texto_completo)
)