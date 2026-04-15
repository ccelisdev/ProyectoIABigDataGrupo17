from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Qdrant
from src.database import GestorVectorial
from src.embeddings import MotorEmbeddings

# --- CONFIGURACIÓN DE FASTAPI ---
app = FastAPI(
    title="API - Asistente Empresarial RAG",
    description="Backend con persistencia en MongoDB para chats independientes",
    version="0.2.0"
)

# Permitir CORS para que React pueda comunicarse con FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONEXIÓN A MONGODB ---
load_dotenv() # Carga las variables del archivo .env

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client.rag_database
conversations_collection = db.get_collection("conversations")

# --- INICIALIZACIÓN DEL MOTOR RAG ---
print("⏳ Cargando sistema RAG...")
gestor = GestorVectorial()
embeddings = MotorEmbeddings().obtener_modelo()
llm = OllamaLLM(model="llama3:8b")

vectorstore = Qdrant(
    client=gestor.obtener_cliente(),
    collection_name=gestor.nombre_coleccion,
    embeddings=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

template = """Eres un asistente experto. Usa este contexto para responder.
Si no lo sabes, di que no está en el documento, no inventes.

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA:"""

prompt = ChatPromptTemplate.from_template(template)
cadena = prompt | llm
print("✅ ¡Sistema RAG listo!")

# --- MODELOS DE DATOS (PYDANTIC) ---
class MessageSchema(BaseModel):
    role: str
    text: str
    timestamp: datetime = datetime.utcnow()

class ChatResponse(BaseModel):
    respuesta: str
    conversation_id: str
    fuentes: List[str] = []

# --- ENDPOINTS ---

@app.get("/")
def health_check():
    return {"estado": "ok", "mensaje": "Servidor funcionando y conectado a DB"}

# 1. Obtener la lista de conversaciones de un usuario
@app.get("/conversations/{user_name}")
async def get_user_conversations(user_name: str):
    cursor = conversations_collection.find({"user_name": user_name}).sort("last_updated", -1)
    chats = await cursor.to_list(length=50)

    return [
        {
            "id": str(chat["_id"]),
            "title": chat.get("title", "Nueva conversación")
        } for chat in chats
    ]

# 2. Obtener los mensajes de una conversación específica
@app.get("/chat/{conversation_id}")
async def get_chat_messages(conversation_id: str):
    try:
        chat = await conversations_collection.find_one({"_id": ObjectId(conversation_id)})
        if not chat:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        messages = chat.get("messages", [])
        for msg in messages:
            if "timestamp" in msg:
                msg["timestamp"] = msg["timestamp"].isoformat()

        return messages
    except Exception:
        raise HTTPException(status_code=400, detail="ID de conversación inválido")

# 3. Endpoint principal de Chat (Crea o actualiza "fichas")
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_name: str = Body(...),
    pregunta: str = Body(...),
    conversation_id: Optional[str] = Body(None)
):
    user_msg = {"role": "user", "text": pregunta, "timestamp": datetime.utcnow()}

    if conversation_id:
        # CASO A: El usuario está en una conversación activa (Actualizar ficha)
        oid = ObjectId(conversation_id)
        await conversations_collection.update_one(
            {"_id": oid},
            {
                "$push": {"messages": user_msg},
                "$set": {"last_updated": datetime.utcnow()}
            }
        )
        current_id = conversation_id
    else:
        # CASO B: Es un nuevo chat (Crear nueva ficha)
        new_chat = {
            "user_name": user_name,
            "title": pregunta[:40] + ("..." if len(pregunta) > 40 else ""),
            "messages": [user_msg],
            "last_updated": datetime.utcnow()
        }
        result = await conversations_collection.insert_one(new_chat)
        current_id = str(result.inserted_id)

    # --- MOTOR RAG REAL ---
    docs = retriever.invoke(pregunta)
    contexto = "\n\n".join([doc.page_content for doc in docs])
    respuesta_rag = cadena.invoke({"context": contexto, "question": pregunta})
    fuentes = [doc.page_content[:200] for doc in docs]
    # ----------------------

    bot_msg = {"role": "bot", "text": respuesta_rag, "timestamp": datetime.utcnow()}

    await conversations_collection.update_one(
        {"_id": ObjectId(current_id)},
        {"$push": {"messages": bot_msg}}
    )

    return {
        "respuesta": respuesta_rag,
        "conversation_id": current_id,
        "fuentes": fuentes
    }

# --- EJECUCIÓN ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
