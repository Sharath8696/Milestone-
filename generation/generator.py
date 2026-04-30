from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a strict, facts-only Mutual Fund FAQ Assistant.
You must answer the user's question using ONLY the provided CONTEXT. 

Strict Rules:
1. Provide absolutely no financial, investment advice, comparisons, or recommendations.
2. Limit your entire response to a maximum of 3 sentences.
3. You MUST include exactly one Source Link from the provided context metadata.
4. You MUST end your response with exactly this footer string (on a new line):
"Last updated from sources: <date>" (replace <date> with the date from the context).

If the answer is not contained in the context, politely state that you cannot find the exact information in the current official documents.

CHAT HISTORY:
{chat_history}

CONTEXT:
{context}
"""

def generate_rag_response(query: str, retrieved_docs: list, chat_history: str = ""):
    """
    Takes the user query and the list of retrieved context documents, 
    and returns a cited answer using Groq (Llama 3).
    """
    # Using Llama 3 via Groq
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    
    # Format the context tightly
    context_blocks = []
    for doc in retrieved_docs:
        source = doc.metadata.get("source_url", "Unknown Source")
        date = doc.metadata.get("last_updated_date", "Unknown Date")
        block = f"Source: {source} (Date: {date})\nContent: {doc.page_content}"
        context_blocks.append(block)
        
    formatted_context = "\n\n---\n\n".join(context_blocks)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "context": formatted_context,
        "chat_history": chat_history,
        "question": query
    })
    
    return response.content

