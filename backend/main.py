import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- PATH HACK ---
# This allows the backend folder to import the rag_engine folder cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import your working AI functions directly from the RAG engine!
from rag_engine.search import query_rag, collection, openai_client

# Initialize the API
app = FastAPI(title="Recipe RAG API")

# --- CORS CONFIGURATION ---
# CRITICAL: This allows your React frontend (usually running on port 5173 or 3000) 
# to talk to this Python backend without being blocked by browser security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Accepts requests from any frontend port during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request format for the chat endpoint
class ChatRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {"status": "FastAPI Recipe Server is running!"}

@app.get("/api/recipes")
def get_recipe_cards(q: str):
    """
    Returns raw JSON recipe metadata for the React UI to display as cards.
    """
    try:
        # 1. Convert search term to vector
        embedding_response = openai_client.embeddings.create(
            input=[q],
            model="qwen"
        )
        vector = embedding_response.data[0].embedding
        
        # 2. Search ChromaDB
        results = collection.query(query_embeddings=[vector], n_results=3)
        
        # 3. Extract the metadata (title, cuisine, time, etc.) to send to the UI
        recipes = []
        if results['metadatas'] and results['metadatas'][0]:
            recipes = results['metadatas'][0]
                
        return {"recipes": recipes}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database search failed: {str(e)}")

@app.post("/api/chat")
def chat_with_chef(request: ChatRequest):
    """
    Passes the query to your LLM pipeline and returns the AI's recipe advice.
    """
    try:
        # Calls the exact function you just perfected in search.py!
        ai_answer = query_rag(request.query)
        return {"reply": ai_answer}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")