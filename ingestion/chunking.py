from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_text_into_chunks(text, metadata, chunk_size=500, chunk_overlap=50):
    """
    Takes raw text and metadata, and splits it into a list of Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "?", "!", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    documents = []
    for chunk in chunks:
        documents.append(Document(page_content=chunk, metadata=metadata))
        
    return documents
