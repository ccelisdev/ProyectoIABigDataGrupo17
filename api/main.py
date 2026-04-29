import os
import re
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from dotenv import load_dotenv
import certifi 

# FastAPI y Servidor
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import uvicorn

# Motor RAG (LangChain + Ollama + Qdrant)
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Qdrant
from src.database import GestorVectorial
from src.embeddings import MotorEmbeddings

# --- CONFIGURACIÓN ---
load_dotenv()
app = FastAPI(
    title="API - Asistente Empresarial RAG",
    description="Punto de entrada principal del TFG - Sistema RAG con historial en MongoDB",
    version="1.0.0"
)

# CORS: Permite que React (puerto 5173) hable con esta API (puerto 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BASES DE DATOS ---
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.rag_database
conversations_collection = db.get_collection("conversations")

# --- MOTOR IA (Configuración de Mario) ---
print("⏳ Inicializando el cerebro del sistema (Llama 3 + Qdrant)...")
gestor = GestorVectorial()
embeddings = MotorEmbeddings().obtener_modelo()
llm = OllamaLLM(model="llama3:8b")

vectorstore = Qdrant(
    client=gestor.obtener_cliente(),
    collection_name=gestor.nombre_coleccion,
    embeddings=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Prompt técnico para evitar alucinaciones
template = """Eres un asistente experto de la empresa. Tu objetivo es ayudar a los empleados basándote exclusivamente en el contexto proporcionado.
Si la información no está en el contexto, indica amablemente que no dispones de esos datos en los documentos oficiales.

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA:"""

prompt = ChatPromptTemplate.from_template(template)
cadena = prompt | llm
print("✅ Sistema listo para procesar consultas.")

# --- MODELOS DE DATOS ---
class ChatResponse(BaseModel):
    respuesta: str
    conversation_id: str
    fuentes: List[dict] = [] # Estructura: {"archivo": "nombre.pdf", "texto": "contenido"}

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "online", "message": "API RAG Mario & Team funcionando"}

@app.get("/conversations/{user_name}")
async def listar_chats(user_name: str):
    cursor = conversations_collection.find({"user_name": user_name}).sort("last_updated", -1)
    chats = await cursor.to_list(length=50)
    return [{"id": str(chat["_id"]), "title": chat.get("title", "Chat")} for chat in chats]

@app.get("/chat/{conversation_id}")
async def obtener_historial(conversation_id: str):
    try:
        chat = await conversations_collection.find_one({"_id": ObjectId(conversation_id)})
        if not chat:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        msgs = chat.get("messages", [])
        for m in msgs:
            if "timestamp" in m: m["timestamp"] = m["timestamp"].isoformat()
        return msgs
    except:
        raise HTTPException(status_code=400, detail="ID inválido")

@app.post("/chat", response_model=ChatResponse)
async def chat_principal(
    user_name: str = Body(...),
    pregunta: str = Body(...),
    conversation_id: Optional[str] = Body(None)
):
    # 1. Registro del mensaje del usuario
    user_msg = {"role": "user", "text": pregunta, "timestamp": datetime.utcnow()}
    
    if conversation_id:
        current_id = conversation_id
        await conversations_collection.update_one(
            {"_id": ObjectId(current_id)},
            {"$push": {"messages": user_msg}, "$set": {"last_updated": datetime.utcnow()}}
        )
    else:
        new_chat = {
            "user_name": user_name,
            "title": pregunta[:40] + "...",
            "messages": [user_msg],
            "last_updated": datetime.utcnow()
        }
        res_db = await conversations_collection.insert_one(new_chat)
        current_id = str(res_db.inserted_id)

    # 2. PROCESO RAG (Mario's Task)
    docs = retriever.invoke(pregunta)
    contexto_str = "\n\n".join([d.page_content for d in docs])
    
    # Llamada a Llama 3
    ai_answer = cadena.invoke({"context": contexto_str, "question": pregunta})
    
    # Construcción de fuentes para el Frontend
    citas = []
    for d in docs:
        citas.append({
            "archivo": os.path.basename(d.metadata.get("source", "Doc")),
            "texto": d.page_content
        })

    # 3. Guardar y Responder
    bot_msg = {"role": "bot", "text": ai_answer, "fuentes": citas, "timestamp": datetime.utcnow()}
    await conversations_collection.update_one(
        {"_id": ObjectId(current_id)},
        {"$push": {"messages": bot_msg}}
    )

    return {
        "respuesta": ai_answer,
        "conversation_id": current_id,
        "fuentes": citas
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)