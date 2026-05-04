"""
Script: reset_qdrant.py
Pasos: 1) Borra la coleccion de Qdrant, 2) Re-ingesta los PDFs, 3) Verifica el contenido
"""
import os
import shutil
from qdrant_client import QdrantClient
from src.ingestion import IngestorDocumentos

QDRANT_PATH = "qdrant_db"
NOMBRE_COLECCION = "documentos_empresa"

# ---- PASO 1: Limpiar ----
print("=" * 50)
print("PASO 1: Borrando carpeta qdrant_db completa...")
if os.path.exists(QDRANT_PATH):
    shutil.rmtree(QDRANT_PATH)
    print(f"Carpeta '{QDRANT_PATH}' eliminada por completo.")
else:
    print("La carpeta no existia, nada que borrar.")

# ---- PASO 2: Re-ingestar ----
print("\nPASO 2: Re-ingesta de documentos...")
ingestor = IngestorDocumentos()
ingestor.procesar_archivo("acme_general.pdf",   nivel_acceso="publico")
ingestor.procesar_archivo("acme_finanzas.pdf",  nivel_acceso="finanzas")
ingestor.procesar_archivo("acme_direccion.pdf", nivel_acceso="admin")
ingestor.cliente_qdrant.close()

# ---- PASO 3: Verificar ----
print("\nPASO 3: Verificando contenido en Qdrant...")
client2 = QdrantClient(path=QDRANT_PATH)
total = client2.count(collection_name=NOMBRE_COLECCION).count
print(f"Total de fragmentos indexados: {total}")

resultados = client2.scroll(collection_name=NOMBRE_COLECCION, limit=3, with_payload=True, with_vectors=False)
print("\nMuestra de 3 fragmentos:")
for punto in resultados[0]:
    payload = punto.payload or {}
    metadata = payload.get("metadata", {})
    print(f"  nivel_acceso: {metadata.get('nivel_acceso', 'NO TIENE')} | source: {metadata.get('source', '?')}")

client2.close()
print("=" * 50)
print("Listo.")
