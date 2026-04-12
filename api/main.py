from fastapi import FastAPI

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="API - Asistente Empresarial RAG",
    description="Backend para el asistente inteligente corporativo del Grupo 17",
    version="0.1.0"
)

# Endpoint de prueba para saber si el servidor está vivo (Health Check)
@app.get("/")
def read_root():
    return {"estado": "ok", "mensaje": "¡Servidor FastAPI funcionando correctamente!"}

# Aquí es donde conectaremos el Frontend y el motor RAG más adelante
@app.post("/chat")
def chat_endpoint(pregunta: str):
    # TODO: Conectar con src.rag_chain para obtener la respuesta real del LLM
    return {
        "pregunta": pregunta,
        "respuesta": "Esta es una respuesta simulada. Pronto conectaremos el LLM local.",
        "fuentes": []
    }