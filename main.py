from fastapi import FastAPI
from src.embeddings import MotorEmbeddings
from src.database import GestorVectorial

app = FastAPI(
    title="API - Asistente Empresarial RAG",
    description="Backend para el asistente inteligente corporativo del Grupo 17",
    version="0.1.0"
)

# Cargamos las piezas de Mario
motor   = MotorEmbeddings().obtener_modelo()
cliente = GestorVectorial().obtener_cliente()
COLECCION = "documentos_empresa"

@app.get("/")
def read_root():
    return {"estado": "ok", "mensaje": "¡Servidor FastAPI funcionando correctamente!"}

@app.post("/chat")
def chat_endpoint(pregunta: str):

    # Paso 1: convertir pregunta a números
    pregunta_en_numeros = motor.embed_query(pregunta)

    # Paso 2: buscar en Qdrant los fragmentos más relevantes
    resultados = cliente.search(
        collection_name=COLECCION,
        query_vector=pregunta_en_numeros,
        limit=3
    )

    # Paso 3: extraer el texto
    fuentes = []
    for r in resultados:
        fuentes.append({
            "texto":      r.payload["page_content"],
            "fuente":     r.payload.get("source", "desconocida"),
            "relevancia": round(r.score, 2)
        })

    # Paso 4: devolver respuesta real
    return {
        "pregunta": pregunta,
        "respuesta": fuentes[0]["texto"] if fuentes else "No encontré información relevante.",
        "fuentes":   fuentes
    }