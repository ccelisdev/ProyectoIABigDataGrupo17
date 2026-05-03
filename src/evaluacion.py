import requests
import pandas as pd
import unicodedata
from datetime import datetime

API_URL = "http://localhost:8000"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer invitado"
}

ARCHIVO_ENTRADA = "pruebas_entrada.xlsx"
ARCHIVO_SALIDA  = "pruebas_resultados.xlsx"

FRASES_RECHAZO = ["no está", "no tengo", "no encuentro", "no dispongo", "no se menciona", "no puedo", "no está en el documento"]

def normalizar(texto: str) -> str:
    texto = texto.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def evaluar():
    df = pd.read_excel(ARCHIVO_ENTRADA)

    resultados = []

    print(f"\n{'='*60}")
    print(f"  EVALUACIÓN RAG - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}\n")

    for i, fila in df.iterrows():
        pregunta        = str(fila["pregunta"])
        esperado        = str(fila["respuesta_esperada"]) if pd.notna(fila["respuesta_esperada"]) else None
        debe_responder  = str(fila["debe_responder"]).strip().lower() == "si"

        payload  = {"pregunta": pregunta, "conversation_id": None}
        response = requests.post(f"{API_URL}/chat", headers=HEADERS, json=payload)
        data     = response.json()

        respuesta  = data.get("respuesta", "")
        latencia   = data.get("latencia_ms", None)

        if debe_responder:
            acierto    = normalizar(esperado) in normalizar(respuesta)
            resultado  = "CORRECTO" if acierto else "INCORRECTO"
            alucinacion = "NO"
        else:
            no_alucino  = any(normalizar(f) in normalizar(respuesta) for f in FRASES_RECHAZO)
            resultado   = "CORRECTO" if no_alucino else "POSIBLE ALUCINACIÓN"
            alucinacion = "NO" if no_alucino else "SÍ"

        print(f"[{i+1}] {pregunta}")
        print(f"     Respuesta: {respuesta[:100]}...")
        print(f"     Resultado: {resultado} | Latencia: {latencia} ms\n")

        resultados.append({
            "pregunta":           pregunta,
            "respuesta_esperada": esperado,
            "debe_responder":     "Sí" if debe_responder else "No",
            "respuesta_bot":      respuesta,
            "latencia_ms":        latencia,
            "resultado":          resultado,
            "alucinacion":        alucinacion,
        })

    df_out     = pd.DataFrame(resultados)
    correctas  = (df_out["resultado"] == "CORRECTO").sum() + (df_out["resultado"] == "CORRECTO (no inventó)").sum()
    total      = len(df_out)
    precision  = round((correctas / total) * 100, 1)
    latencias  = df_out["latencia_ms"].dropna().tolist()

    print(f"{'='*60}")
    print(f"  RESUMEN")
    print(f"{'='*60}")
    print(f"  Precisión:         {correctas}/{total} ({precision}%)")
    print(f"  Alucinaciones:     {(df_out['alucinacion'] == 'SÍ').sum()}")
    if latencias:
        print(f"  Latencia promedio: {round(sum(latencias)/len(latencias))} ms")
        print(f"  Latencia máxima:   {max(latencias)} ms")
        print(f"  Latencia mínima:   {min(latencias)} ms")
    print(f"{'='*60}\n")

    nombre_hoja = datetime.now().strftime("Prueba_%d%m%Y_%H%M")

    from openpyxl import load_workbook
    import os
    if os.path.exists(ARCHIVO_SALIDA):
        with pd.ExcelWriter(ARCHIVO_SALIDA, engine="openpyxl", mode="a", if_sheet_exists="new") as writer:
            df_out.to_excel(writer, sheet_name=nombre_hoja, index=False)
    else:
        df_out.to_excel(ARCHIVO_SALIDA, sheet_name=nombre_hoja, index=False)

    print(f"Resultados guardados en: {ARCHIVO_SALIDA} (hoja: {nombre_hoja})")

if __name__ == "__main__":
    evaluar()
