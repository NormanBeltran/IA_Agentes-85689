# ============================================================
# RAG CON STREAMLIT + POSTGRESQL + PGVECTOR + GROQ
# ============================================================
#
# Flujo:
#
# Documento
#    ↓
# Chunking
#    ↓
# Embeddings
#    ↓
# PostgreSQL + pgvector
#    ↓
# Pregunta del usuario
#    ↓
# Embedding de la pregunta
#    ↓
# Búsqueda semántica
#    ↓
# Contexto recuperado
#    ↓
# Groq / LLM
#    ↓
# Respuesta
#
# ============================================================

import os

import psycopg
import streamlit as st

from dotenv import load_dotenv
from groq import Groq
from pgvector.psycopg import register_vector
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. VARIABLES DE ENTORNO
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "ragdb")
DB_USER = os.getenv("DB_USER", "raguser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ragpass")

GROQ_API_KEY = os.getenv("API_KEY_GROQ")
GROQ_MODEL = os.getenv(
    "MODEL_GROQ",
    "llama-3.3-70b-versatile"
)


# ============================================================
# 2. MODELO DE EMBEDDINGS
# ============================================================

# Este modelo genera vectores de 384 dimensiones.
# Es multilingüe y funciona bien con textos en español.
EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# ============================================================
# 3. CONFIGURACIÓN STREAMLIT
# ============================================================

st.set_page_config(
    page_title="RAG con PostgreSQL",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# 4. CARGAR MODELO DE EMBEDDINGS
# ============================================================

@st.cache_resource
def cargar_modelo_embeddings():
    """
    Carga SentenceTransformer una sola vez.

    Streamlit vuelve a ejecutar el script ante cada interacción.
    st.cache_resource evita recargar el modelo en cada ejecución.
    """
    return SentenceTransformer(EMBEDDING_MODEL)


embedding_model = cargar_modelo_embeddings()


# ============================================================
# 5. CLIENTE GROQ
# ============================================================

def obtener_cliente_groq():
    """
    Crea el cliente de Groq.

    La API KEY debe estar configurada en:
    GROQ_API_KEY dentro del archivo .env
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "TU_API_KEY_DE_GROQ":
        raise ValueError(
            "Configurá GROQ_API_KEY en el archivo .env"
        )

    return Groq(api_key=GROQ_API_KEY)


# ============================================================
# 6. CONEXIÓN A POSTGRESQL
# ============================================================

def obtener_conexion():
    """
    Se conecta con PostgreSQL.

    Docker publica:
        localhost:5433 -> contenedor:5432

    Por eso Python se conecta al puerto 5433.
    """

    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    # Hace que Psycopg comprenda el tipo VECTOR de pgvector.
    register_vector(conn)

    return conn


# ============================================================
# 7. LEER DOCUMENTO
# ============================================================

def leer_documento(archivo):
    """
    Lee archivos TXT o PDF cargados desde Streamlit.

    Retorna:
        str con todo el texto extraído.
    """

    nombre = archivo.name.lower()

    # -----------------------------
    # TXT
    # -----------------------------
    if nombre.endswith(".txt"):
        return archivo.getvalue().decode(
            "utf-8",
            errors="ignore"
        )

    # -----------------------------
    # PDF
    # -----------------------------
    if nombre.endswith(".pdf"):
        reader = PdfReader(archivo)

        paginas = []

        for pagina in reader.pages:
            texto = pagina.extract_text()

            if texto:
                paginas.append(texto)

        return "\n".join(paginas)

    raise ValueError(
        "Formato no soportado. Utilizá TXT o PDF."
    )


# ============================================================
# 8. CHUNKING
# ============================================================

def dividir_texto(
    texto,
    tamanio_chunk=1000,
    overlap=150
):
    """
    Divide un texto largo en fragmentos.

    Ejemplo con chunk=1000 y overlap=150:

        Chunk 1 -> caracteres    0 a 1000
        Chunk 2 -> caracteres  850 a 1850
        Chunk 3 -> caracteres 1700 a 2700

    El overlap permite conservar parte del contexto entre
    fragmentos consecutivos.
    """

    chunks = []
    inicio = 0

    while inicio < len(texto):

        fin = inicio + tamanio_chunk

        chunk = texto[inicio:fin].strip()

        if chunk:
            chunks.append(chunk)

        inicio += tamanio_chunk - overlap

    return chunks


# ============================================================
# 9. GENERAR EMBEDDING
# ============================================================

def generar_embedding(texto):
    """
    Convierte texto en un vector numérico.

    Ejemplo conceptual:

        "Python se utiliza para Data Science"
                    ↓
        SentenceTransformer
                    ↓
        [0.043, -0.125, ..., 0.091]

    El vector resultante posee 384 dimensiones.
    """

    return embedding_model.encode(
        texto,
        normalize_embeddings=True
    )


# ============================================================
# 10. GUARDAR DOCUMENTO EN POSTGRESQL
# ============================================================

def guardar_documento(filename, chunks):
    """
    Guarda cada fragmento del documento junto con su embedding.

    Si el archivo ya había sido procesado, primero se eliminan
    los chunks anteriores para evitar duplicados.
    """

    conn = obtener_conexion()

    try:
        with conn.cursor() as cursor:

            # Eliminar versión anterior del mismo documento.
            cursor.execute(
                """
                DELETE FROM documents
                WHERE filename = %s
                """,
                (filename,)
            )

            # Procesar cada fragmento.
            for indice, chunk in enumerate(chunks):

                embedding = generar_embedding(chunk)

                cursor.execute(
                    """
                    INSERT INTO documents
                    (
                        filename,
                        chunk_index,
                        content,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        filename,
                        indice,
                        chunk,
                        embedding
                    )
                )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# 11. BUSCAR DOCUMENTOS POR SIMILITUD
