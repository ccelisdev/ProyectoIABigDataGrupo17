class HolaMundo:
    def __init__(self, nombre):
        self.nombre = nombre

    def saludar(self):
        print(f"¡Hola Mundo! Soy {self.nombre} y mi conexión a GitHub funciona perfectamente.")

# Este bloque ejecuta el código si lanzas el archivo directamente
if __name__ == "__main__":
    prueba = HolaMundo("Mario")
    prueba.saludar()