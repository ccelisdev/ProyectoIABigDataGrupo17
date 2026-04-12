import sys
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from src.database import GestorVectorial
from src.embeddings import MotorEmbeddings
from langchain_community.vectorstores import Qdrant

def chat_interactivo():
    print("\n" + "="*50)
    print("🤖 BIENVENIDO AL CHAT RAG - GRUPO 17")
    print("      (Escribe 'salir' para terminar)")
    print("="*50)
    
    try:
        # Cargamos el motor una sola vez
        print("🧠 Despertando a Llama 3... (Espera un momento)")
        llm = OllamaLLM(model="llama3:8b")
        
        gestor = GestorVectorial()
        embeddings = MotorEmbeddings().obtener_modelo()
        
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

        print("\n✅ ¡Sistema listo! ¿Qué quieres saber sobre el PDF?")

        while True:
            pregunta = input("\n👤 TÚ: ")
            
            if pregunta.lower() in ["salir", "exit", "quit", "adiós"]:
                print("\n👋 ¡Hasta luego, Mario! Cerrando conexión...")
                break

            print("🔍 Buscando y pensando...")
            
            # Buscamos trozos relevantes
            docs = retriever.invoke(pregunta)
            contexto_texto = "\n\n".join([doc.page_content for doc in docs])
            
            # Generamos la respuesta
            respuesta = cadena.invoke({"context": contexto_texto, "question": pregunta})
            
            print(f"\n🤖 IA: {respuesta}")
            print("-" * 30)

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    chat_interactivo()