# ============================================================

def buscar_documentos(
    pregunta,
    cantidad=4
):
    """
    RETRIEVAL DEL RAG.

    1. Convierte la pregunta en embedding.
    2. PostgreSQL compara el embedding de la pregunta con
       los embeddings almacenados.
    3. Retorna los fragmentos semánticamente más próximos.

    En pgvector:

        <=> = distancia coseno

    Cuanto menor sea la distancia, más parecidos son los
    vectores.

    Para mostrar una similitud intuitiva usamos:

        1 - distancia_coseno
    """

    query_embedding = generar_embedding(
        pregunta
    )

    conn = obtener_conexion()

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    filename,
                    chunk_index,
                    content,
                    1 - (embedding <=> %s) AS similarity

                FROM documents

                ORDER BY embedding <=> %s

                LIMIT %s
                """,
                (
                    query_embedding,
                    query_embedding,
                    cantidad
                )
            )

            return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# 12. CONTAR DOCUMENTOS
# ============================================================

def obtener_estadisticas():
    """
    Retorna cantidad de archivos y chunks almacenados.
    """

    conn = obtener_conexion()

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    COUNT(DISTINCT filename),
                    COUNT(*)
                FROM documents
                """
            )

            return cursor.fetchone()

    finally:
        conn.close()


# ============================================================
# 13. GENERATION - RESPUESTA CON GROQ
# ============================================================

def generar_respuesta(
    pregunta,
    documentos
):
    """
    GENERATION DEL RAG.

    Recibe los chunks recuperados y crea un contexto.

    Luego envía al LLM:
        - instrucciones
        - contexto
        - pregunta

    El modelo debe contestar solamente basándose en el
    contenido recuperado.
    """

    contexto = ""

    for documento in documentos:

        filename = documento[0]
        chunk_index = documento[1]
        content = documento[2]

        contexto += f"""
FUENTE: {filename}
FRAGMENTO: {chunk_index}

{content}

--------------------------------------------------
"""

    # --------------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------------

    system_prompt = """
Eres un asistente basado en RAG.

Debes responder EXCLUSIVAMENTE utilizando la información
contenida en el CONTEXTO proporcionado.

No utilices conocimiento externo para completar información.

Si el contexto no contiene información suficiente para
contestar la pregunta, responde exactamente:

"No encuentro esa información en los documentos cargados."

Cuando corresponda, menciona el nombre del documento utilizado
como fuente.
"""

    # --------------------------------------------------------
    # AUGMENTED PROMPT
    # --------------------------------------------------------

    user_prompt = f"""
CONTEXTO RECUPERADO:

{contexto}


PREGUNTA DEL USUARIO:

{pregunta}
"""

    client = obtener_cliente_groq()

    completion = client.chat.completions.create(
        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        # Temperatura baja para respuestas más deterministas.
        temperature=0.1
    )

    return completion.choices[0].message.content


