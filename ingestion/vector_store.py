import os
import glob
import json
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from ingestion.chunking import split_text_into_chunks

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")

def create_or_update_vector_store():
    print("Initializing BGE Embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    print("Loading raw files and chunking...")
    all_documents = []
    
    if not os.path.exists(DATA_DIR):
        print(f"Data directory {DATA_DIR} not found. Please run the scraper first.")
        return
        
    for file_path in glob.glob(os.path.join(DATA_DIR, "*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        metadata = data.get("metadata", {})
        text = data.get("text", "")
        
        docs = split_text_into_chunks(text, metadata)
        all_documents.extend(docs)
        print(f"Chunked {os.path.basename(file_path)}: {len(docs)} segments")
        
    if all_documents:
        print(f"Creating/Updating local ChromaDB with {len(all_documents)} total chunks...")
        vectorstore = Chroma.from_documents(
            documents=all_documents,
            embedding=embeddings,
            persist_directory=CHROMA_DIR
        )
        print(f"Vector Database stored at {CHROMA_DIR}")
    else:
        print("No documents to ingest.")

if __name__ == "__main__":
    create_or_update_vector_store()
