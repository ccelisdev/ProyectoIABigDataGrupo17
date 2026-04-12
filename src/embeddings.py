from langchain_community.embeddings import HuggingFaceEmbeddings

class MotorEmbeddings:
    def __init__(self):
        # Elegimos un modelo ligero y de código abierto (ideal para local)
        self.nombre_modelo = "sentence-transformers/all-MiniLM-L6-v2"
        # Inicializamos el modelo de LangChain
        self.embeddings = HuggingFaceEmbeddings(model_name=self.nombre_modelo)

    def obtener_modelo(self):
        return self.embeddings

# Bloque de prueba: esto solo se ejecuta si lanzas este script directamente
if __name__ == "__main__":
    print("⏳ Descargando/Cargando modelo de embeddings local...")
    motor = MotorEmbeddings().obtener_modelo()
    
    texto_prueba = "El asistente corporativo debe mantener la privacidad de los datos."
    vector = motor.embed_query(texto_prueba)
    
    print(f"✅ ¡Éxito! El texto se ha convertido en un vector de {len(vector)} dimensiones.")
    print(f"🔢 Primeros 5 valores del vector: {vector[:5]}")