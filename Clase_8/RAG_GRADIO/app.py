import os
from pathlib import Path

import gradio as gr
import numpy as np
import psycopg
from dotenv import load_dotenv
from groq import Groq
from pgvector.psycopg import register_vector
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "ragdb")
DB_USER = os.getenv("POSTGRES_USER", "raguser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ragpass")

GROQ_API_KEY = os.getenv("API_KEY_GROQ")
GROQ_MODEL = os.getenv("MODEL_GROQ", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise ValueError(
        "API_KEY_GROQ no está definida. "
        "Copiá .env.example como .env y agregá tu clave."
    )


# Modelo local de embeddings.
#
# Elegimos uno multilingüe porque funciona bien para un ejemplo
# donde tanto los documentos como las preguntas pueden estar en español.
#
# Este modelo genera vectores de 384 dimensiones.
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Cliente del LLM que se utilizará en la etapa de generación.
groq_client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# 2. CONEXIÓN A POSTGRESQL
# ============================================================

def get_connection():
    """
    Abre una conexión nueva a PostgreSQL.

    register_vector() registra en Psycopg el tipo VECTOR de pgvector.
    Esto permite enviar arrays NumPy directamente como parámetros SQL.
    """

    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

    register_vector(conn)

    return conn


# ============================================================
# 3. LECTURA DE DOCUMENTOS
# ============================================================

def extract_text(filepath: str) -> str:
    """
    Extrae texto de archivos TXT, Markdown o PDF.

    Importante:
    pypdf extrae texto de PDFs que contienen texto real.
    Un PDF escaneado como imagen requeriría OCR.
    """

    path = Path(filepath)
    extension = path.suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(filepath)

        pages = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)

        return "\n".join(pages)

    if extension in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError(
        "Formato no soportado. Usá archivos .txt, .md o .pdf"
    )


# ============================================================
# 4. CHUNKING
# ============================================================

def split_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> list[str]:
    """
    Divide el documento en fragmentos superpuestos.

    chunk_size:
        Cantidad máxima aproximada de caracteres por fragmento.

    overlap:
        Cantidad de caracteres que se repiten entre un fragmento
        y el siguiente.

    ¿Por qué usamos overlap?
    Porque una idea puede comenzar al final de un chunk y terminar
    al principio del siguiente. El solapamiento reduce la posibilidad
    de perder ese contexto.
    """

    text = " ".join(text.split())

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap debe ser menor que chunk_size")

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size].strip()

        if chunk:
            chunks.append(chunk)

        if start + chunk_size >= len(text):
            break

    return chunks


# ============================================================
# 5. EMBEDDINGS
# ============================================================

def create_embeddings(texts: list[str]) -> np.ndarray:
    """
    Convierte una lista de textos a vectores numéricos.

    normalize_embeddings=True normaliza los embeddings para que
    sean adecuados para comparaciones basadas en similitud coseno.
    """

    vectors = embedding_model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return np.asarray(vectors, dtype=np.float32)


# ============================================================
# 6. INDEXACIÓN DEL DOCUMENTO
# ============================================================

def ingest_document(filepath: str) -> str:
    """
    Pipeline de ingesta del RAG:

        documento
          ↓
        extracción de texto
          ↓
        chunking
          ↓
        embeddings
          ↓
        PostgreSQL + pgvector
    """

    if not filepath:
        return "⚠️ Seleccioná primero un archivo."

    filename = Path(filepath).name

    try:
        text = extract_text(filepath)

        if not text.strip():
            return (
                f"⚠️ No se pudo extraer texto de {filename}. "
                "Si es un PDF escaneado necesitarías OCR."
            )

        chunks = split_text(text)

        embeddings = create_embeddings(chunks)

        with get_connection() as conn:

            # Para mantener simple el ejemplo, si volvemos a cargar
            # el mismo archivo eliminamos sus chunks anteriores.
            conn.execute(
                "DELETE FROM documents WHERE filename = %s",
                (filename,),
            )

            rows = []

            for index, (chunk, embedding) in enumerate(
                zip(chunks, embeddings)
            ):
                rows.append(
                    (
                        filename,
                        index,
                        chunk,
                        embedding,
                    )
                )

            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO documents
                        (filename, chunk_index, content, embedding)
                    VALUES
                        (%s, %s, %s, %s)
                    """,
                    rows,
                )

            conn.commit()

        return (
            f"✅ Documento indexado correctamente.\n\n"
            f"**Archivo:** {filename}\n\n"
            f"**Chunks almacenados:** {len(chunks)}"
        )

    except Exception as exc:
        return f"❌ Error al indexar el documento:\n\n`{exc}`"


# ============================================================
# 7. RETRIEVAL: BÚSQUEDA SEMÁNTICA
# ============================================================

def search_similar_chunks(
    question: str,
    top_k: int = 4
) -> list[tuple]:
    """
    Busca en PostgreSQL los chunks semánticamente más parecidos
    a la pregunta.

    El operador <=> de pgvector calcula distancia coseno.

    Como queremos mostrar una similitud intuitiva:
        similitud = 1 - distancia_coseno
    """

    question_vector = create_embeddings([question])[0]

    with get_connection() as conn:
        rows = conn.execute(
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
                question_vector,
                question_vector,
                top_k,
            ),
        ).fetchall()

    return rows


# ============================================================
# 8. GENERACIÓN: ARMADO DEL PROMPT RAG
# ============================================================

def generate_answer(
    question: str,
    top_k: int = 4
):
    """
    Pipeline de consulta:

        pregunta
          ↓
        embedding de la pregunta
          ↓
        búsqueda vectorial en PostgreSQL
          ↓
        chunks relevantes
          ↓
        prompt con contexto
          ↓
        LLM
          ↓
        respuesta
    """

    if not question or not question.strip():
        return "Escribí una pregunta.", ""

    try:
        rows = search_similar_chunks(
            question,
            int(top_k),
        )

        if not rows:
            return (
                "No existen documentos cargados todavía.",
                ""
            )

        context_parts = []
        sources_parts = []

        for number, row in enumerate(rows, start=1):

            filename, chunk_index, content, similarity = row

            context_parts.append(
                f"""
