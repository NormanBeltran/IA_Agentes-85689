# try / except es la estructura para capturar errores que exceden el alcance del algoritmo

try:
    a = 100 / 10
    lista = [1,2,3]
    print(lista[10])
except Exception as e:
    print(f"Ocurrio una excepcion {e}")

print("Fin de programa")    