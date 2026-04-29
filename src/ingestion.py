import os
import re
import logging
import pandas as pd
from docx import Document as DocxDocument
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
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
        if not text: return ""
        text = text.replace("\n", " ").strip()
        return re.sub(r"\s+", " ", text)

    def apply_data_masking(self, text: str) -> str:
        # Anonimización de emails y teléfonos
        text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", "[EMAIL_MASKED]", text)
        text = re.sub(r"\b\d{9}\b", "[PHONE_MASKED]", text)
        return text

    def procesar_archivo(self, ruta_archivo):
        if not os.path.exists(ruta_archivo):
            logger.error(f"❌ El archivo no existe: {ruta_archivo}")
            return

        logger.info(f"📄 Procesando formato: {os.path.splitext(ruta_archivo)[1]} -> {ruta_archivo}")
        documentos_langchain = []

        # --- LÓGICA DE DETECCIÓN DE FORMATO ---
        ext = ruta_archivo.lower()

        if ext.endswith(".pdf"):
            loader = PyPDFLoader(ruta_archivo)
            documentos_langchain = loader.load()

        elif ext.endswith(".docx"):
            doc_word = DocxDocument(ruta_archivo)
            texto_completo = "\n".join([para.text for para in doc_word.paragraphs])
            documentos_langchain = [Document(page_content=texto_completo, metadata={"source": ruta_archivo})]

        elif ext.endswith((".xlsx", ".xls")):
            df = pd.read_excel(ruta_archivo)
            # Convertimos el Excel a un formato de texto que la IA entienda (tipo tabla)
            texto_excel = df.to_string(index=False)
            documentos_langchain = [Document(page_content=texto_excel, metadata={"source": ruta_archivo})]

        elif ext.endswith(".txt"):
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                texto_txt = f.read()
            documentos_langchain = [Document(page_content=texto_txt, metadata={"source": ruta_archivo})]

        else:
            logger.warning(f"⚠️ Formato {ext} no soportado todavía.")
            return

        # --- PROCESAMIENTO COMÚN (Limpieza, Masking y Chunking) ---
        for doc in documentos_langchain:
            doc.page_content = self.apply_data_masking(self.clean_text(doc.page_content))

        # Aumentamos un poco el chunk_size para que el Excel no se corte a mitad de fila
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        trozos = text_splitter.split_documents(documentos_langchain)
        
        vectorstore = Qdrant(
            client=self.cliente_qdrant,
            collection_name=self.nombre_coleccion,
            embeddings=self.embeddings
        )
        vectorstore.add_documents(trozos)
        logger.info(f"✅ ¡{len(trozos)} fragmentos indexados con éxito desde {os.path.basename(ruta_archivo)}!")

if __name__ == "__main__":
    ingestor = IngestorDocumentos()
    
    # Aquí puedes añadir los archivos que quieras probar
    archivos_prueba = ["prueba.xlsx", "empresa_prueba.pdf"] 
    
    for arc in archivos_prueba:
        if os.path.exists(arc):
            ingestor.procesar_archivo(arc)