import json
import redis
from fastapi import FastAPI, HTTPException
from api.schemas import ChatRequest, ChatResponse
from retrieval.search_engine import search_documents
from generation.guardrails import apply_input_guardrails, apply_output_guardrails
from generation.generator import generate_rag_response

app = FastAPI(title="Mutual Fund FAQ API")

# Setup Redis with a local dict fallback
redis_client = None
sessions = {}

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
    redis_client.ping()
    print("Connected to Redis successfully.")
except (redis.ConnectionError, redis.TimeoutError):
    print("Redis not available or timed out. Falling back to in-memory session store.")
    redis_client = None

def get_history(session_id: str):
    if redis_client:
        raw_data = redis_client.lrange(session_id, 0, -1)
        return [json.loads(x) for x in raw_data]
    else:
        return sessions.get(session_id, [])

def add_history(session_id: str, query: str, response: str):
    record = {"q": query, "a": response}
    if redis_client:
        redis_client.rpush(session_id, json.dumps(record))
        redis_client.expire(session_id, 3600)  # Expire sessions after 1 hour
    else:
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append(record)

@app.get("/")
def read_root():
    return {"message": "Mutual Fund FAQ API is running."}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    # 1. Input Guardrails
    guardrail_error = apply_input_guardrails(request.query)
    if guardrail_error:
        return ChatResponse(response=guardrail_error, error=True)
    
    # 2. Retrieve Context
    try:
        docs = search_documents(request.query, k=4)
        if not docs:
             return ChatResponse(response="I'm sorry, I couldn't find relevant factual information for that query.", error=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # 3. LLM Generation
    history = get_history(request.session_id)
    chat_history_str = "\n".join([f"User: {h['q']}\nAssistant: {h['a']}" for h in history[-3:]])
    
    try:
        raw_response = generate_rag_response(request.query, docs, chat_history_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating response from LLM.")
        
    # 4. Output Guardrails
    final_response = apply_output_guardrails(raw_response)
    
    # Track history
    add_history(request.session_id, request.query, final_response)
    
    return ChatResponse(response=final_response, error=False)

