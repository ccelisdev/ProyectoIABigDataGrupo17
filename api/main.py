import os
from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from dotenv import load_dotenv
import certifi 

# FastAPI y Servidor
from fastapi import FastAPI, Body, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import uvicorn

# Seguridad
from passlib.context import CryptContext
from jose import JWTError, jwt

# Motor RAG
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Qdrant
from src.database import GestorVectorial
from src.embeddings import MotorEmbeddings

# --- CONFIGURACIÓN ---
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 # 8 horas de jornada laboral

app = FastAPI(title="API RAG Empresarial - Grupo 17", version="1.2.0")

# OAuth2 esquema para extraer el token del header Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
user_collection = db.get_collection("users")

# --- SEGURIDAD Y TOKENS ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_token_acceso(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    if token == "invitado": # Bypass para invitados
        return {"sub": "invitado@empresa.com", "role": "empleado", "name": "invitado"}
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión expirada o inválida",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return payload # Retorna los datos del usuario contenidos en el token
    except JWTError:
        raise credentials_exception

# --- MOTOR IA (IGUAL) ---
gestor = GestorVectorial()
embeddings = MotorEmbeddings().obtener_modelo()
llm = OllamaLLM(model="llama3:8b")
vectorstore = Qdrant(client=gestor.obtener_cliente(), collection_name=gestor.nombre_coleccion, embeddings=embeddings)
template = """Eres un asistente experto. CONTEXTO:\n{context}\n\nPREGUNTA: {question}\nRESPUESTA:"""
prompt = ChatPromptTemplate.from_template(template)
cadena = prompt | llm

# --- SCHEMAS ---
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    user_name: str
    role: str
    token: str # El frontend necesita esto

class ChatResponse(BaseModel):
    respuesta: str
    conversation_id: str
    fuentes: List[dict] = []

class FeedbackSchema(BaseModel):
    conversation_id: str
    message_index: int
    valor: str

# ------------------- ENDPOINTS PROTEGIDOS -------------------

@app.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    user = await user_collection.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Creamos el token con el email y el rol
    access_token = crear_token_acceso(data={"sub": user["email"], "role": user["role"], "name": user.get("user_name", "Usuario")})
    
    return {
        "user_name": user.get("user_name", user["email"]),
        "role": user["role"],
        "token": access_token
    }

@app.get("/chat/{conversation_id}")
async def obtener_historial(
    conversation_id: str, 
    current_user: dict = Depends(obtener_usuario_actual) # SEGURIDAD AÑADIDA
):
    try:
        # Buscamos la conversación por ID en MongoDB
        chat = await conversations_collection.find_one({"_id": ObjectId(conversation_id)})
        
        if not chat:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        # Verificación de propiedad: Un usuario no puede leer chats de otro
        # A menos que sea admin
        if chat["user_name"] != current_user["name"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="No tienes permiso para ver este historial")

        msgs = chat.get("messages", [])
        
        # Formateamos los timestamps para que JSON los entienda
        for m in msgs:
            if "timestamp" in m and isinstance(m["timestamp"], datetime):
                m["timestamp"] = m["timestamp"].isoformat()
                
        return msgs
    except Exception as e:
        print(f"Error al cargar historial: {e}")
        raise HTTPException(status_code=400, detail="ID de conversación no válido o error interno")

@app.get("/conversations/{user_name}")
async def listar_chats(user_name: str, current_user: dict = Depends(obtener_usuario_actual)):
    # Verificación de integridad: un usuario no debería ver chats de otro
    if current_user["name"] != user_name and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para ver estos chats")
    
    cursor = conversations_collection.find({"user_name": user_name}).sort("last_updated", -1)
    chats = await cursor.to_list(length=50)
    return [{"id": str(chat["_id"]), "title": chat.get("title", "Chat")} for chat in chats]

@app.post("/chat", response_model=ChatResponse)
async def chat_principal(
    current_user: dict = Depends(obtener_usuario_actual), # Obliga a estar logueado
    pregunta: str = Body(...),
    conversation_id: Optional[str] = Body(None)
):
    user_name = current_user["name"]
    role = current_user["role"].lower()

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

    # --- FILTRO RAG POR ROL ---
    filtro = {"nivel_acceso": "publico"}
    if role == "compliance":
        filtro = {"nivel_acceso": {"$in": ["publico", "compliance"]}}
    elif role == "admin":
        filtro = None 

    docs = vectorstore.similarity_search(pregunta, k=3, filter=filtro)
    contexto_str = "\n\n".join([d.page_content for d in docs])
    ai_answer = cadena.invoke({"context": contexto_str, "question": pregunta})
    
    citas = [{"archivo": os.path.basename(d.metadata.get("source", "Doc")), "texto": d.page_content} for d in docs]

    bot_msg = {"role": "bot", "text": ai_answer, "fuentes": citas, "timestamp": datetime.utcnow()}
    await conversations_collection.update_one({"_id": ObjectId(current_id)}, {"$push": {"messages": bot_msg}})

    return {"respuesta": ai_answer, "conversation_id": current_id, "fuentes": citas}

@app.post("/chat/feedback")
async def save_feedback(data: FeedbackSchema, current_user: dict = Depends(obtener_usuario_actual)):
    field_path = f"messages.{data.message_index}.feedback"
    await conversations_collection.update_one(
        {"_id": ObjectId(data.conversation_id)},
        {"$set": {field_path: data.valor}} 
    )
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)