"""
ingestion.py

Pipeline de ingesta documental para sistema RAG corporativo - Grupo17.

Funciones que se aplican en el proceso de ingesta:
- Lectura de documentos (TXT, PDF)
- Limpieza de texto
- Data Masking (GDPR)
- Chunking
- Generación de embeddings
- Carga en Qdrant (local)

Autor: Katherin Marin
"""

import os
import re
import logging
from typing import List

import pdfplumber
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct

# ------------------------------
# Configuración y constantes
# ------------------------------

CHUNK_SIZE = 500
COLLECTION_NAME = "document_chunks"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ------------------------------
# Path de almacenamiento local para Qdrant
# ------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
QDRANT_PATH = os.path.join(BASE_DIR, "qdrant_local")

# ------------------------------
# Logging básico
# ------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ------------------------------
# Limpieza de texto básica y data masking
# ------------------------------
def clean_text(text: str) -> str:
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ------------------------------
# Data Masking (anonimización básica)
# ------------------------------
def apply_data_masking(text: str) -> str:
    text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", "[EMAIL_MASKED]", text)
    text = re.sub(r"\b\d{9}\b", "[PHONE_MASKED]", text)
    text = re.sub(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", "[NAME_MASKED]", text)
    return text


# ------------------------------
# 3. Chunking del texto
# ------------------------------
#def chunk_text(text: str, size=CHUNK_SIZE):
#    chunks = []
#    for i in range(0, len(text), size):
#        chunks.append({
#            "chunk_id": i // size,
#            "text": text[i:i+size]
#        })
#   return chunks

def chunk_text(text: str, size: int = CHUNK_SIZE) -> List[str]:
    return [text[i:i + size] for i in range(0, len(text), size)]


# ------------------------------
# Lectura de PDF o TXT
# ------------------------------

def read_document(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return " ".join(page.extract_text() or "" for page in pdf.pages)

    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    logger.warning(f"Formato no soportado: {file_path}")
    return ""


# ------------------------------
# 5. Conexión a Qdrant
# ------------------------------

def init_qdrant(client: QdrantClient):
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance="Cosine"
            )
        )
        logger.info("Colección Qdrant creada.")
    else:
        logger.info("Colección Qdrant ya existe.")


# ------------------------------
# 6. Pipeline completo de ingesta
# ------------------------------

def ingest_documents():
    logger.info("Iniciando pipeline de ingesta...")

    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"No existe la ruta: {RAW_DATA_PATH}")

    files = os.listdir(RAW_DATA_PATH)
    if not files:
        logger.warning("No hay documentos para procesar.")
        return

    logger.info(f"Documentos encontrados: {len(files)}")

    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(path=QDRANT_PATH)
    init_qdrant(client)

    points = []
    point_id = 0

    for filename in files:
        file_path = os.path.join(RAW_DATA_PATH, filename)
        logger.info(f"Procesando archivo: {filename}")

        raw_text = read_document(file_path)
        if not raw_text.strip():
            logger.warning(f"Archivo vacío o no legible: {filename}")
            continue

        cleaned = clean_text(raw_text)
        masked = apply_data_masking(cleaned)
        chunks = chunk_text(masked)

        for idx, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "file_name": filename,
                        "chunk_id": idx,
                        "text": chunk
                    }
                )
            )
            point_id += 1

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        logger.info(f"Cargados {len(points)} embeddings en Qdrant.")
    else:
        logger.warning("No se generaron embeddings.")

# --------------------------------------------------
# MAIN 
# --------------------------------------------------

if __name__ == "__main__":
    ingest_documents()
