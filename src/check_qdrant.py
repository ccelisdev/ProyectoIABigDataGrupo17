#file to check qdrant connection and data

from qdrant_client import QdrantClient

COLLECTION_NAME = "document_chunks"

client = QdrantClient(path="qdrant_local")

try:
    print("¿Existe la colección?:", client.collection_exists(COLLECTION_NAME))

    info = client.get_collection(COLLECTION_NAME)
    print("Número de embeddings detectados:", info.points_count)

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=3
    )

    for p in points:
        print("-" * 40)
        print("ID:", p.id)
        print("Archivo:", p.payload["file_name"])
        print("Chunk ID:", p.payload["chunk_id"])
        print("Texto:", p.payload["text"][:200], "...")

finally:
    client.close()

