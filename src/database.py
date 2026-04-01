from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os

class GestorVectorial:
    def __init__(self):
        # Guardaremos los datos en una carpeta local llamada 'qdrant_db'
        self.path_db = "qdrant_db"
        self.nombre_coleccion = "documentos_empresa"
        
        # Inicializamos el cliente en modo local
        self.client = QdrantClient(path=self.path_db)
        
        # Creamos la colección si no existe
        self._crear_coleccion_si_no_existe()

    def _crear_coleccion_si_no_existe(self):
        # Comprobamos si la colección ya está creada
        colecciones = self.client.get_collections().collections
        existe = any(c.name == self.nombre_coleccion for c in colecciones)
        
        if not existe:
            print(f"🚀 Creando colección '{self.nombre_coleccion}'...")
            self.client.create_collection(
                collection_name=self.nombre_coleccion,
                vectors_config=VectorParams(
                    size=384, # El tamaño de tus vectores (MiniLM)
                    distance=Distance.COSINE # El método de búsqueda
                ),
            )
            print("✅ Colección creada con éxito.")
        else:
            print(f"📦 La colección '{self.nombre_coleccion}' ya está lista.")

    def obtener_cliente(self):
        return self.client

if __name__ == "__main__":
    # Prueba de conexión
    gestor = GestorVectorial()
    print("🤖 Conexión con Qdrant establecida correctamente.")