import gradio as gr


def calcular(numero_1: float, numero_2: float):
    suma = numero_1 + numero_2
    producto = numero_1 * numero_2
    promedio = suma / 2

    return suma, producto, promedio


app = gr.Interface(
    fn=calcular,
    inputs=[
        gr.Number(label="Primer número", value=0),
        gr.Number(label="Segundo número", value=0),
    ],
    outputs=[
        gr.Number(label="Suma"),
        gr.Number(label="Producto"),
        gr.Number(label="Promedio"),
    ],
    title="Calculadora",
)

app.launch()