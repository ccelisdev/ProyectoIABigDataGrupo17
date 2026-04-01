from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.embeddings import MotorEmbeddings
from src.database import GestorVectorial
from langchain_community.vectorstores import Qdrant # Importamos la clase principal

class IngestorDocumentos:
    def __init__(self):
        self.embeddings = MotorEmbeddings().obtener_modelo()
        self.gestor_db = GestorVectorial()
        # Esta es nuestra "llave" ya abierta
        self.cliente_qdrant = self.gestor_db.obtener_cliente()
        self.nombre_coleccion = self.gestor_db.nombre_coleccion

    def procesar_pdf(self, ruta_pdf):
        print(f"📄 Cargando PDF: {ruta_pdf}...")
        loader = PyPDFLoader(ruta_pdf)
        paginas = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        trozos = text_splitter.split_documents(paginas)
        
        print(f"✂️ PDF dividido en {len(trozos)} trozos.")

        print("📥 Guardando vectores en la base de datos...")
        
        # CORRECCIÓN: Usamos el cliente que ya existe en lugar de .from_documents()
        vectorstore = Qdrant(
            client=self.cliente_qdrant,
            collection_name=self.nombre_coleccion,
            embeddings=self.embeddings
        )
        
        vectorstore.add_documents(trozos)
        print("✅ ¡Documento indexado con éxito!")

if __name__ == "__main__":
    ingestor = IngestorDocumentos()
    # Asegúrate de que Tema2.pdf esté en la raíz
    ingestor.procesar_pdf("Tema2.pdf")