# ============================================================
# 14. INTERFAZ
# ============================================================

st.title(
    "🤖 RAG con Streamlit + PostgreSQL + pgvector"
)

st.markdown(
    """
Esta aplicación implementa un **RAG completo** sin utilizar
LangChain para poder observar claramente cada una de sus etapas:

**Documento → Chunking → Embeddings → PostgreSQL → Retrieval → Groq**
"""
)


# ============================================================
# 15. SIDEBAR - CARGA DE DOCUMENTOS
# ============================================================

with st.sidebar:

    st.header("📚 Base de conocimiento")

    archivo = st.file_uploader(
        "Cargar documento",
        type=["txt", "pdf"]
    )

    if archivo:

        st.caption(
            f"Archivo: {archivo.name}"
        )

        if st.button(
            "Procesar documento",
            type="primary",
            use_container_width=True
        ):

            try:
                with st.spinner(
                    "Leyendo, fragmentando y vectorizando..."
                ):

                    # 1. Extraer texto
                    texto = leer_documento(
                        archivo
                    )

                    if not texto.strip():
                        raise ValueError(
                            "No se pudo extraer texto del documento."
                        )

                    # 2. Crear chunks
                    chunks = dividir_texto(
                        texto
                    )

                    # 3. Embeddings + PostgreSQL
                    guardar_documento(
                        archivo.name,
                        chunks
                    )

                st.success(
                    f"Documento procesado: {len(chunks)} chunks."
                )

            except Exception as e:
                st.error(
                    f"Error al procesar el documento: {e}"
                )

    st.divider()

    # --------------------------------------------------------
    # Estadísticas PostgreSQL
    # --------------------------------------------------------

    st.subheader("📊 PostgreSQL")

    try:
        archivos, chunks = obtener_estadisticas()

        st.metric(
            "Documentos",
            archivos
        )

        st.metric(
            "Chunks",
            chunks
        )

        st.caption(
            "PostgreSQL: localhost:5434"
        )

    except Exception:
        st.warning(
            "PostgreSQL no está disponible."
        )


# ============================================================
# 16. CHAT
# ============================================================

st.header("💬 Consultar documentos")

pregunta = st.chat_input(
    "Realizá una pregunta..."
)


if pregunta:

    # --------------------------------------------------------
    # Mostrar pregunta
    # --------------------------------------------------------

    with st.chat_message("user"):
        st.write(pregunta)

    try:
        # ----------------------------------------------------
        # RETRIEVAL
        # ----------------------------------------------------

        documentos = buscar_documentos(
            pregunta,
            cantidad=4
        )

        if not documentos:

            with st.chat_message("assistant"):
                st.warning(
                    "No hay documentos cargados en PostgreSQL."
                )

        else:
            # ------------------------------------------------
            # GENERATION
            # ------------------------------------------------

            respuesta = generar_respuesta(
                pregunta,
                documentos
            )

            with st.chat_message("assistant"):
                st.write(respuesta)

            # ------------------------------------------------
            # Explicabilidad del RAG
            # ------------------------------------------------

            with st.expander(
                "🔎 Ver chunks recuperados por el RAG"
            ):

                for documento in documentos:

                    filename = documento[0]
                    chunk = documento[1]
                    contenido = documento[2]
                    similarity = documento[3]

                    st.markdown(
                        f"""
**Archivo:** `{filename}`  
**Chunk:** `{chunk}`  
**Similitud coseno:** `{similarity:.4f}`
"""
                    )

                    st.write(contenido)

                    st.divider()

    except Exception as e:

        with st.chat_message("assistant"):
            st.error(
                f"Error: {e}"
            )