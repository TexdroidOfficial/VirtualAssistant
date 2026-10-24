from operator import itemgetter

from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

LLM_MODEL = "gemma4:e4b-it-qat"
EMBEDDING_MODEL = "embeddinggemma-2"
DB_DIR = "./vector_db"


def process_document(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=DB_DIR)

    return vectorstore


def get_rag_chain():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatOllama(model=LLM_MODEL)

    system_prompt = (
        "Eres un asistente útil para empleados. Usa los siguientes fragmentos de contexto "
        "recuperado para responder a la pregunta. Si no sabes la respuesta, di que no lo sabes. "
        "Usa un máximo de tres oraciones y mantén la respuesta concisa.\n\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    def format_documents(documents):
        return "\n\n".join(document.page_content for document in documents)

    return (
        {
            "context": itemgetter("input") | retriever | format_documents,
            "input": itemgetter("input"),
        }
        | prompt
        | llm
        | StrOutputParser()
    )