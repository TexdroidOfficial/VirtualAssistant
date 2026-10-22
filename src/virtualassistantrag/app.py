import streamlit as st
import os
from virtualassistantrag.rag_core import process_document, get_rag_chain

st.set_page_config(page_title="RAG Operativo Local", layout="wide")
st.title("Chatbot de Manuales Operativos")

# Definir la carpeta dedicada para almacenar los documentos temporalmente
DOCS_DIR = "./documentos_temp"
os.makedirs(DOCS_DIR, exist_ok=True)

# 1. Variables de estado para control de UI
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Controla la llave del widget de archivos para forzar su limpieza
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Barra lateral para la carga de documentos
with st.sidebar:
    st.header("Gestión de Documentos")
    
    if st.session_state.get("upload_success", False):
        st.success("¡Documento ingerido a la base de datos!")
        st.session_state.upload_success = False
    
    # El widget usa el key dinámico. Al cambiar el key, el widget desaparece y se crea uno nuevo vacío.
    uploaded_file = st.file_uploader(
        "Sube un manual en PDF",
        type="pdf",
        key=f"uploader_{st.session_state.uploader_key}",
        disabled=st.session_state.is_processing
    )
    
    if st.button("Procesar e Ingerir", disabled=st.session_state.is_processing):
        if uploaded_file is not None:
            with st.spinner("Procesando documento..."):
                temp_path = os.path.join(DOCS_DIR, uploaded_file.name)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                process_document(temp_path)
                os.remove(temp_path)
                
                st.session_state.uploader_key += 1
                st.session_state.upload_success = True
                st.rerun()
        else:
            st.warning("Por favor, sube un documento primero.")

# Mostrar el historial de chat en la interfaz
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# La caja de chat se deshabilita si la IA está procesando una respuesta
if prompt := st.chat_input("Haz una pregunta sobre los manuales operativos...", disabled=st.session_state.is_processing):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Buscando en la base de datos..."):
            try:
                # Marcamos el estado como procesando (previene interacciones encoladas)
                st.session_state.is_processing = True
                rag_chain = get_rag_chain()
                answer = rag_chain.invoke({"input": prompt})
                st.markdown(answer)
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error al procesar la consulta: Asegúrate de haber ingerido un documento primero. ({e})")
            finally:
                # Liberamos la interfaz cuando termine (incluso si hay error)
                st.session_state.is_processing = False