from sentence_transformers import SentenceTransformer, util
import torch

documentos = [
    "Python es un lenguaje de programación de alto nivel",
    "Python se utiliza en una amplia variedad de aplicaciones",
    "Donald Trump ataca a Uruguay y se hace con el control de Sudamerica",
    "Confirman luego de haber encontrado el arca de Noe que la Biblia es historica",
    "Descubren en una planta la solucion de una enfermedad milenaria",
    "Los animales son buenos"
]

modelo_embeddings = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embeddings = modelo_embeddings.encode(documentos)

pregunta = input("Ingrese su pregunta:")
embedding_pregunta = modelo_embeddings.encode(pregunta)

print("_"*80)
print(embeddings)
print("_"*80)

similitudes = util.cos_sim(embedding_pregunta, embeddings)[0]
top_resultados = torch.topk(similitudes, 2)
contexto = "\n".join([documentos[i] for i in top_resultados.indices])

print(contexto)