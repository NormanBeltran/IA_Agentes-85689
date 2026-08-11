import gradio as gr


def generar_perfil(
    nombre: str,
    edad: int,
    lenguaje: str,
    trabaja_con_ia: bool,
):
    return {
        "nombre": nombre,
        "edad": edad,
        "lenguaje_preferido": lenguaje,
        "trabaja_con_ia": trabaja_con_ia,
    }


app = gr.Interface(
    fn=generar_perfil,
    inputs=[
        gr.Textbox(label="Nombre"),
        gr.Slider(
            minimum=18,
            maximum=80,
            value=30,
            step=1,
            label="Edad",
        ),
        gr.Dropdown(
            choices=["Python", "Java", "JavaScript", "C#"],
            value="Python",
            label="Lenguaje",
        ),
        gr.Checkbox(label="¿Trabaja con inteligencia artificial?"),
    ],
    outputs=gr.JSON(label="Perfil generado"),
)

app.launch()