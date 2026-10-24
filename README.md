# Virtual Assistant RAG

**Local, private RAG chatbot for operational manuals and internal documents.**

[English](#english) · [Español](#español)

---

## English

A Retrieval-Augmented Generation (RAG) system that ingests operational documents (PDFs, manuals) and answers employee questions using **fully local LLMs via Ollama**. Documents are uploaded directly from a **Streamlit** chat interface and added to a persistent vector database on the fly — no cloud APIs, no data leaving your machine.

### Features

- **Document ingestion from the UI** — upload one or more PDFs from the sidebar and index them without restarting the app.
- **Local inference end to end** — chat model and embeddings both run through Ollama.
- **Persistent vector store** — Chroma keeps embeddings on disk, so the knowledge base survives restarts.
- **Grounded answers** — responses are constrained to the retrieved context, with an explicit "I don't know" fallback.
- **Conversational interface** — Streamlit chat with message history and processing-state guards.
- **Temporary upload handling** — files are written to a temp folder only for indexing and deleted immediately afterwards.

### Architecture

```
   PDF upload (Streamlit)
            │
            ▼
   PyPDFLoader → RecursiveCharacterTextSplitter
            │        (chunk 1000 / overlap 200)
            ▼
   OllamaEmbeddings (embeddinggemma-2)
            │
            ▼
   Chroma vector database (persisted to disk)
            │
   user question
            ▼
   Retriever (top-k = 3) → prompt with context
            │
            ▼
   ChatOllama (gemma4:e4b-it-qat) → answer in the chat
```

| Layer | Technology |
| --- | --- |
| UI | Streamlit |
| Orchestration | LangChain (`langchain`, `langchain-core`) |
| LLM & embeddings | Ollama (`langchain-ollama`) |
| Vector store | Chroma (`langchain-chroma`) |
| PDF parsing | `pypdf` via `PyPDFLoader` |
| Text splitting | `langchain-text-splitters` |
| Packaging | `uv`, Python 3.12+ |

### Project structure

```
.
├── src/
│   └── virtualassistantrag/
│       ├── __init__.py     # Entry point: launches the Streamlit app
│       ├── __main__.py     # Enables `python -m virtualassistantrag`
│       ├── app.py          # Streamlit UI: upload, ingestion and chat
│       └── rag_core.py     # Ingestion pipeline, embeddings, retriever, chain
├── pyproject.toml
├── uv.lock
└── README.md
```

### Requirements

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (recommended package manager)
- **[Ollama](https://ollama.com/)** installed and running

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd VirtualAssistantRAG
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Start Ollama** (in a separate terminal, if it is not already running as a service)

   ```bash
   ollama serve
   ```

4. **Download the models**

   ```bash
   ollama pull gemma4:e4b-it-qat
   ollama pull embeddinggemma-2
   ```

   > If the chat model tag is not available in your Ollama version, pull any compatible model
   > (for example `gemma3:4b`) and update `LLM_MODEL` in `src/virtualassistantrag/rag_core.py`.

### Usage

```bash
uv run virtualassistantrag
```

The command above is the installed entry point and launches Streamlit on `app.py`. You can also run
the app directly, which is equivalent:

```bash
uv run streamlit run src/virtualassistantrag/app.py
```

Streamlit flags are forwarded, for example `uv run virtualassistantrag --server.port 8502`.
From an activated environment, `python -m virtualassistantrag` works too.

Then, in the browser:

1. **Upload a PDF** from the sidebar (*Gestión de Documentos*).
2. Click **Procesar e Ingerir** to chunk, embed and store it in the vector database.
3. Repeat for every manual you want in the knowledge base.
4. **Ask questions** in the chat box at the bottom. Answers are generated only from the retrieved fragments.

### Configuration

All tunable parameters live at the top of `src/virtualassistantrag/rag_core.py`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `LLM_MODEL` | `gemma4:e4b-it-qat` | Ollama chat model used to answer |
| `EMBEDDING_MODEL` | `embeddinggemma-2` | Ollama embedding model |
| `DB_DIR` | `./vector_db` | Chroma persistence directory |
| `chunk_size` / `chunk_overlap` | `1000` / `200` | Text splitter settings |
| `search_kwargs={"k": 3}` | `3` | Number of retrieved chunks per query |

The upload staging folder is `./documentos_temp`, defined in `app.py`. Both `vector_db/` and `documentos_temp/` are created at runtime relative to the working directory and are excluded from version control.

### How it works

1. **Load** — `PyPDFLoader` extracts text page by page.
2. **Split** — `RecursiveCharacterTextSplitter` breaks the text into overlapping chunks to preserve context across boundaries.
3. **Embed & store** — each chunk is embedded with `embeddinggemma-2` and persisted in Chroma.
4. **Retrieve** — the user's question is embedded and the 3 most similar chunks are fetched.
5. **Generate** — the chunks are injected into a Spanish system prompt that instructs the model to answer concisely (max. three sentences) and to admit when it does not know.
6. **Render** — the answer is streamed into the chat and appended to the session history.

### Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| `Error al procesar la consulta` on the first question | No documents ingested yet. Upload and process a PDF first. |
| Connection refused / model not found | Ollama is not running, or the model was not pulled. Run `ollama serve` and `ollama pull <model>`. |
| Slow first response | The model is being loaded into memory for the first time; subsequent queries are faster. |
| Poor or empty answers | The PDF may be scanned (image-only) and contain no extractable text. OCR is not included. |
| Answers ignore your latest document | Chroma accumulates documents; older, similar chunks can still be retrieved. Delete `vector_db/` to reset the knowledge base. |

### Limitations & roadmap

- PDFs must contain a text layer; scanned documents need OCR (e.g. Tesseract) first.
- The chat history is displayed but **not** sent to the LLM, so follow-up questions lack conversational memory.
- Each answer is generated in Spanish, matching the current system prompt.
- No authentication, multi-user separation or per-document deletion yet.
- Possible next steps: conversational memory, source citations, document management panel, OCR support, Docker deployment.

### License

No license file is included in this repository. Add one before distributing or reusing the code.

---

## Español

Sistema de Generación Aumentada por Recuperación (RAG) que ingiere documentos operativos (PDFs, manuales) y responde consultas de empleados usando **modelos LLM totalmente locales vía Ollama**. Los documentos se suben directamente desde un chatbot en **Streamlit** y se agregan a una base de datos vectorial persistente al instante: sin APIs en la nube y sin que los datos salgan de tu equipo.

### Características

- **Ingesta desde la interfaz** — sube uno o varios PDFs desde la barra lateral y indexalos sin reiniciar la aplicación.
- **Inferencia 100 % local** — tanto el modelo de chat como los embeddings se ejecutan con Ollama.
- **Base vectorial persistente** — Chroma guarda los embeddings en disco, por lo que la base de conocimiento sobrevive a los reinicios.
- **Respuestas fundamentadas** — las respuestas se limitan al contexto recuperado, con una salida explícita de "no lo sé" cuando corresponde.
- **Interfaz conversacional** — chat en Streamlit con historial de mensajes y bloqueo de la UI mientras se procesa.
- **Manejo temporal de archivos** — cada PDF se guarda solo para indexarlo y se elimina inmediatamente después.

### Arquitectura

```
   Subida del PDF (Streamlit)
            │
            ▼
   PyPDFLoader → RecursiveCharacterTextSplitter
            │        (chunk 1000 / overlap 200)
            ▼
   OllamaEmbeddings (embeddinggemma-2)
            │
            ▼
   Base vectorial Chroma (persistida en disco)
            │
   pregunta del usuario
            ▼
   Retriever (top-k = 3) → prompt con contexto
            │
            ▼
   ChatOllama (gemma4:e4b-it-qat) → respuesta en el chat
```

| Capa | Tecnología |
| --- | --- |
| Interfaz | Streamlit |
| Orquestación | LangChain (`langchain`, `langchain-core`) |
| LLM y embeddings | Ollama (`langchain-ollama`) |
| Base vectorial | Chroma (`langchain-chroma`) |
| Lectura de PDF | `pypdf` mediante `PyPDFLoader` |
| División de texto | `langchain-text-splitters` |
| Empaquetado | `uv`, Python 3.12+ |

### Estructura del proyecto

```
.
├── src/
│   └── virtualassistantrag/
│       ├── __init__.py     # Entry point: lanza la aplicación Streamlit
│       ├── __main__.py     # Permite `python -m virtualassistantrag`
│       ├── app.py          # Interfaz Streamlit: subida, ingesta y chat
│       └── rag_core.py     # Pipeline de ingesta, embeddings, retriever y cadena
├── pyproject.toml
├── uv.lock
└── README.md
```

### Requisitos

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (gestor de paquetes recomendado)
- **[Ollama](https://ollama.com/)** instalado y en ejecución

### Instalación

1. **Clona el repositorio**

   ```bash
   git clone <url-del-repositorio>
   cd VirtualAssistantRAG
   ```

2. **Instala las dependencias**

   ```bash
   uv sync
   ```

3. **Inicia Ollama** (en otra terminal, si no corre ya como servicio)

   ```bash
   ollama serve
   ```

4. **Descarga los modelos**

   ```bash
   ollama pull gemma4:e4b-it-qat
   ollama pull embeddinggemma-2
   ```

   > Si el tag del modelo de chat no está disponible en tu versión de Ollama, descarga cualquier
   > modelo compatible (por ejemplo `gemma3:4b`) y actualiza `LLM_MODEL` en
   > `src/virtualassistantrag/rag_core.py`.

### Uso

```bash
uv run virtualassistantrag
```

Ese comando es el entry point instalado y lanza Streamlit sobre `app.py`. También puedes ejecutar
la aplicación directamente, lo que es equivalente:

```bash
uv run streamlit run src/virtualassistantrag/app.py
```

Las opciones de Streamlit se reenvían, por ejemplo `uv run virtualassistantrag --server.port 8502`.
Desde un entorno activado también funciona `python -m virtualassistantrag`.

Luego, en el navegador:

1. **Sube un PDF** desde la barra lateral (*Gestión de Documentos*).
2. Pulsa **Procesar e Ingerir** para dividir, vectorizar y almacenar el documento en la base vectorial.
3. Repite el proceso con cada manual que quieras añadir a la base de conocimiento.
4. **Haz tus preguntas** en la caja de chat inferior. Las respuestas se generan únicamente a partir de los fragmentos recuperados.

### Configuración

Todos los parámetros ajustables están al inicio de `src/virtualassistantrag/rag_core.py`:

| Variable | Valor por defecto | Función |
| --- | --- | --- |
| `LLM_MODEL` | `gemma4:e4b-it-qat` | Modelo de chat de Ollama para responder |
| `EMBEDDING_MODEL` | `embeddinggemma-2` | Modelo de embeddings de Ollama |
| `DB_DIR` | `./vector_db` | Directorio de persistencia de Chroma |
| `chunk_size` / `chunk_overlap` | `1000` / `200` | Configuración del divisor de texto |
| `search_kwargs={"k": 3}` | `3` | Cantidad de fragmentos recuperados por consulta |

La carpeta temporal de subida es `./documentos_temp`, definida en `app.py`. Tanto `vector_db/` como `documentos_temp/` se crean en tiempo de ejecución respecto al directorio de trabajo y están excluidas del control de versiones.

### Cómo funciona

1. **Carga** — `PyPDFLoader` extrae el texto página por página.
2. **División** — `RecursiveCharacterTextSplitter` parte el texto en fragmentos con solapamiento para no perder contexto entre cortes.
3. **Vectorización y almacenamiento** — cada fragmento se convierte en embedding con `nomic-embed-text` y se guarda en Chroma.
4. **Recuperación** — la pregunta se vectoriza y se obtienen los 3 fragmentos más similares.
5. **Generación** — los fragmentos se inyectan en un prompt de sistema en español que pide respuestas concisas (máximo tres oraciones) y admite cuando no se conoce la respuesta.
6. **Respuesta** — el texto se muestra en el chat y se añade al historial de la sesión.

### Solución de problemas

| Síntoma | Causa probable / solución |
| --- | --- |
| `Error al procesar la consulta` en la primera pregunta | Aún no hay documentos ingeridos. Sube y procesa un PDF primero. |
| Conexión rechazada / modelo no encontrado | Ollama no está en ejecución o el modelo no se descargó. Ejecuta `ollama serve` y `ollama pull <modelo>`. |
| Primera respuesta muy lenta | El modelo se está cargando en memoria por primera vez; las siguientes consultas serán más rápidas. |
| Respuestas pobres o vacías | El PDF puede ser escaneado (solo imágenes) y no tener texto extraíble. No se incluye OCR. |
| Las respuestas ignoran el documento más reciente | Chroma acumula documentos y fragmentos antiguos similares pueden recuperarse. Elimina `vector_db/` para reiniciar la base de conocimiento. |

### Limitaciones y próximos pasos

- Los PDFs deben contener una capa de texto; los documentos escaneados requieren OCR (por ejemplo, Tesseract) antes de ingerirlos.
- El historial del chat se muestra pero **no** se envía al LLM, por lo que las preguntas de seguimiento carecen de memoria conversacional.
- Las respuestas se generan en español, según el prompt de sistema actual.
- Todavía no hay autenticación, separación por usuario ni eliminación de documentos individuales.
- Posibles siguientes pasos: memoria conversacional, citas de las fuentes, panel de gestión de documentos, soporte OCR y despliegue con Docker.

### Licencia

El repositorio no incluye un archivo de licencia. Añade uno antes de distribuir o reutilizar el código.
