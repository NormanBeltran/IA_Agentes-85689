# RAG + GRADIO + POSTGRES + PGVECTOR + GROQ

## Definiciones 

- Usuario ingrese a la aplicación, cargue un documento
- El agente va a trnsformar ese documento en chuncks 
- Guardar esos chuncks en la BD Vectorial
- Usuario hace consultas sobre el documento privado (prompt)
- El agente busca por cercania que chunks podrian tener la respuesta de esa pregunta
- Con el prompt + chucks que devolvió la consulta a la BD vectorial, el agente llama a 
  un modelo de IA para que genere una respuesta en base a la consulta y los pedazos de documentos
  