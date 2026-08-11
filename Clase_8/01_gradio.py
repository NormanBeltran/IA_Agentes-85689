import gradio as gr


def saludar(nombre: str) -> str:
    if not nombre.strip():
        return "Por favor, ingresá un nombre."

    return f"¡Hola, {nombre}! Bienvenido a Gradio."


app = gr.Interface(
    fn=saludar,
    inputs=gr.Textbox(
        label="Nombre",
        placeholder="Ingresá tu nombre",
    ),
    outputs=gr.Textbox(label="Resultado"),
    title="Mi primera aplicación con Gradio",
    description="Una interfaz web conectada con una función Python.",
    examples=[
        ["Norman"],
        ["Sofía"],
        ["Juan"],
    ],
)

if __name__ == "__main__":
    app.launch()