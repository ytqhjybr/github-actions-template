import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Путь к папке для хранения векторной базы
VECTOR_DB_PATH = "data/vector_db"

# Инициализация модели эмбеддингов (локальная, бесплатная)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def index_pdf(pdf_path: str):
    """
    Загружает PDF, разбивает на фрагменты и сохраняет в векторную базу.
    Возвращает количество фрагментов.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    
    # Создаём или добавляем в векторную базу
    if not os.path.exists(VECTOR_DB_PATH):
        vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=VECTOR_DB_PATH)
    else:
        vectorstore = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
        vectorstore.add_documents(chunks)
    
    vectorstore.persist()
    return len(chunks)

def search_pdf(query: str, k: int = 3):
    """
    Ищет в векторной базе k наиболее релевантных фрагментов по запросу.
    Возвращает список текстов.
    """
    if not os.path.exists(VECTOR_DB_PATH):
        return []
    vectorstore = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
    results = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in results]