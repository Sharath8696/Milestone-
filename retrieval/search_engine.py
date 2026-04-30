import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")

# Keep the db instance global to avoid re-initializing it on every request
_vector_db = None

def get_vector_db():
    global _vector_db
    if _vector_db is None:
        if not os.path.exists(CHROMA_DIR):
            return None
            
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        _vector_db = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        )
    return _vector_db

def search_documents(query: str, k: int = 4):
    """
    Embeds the user query and retrieves top K relevant facts from ChromaDB.
    """
    db = get_vector_db()
    if db is None:
        raise FileNotFoundError("Vector Database not found. Please run the ingestion pipeline.")
        
    results = db.similarity_search(query, k=k)
    return results
