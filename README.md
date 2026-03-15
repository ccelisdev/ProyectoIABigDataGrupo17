# Asistente Empresarial Inteligente y Arquitectura RAG

## Descripción del Proyecto
Este proyecto consiste en el desarrollo de un asistente inteligente corporativo basado en una arquitectura **RAG (Retrieval-Augmented Generation)**. El sistema permite a los empleados consultar información interna como normativas, manuales y documentación técnica de forma privada y segura mediante el uso de un **modelo de lenguaje (LLM) local**. El objetivo principal es mejorar la productividad y garantizar que las respuestas estén fundamentadas exclusivamente en los datos reales de la organización, minimizando alucinaciones.

## Integrantes
* **Katherin Yulyeth Marin Hañari** – Data Engineer: Responsable de la ingesta, limpieza y estructuración documental.
* **Mario Torres Cid** – ML Engineer: Responsable del pipeline RAG, embeddings y evaluación del modelo.
* **Carlos Celis Cagigas** – Platform Engineer: Encargado de la API, integración y despliegue local.
* **Lucas Dore Romero Mesa** – Responsable BI/Producto y Repo Lead: Definición de métricas, gestión de GitHub y documentación.

## Arquitectura Resumida
La arquitectura se ha diseñado bajo un enfoque de **Soberanía de Datos**, donde todo el procesamiento ocurre en infraestructura local. Se articula a través de dos flujos principales:
* **Offline Data Pipeline (Ingesta):** Procesa documentos (PDF, TXT), realiza el fragmentado (*chunking*), genera *embeddings* locales y los almacena en la base de datos vectorial **Qdrant**.
* **Online Query Pipeline (Consulta):** Un frontend captura la consulta del usuario, el backend (FastAPI) orquesta la recuperación de fragmentos relevantes en Qdrant y el LLM local sintetiza la respuesta final.

## Tecnologías
* **Lenguajes:** Python (Backend e IA) y JavaScript/React (Frontend).
* **Frameworks:** FastAPI para la capa de servicios y API.
* **Orquestación RAG:** LangChain y LlamaIndex.
* **Base de Datos Vectorial:** Qdrant (seleccionada por su eficiencia en búsqueda semántica y gestión de metadatos).
* **Modelos de IA:** Modelos LLM Open-Source ejecutados íntegramente en local con técnicas de cuantización.

## Cómo ejecutar
> **Nota:** El proyecto se encuentra actualmente en la **Fase 1 (Documentación y Diseño Técnico)**. Las instrucciones técnicas se actualizarán a medida que se integre el código funcional en las fases posteriores.

1. **Clonación:** Clonar el repositorio mediante `git clone [url-del-repo]`.
2. **Entorno:** Configurar un entorno virtual de Python 3.x.
3. **Dependencias:** Instalar los paquetes necesarios (disponibles en futuras fases en `requirements.txt`).
4. **Infraestructura:** Se requiere una instancia local de Qdrant y capacidad de cómputo para ejecutar el modelo LLM seleccionado.
