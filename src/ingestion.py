import os
import re
import logging
import pdfplumber
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.embeddings import MotorEmbeddings
from src.database import GestorVectorial
from langchain_community.vectorstores import Qdrant

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class IngestorDocumentos:
    def __init__(self):
        self.embeddings = MotorEmbeddings().obtener_modelo()
        self.gestor_db = GestorVectorial()
        self.cliente_qdrant = self.gestor_db.obtener_cliente()
        self.nombre_coleccion = self.gestor_db.nombre_coleccion

    def clean_text(self, text: str) -> str:
        text = text.replace("\n", " ").strip()
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def apply_data_masking(self, text: str) -> str:
        # Anonimización básica
        text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", "[EMAIL_MASKED]", text)
        text = re.sub(r"\b\d{9}\b", "[PHONE_MASKED]", text)
        return text

    def procesar_archivo(self, ruta_archivo):
        logger.info(f"📄 Procesando: {ruta_archivo}...")
        if ruta_archivo.endswith(".pdf"):
            loader = PyPDFLoader(ruta_archivo)
            documentos = loader.load()
        else:
            logger.warning("Formato no soportado en este ejemplo rápido")
            return

        for doc in documentos:
            doc.page_content = self.clean_text(doc.page_content)
            doc.page_content = self.apply_data_masking(doc.page_content)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        trozos = text_splitter.split_documents(documentos)
        
        vectorstore = Qdrant(
            client=self.cliente_qdrant,
            collection_name=self.nombre_coleccion,
            embeddings=self.embeddings
        )
        vectorstore.add_documents(trozos)
        logger.info("✅ ¡Documento indexado con éxito!")

if __name__ == "__main__":
    ingestor = IngestorDocumentos()
    if os.path.exists("Tema2.pdf"):
        ingestor.procesar_archivo("Tema2.pdf")