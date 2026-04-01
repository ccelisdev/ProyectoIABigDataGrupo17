from src.embeddings import MotorEmbeddings
from src.database import GestorVectorial

def test_recuperacion_real():
    print("🧠 Cargando motor de inteligencia...")
    motor = MotorEmbeddings()
    modelo = motor.obtener_modelo()
    
    # 1. Usamos nuestro Gestor para obtener el cliente que YA ESTÁ ABIERTO
    gestor = GestorVectorial()
    client = gestor.obtener_cliente()
    
    # LA PREGUNTA
    pregunta = "Conceptos fundamentales del tema" 
    print(f"🔍 Preguntando a la base de datos: '{pregunta}'")
    
    # 2. Convertimos pregunta a vector
    vector_pregunta = modelo.embed_query(pregunta)
    
    # 3. BUSCAMOS directamente con el cliente del gestor
    resultados = client.search(
        collection_name=gestor.nombre_coleccion,
        query_vector=vector_pregunta,
        limit=3
    )
    
    if not resultados:
        print("⚠️ No se han encontrado resultados. Asegúrate de haber ejecutado src/ingestion.py antes.")
        return

    print(f"\n✨ ¡HE ENCONTRADO DATOS! ({len(resultados)} fragmentos):")
    for i, res in enumerate(resultados):
        texto = res.payload.get("page_content", "Sin texto")
        print(f"\n--- Fragmento {i+1} (Puntuación: {res.score:.4f}) ---")
        print(texto[:300] + "...")

if __name__ == "__main__":
    test_recuperacion_real()