FUENTE {number}
Archivo: {filename}
Chunk: {chunk_index}

{content}
""".strip()
            )

            sources_parts.append(
                f"""
### Fuente {number}
- **Archivo:** {filename}
- **Chunk:** {chunk_index}
- **Similitud:** {float(similarity):.3f}

> {content[:500]}...
""".strip()
            )

        context = "\n\n---\n\n".join(context_parts)

        system_prompt = """
Sos un asistente que trabaja con una arquitectura RAG.

REGLAS:
1. Respondé únicamente usando la información incluida en CONTEXTO.
2. No inventes información.
3. Si el contexto no contiene la respuesta, indicá claramente:
   "No encuentro esa información en los documentos cargados".
4. Respondé en español.
5. Mantené la respuesta clara y concreta.
""".strip()

        user_prompt = f"""
CONTEXTO
========
{context}

PREGUNTA
========
{question}
""".strip()

        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.2,
        )

        answer = completion.choices[0].message.content

        sources_markdown = "\n\n".join(sources_parts)

        return answer, sources_markdown

    except Exception as exc:
        return (
            f"❌ Error durante la consulta:\n\n`{exc}`",
            "",
        )


# ============================================================
# 9. INTERFAZ GRADIO
# ============================================================

with gr.Blocks(title="RAG con PostgreSQL + pgvector") as demo:

    gr.Markdown(
        """
# RAG con Python, Gradio y PostgreSQL

Este ejemplo implementa un RAG desde cero sin LangChain.

### Flujo

**Documento → chunks → embeddings → PostgreSQL/pgvector**

Luego:

**Pregunta → embedding → búsqueda vectorial → contexto → Groq → respuesta**
"""
    )

    # --------------------------------------------------------
    # PESTAÑA 1: carga e indexación
    # --------------------------------------------------------

    with gr.Tab("1. Cargar documentos"):

        document_file = gr.File(
            label="Documento",
            file_types=[".txt", ".md", ".pdf"],
            type="filepath",
        )

        ingest_button = gr.Button(
            "Indexar documento",
            variant="primary",
        )

        ingest_status = gr.Markdown()

        ingest_button.click(
            fn=ingest_document,
            inputs=document_file,
            outputs=ingest_status,
        )

    # --------------------------------------------------------
    # PESTAÑA 2: consultas al RAG
    # --------------------------------------------------------

    with gr.Tab("2. Preguntar"):

        question = gr.Textbox(
            label="Pregunta",
            placeholder=(
                "Ejemplo: ¿Qué política de vacaciones "
                "menciona el documento?"
            ),
            lines=3,
        )

        top_k = gr.Slider(
            minimum=1,
            maximum=10,
            value=4,
            step=1,
            label="Cantidad de chunks recuperados",
        )

        ask_button = gr.Button(
            "Consultar RAG",
            variant="primary",
        )

        gr.Markdown("## Respuesta")

        answer_output = gr.Markdown()

        gr.Markdown("## Contexto recuperado")

        sources_output = gr.Markdown()

        ask_button.click(
            fn=generate_answer,
            inputs=[
                question,
                top_k,
            ],
            outputs=[
                answer_output,
                sources_output,
            ],
        )

        # Permite ejecutar la consulta presionando ENTER.
        question.submit(
            fn=generate_answer,
            inputs=[
                question,
                top_k,
            ],
            outputs=[
                answer_output,
                sources_output,
            ],
        )


# ============================================================
# 10. EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
    )
    