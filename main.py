from fastapi import FastAPI
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Qdrant
from src.database import GestorVectorial
from src.embeddings import MotorEmbeddings

app = FastAPI(
    title="API - Asistente Empresarial RAG",
    description="Backend para el asistente inteligente corporativo del Grupo 17",
    version="0.1.0"
)

print("⏳ Cargando sistema RAG...")
gestor     = GestorVectorial()
embeddings = MotorEmbeddings().obtener_modelo()
llm        = OllamaLLM(model="llama3:8b")

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

print("✅ ¡Sistema listo!")

@app.get("/")
def read_root():
    return {"estado": "ok", "mensaje": "¡Servidor FastAPI funcionando correctamente!"}

@app.post("/chat")
def chat_endpoint(pregunta: str):

    docs = retriever.invoke(pregunta)
    contexto = "\n\n".join([doc.page_content for doc in docs])

    respuesta = cadena.invoke({
        "context": contexto,
        "question": pregunta
    })

    return {
        "pregunta": pregunta,
        "respuesta": respuesta,
        "fuentes": [doc.page_content[:200] for doc in docs]
    }