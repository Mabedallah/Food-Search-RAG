import os
import chromadb
from openai import OpenAI

openai_client = OpenAI(
    base_url="http://localhost:8080/v1", 
    api_key="local-no-key-needed"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_collection(name="recipes")

def query_rag(user_prompt: str) -> str:
    print(f"\n--- DEBUG: STARTING SEARCH FOR '{user_prompt}' ---")
    retrieved_docs = []

    # 1. HYBRID STEP: Keyword/Title Fallback Match
    # Let's search metadata directly to see if the user typed an exact recipe title
    try:
        # We look for an exact case-insensitive match or contains match in our local memory
        # Chroma allows metadata filtering, but since we have them locally, a quick pass is highly reliable
        all_meta = collection.get(include=["metadatas", "documents"])
        
        for idx, meta in enumerate(all_meta['metadatas']):
            # Check if the query is hidden inside the title
            if user_prompt.lower().strip() in meta['title'].lower().strip():
                print(f"🎯 [Hybrid Match] Found exact/partial title match in metadata: '{meta['title']}'")
                retrieved_docs.append(all_meta['documents'][idx])
                break # Found it, pull it in!
    except Exception as e:
        print(f"⚠️ Hybrid metadata check skipped: {e}")

    # 2. VECTOR SEARCH STEP (If hybrid didn't find enough, or to complement it)
    if len(retrieved_docs) < 3:
        try:
            embedding_response = openai_client.embeddings.create(
                input=[user_prompt],
                model="qwen" 
            )
            user_query_vector = embedding_response.data[0].embedding

            results = collection.query(
                query_embeddings=[user_query_vector],
                n_results=3
            )
            
            # Add vector results to our document pool, avoiding duplicates
            if results['documents'] and results['documents'][0]:
                for doc in results['documents'][0]:
                    if doc not in retrieved_docs:
                        retrieved_docs.append(doc)
                        
        except Exception as e:
            print(f"❌ Vector search failed: {e}")
            return "Error calculating vector pathways."

    # Trim down to the top 3 best matching documents total
    retrieved_docs = retrieved_docs[:3]

    # --- PRINT WHAT WAS ACTUALLY RETRIEVED TO TERMINAL ---
    print(f"📦 [ChromaDB Fetched {len(retrieved_docs)} Documents]")
    for i, doc in enumerate(retrieved_docs):
        # Print just the first line (the title line) of what was fetched
        first_line = doc.split('\n')[0] if doc else "Empty"
        print(f"   -> Result #{i+1}: {first_line}")
    print("--------------------------------------------------\n")

    if not retrieved_docs:
        return "I'm sorry, I couldn't find any recipes matching that request in my database."

    # Merge contexts
    retrieved_context = "\n\n=== RECIPE RECORD ===\n\n".join(retrieved_docs)
    
    # 3. STRICT SYSTEM PROMPT (No Hallucinations Allowed!)
    system_prompt = (
        "You are a strict recipe lookup system. Your ONLY source of knowledge is the provided Context.\n"
        "RULES:\n"
        "1. If the Context contains recipes that match the user's request, show them clearly.\n"
        "2. If the Context does not contain a relevant recipe, or if the context is empty, you MUST say exactly: "
        "'I am sorry, but I do not have that recipe in my local database.'\n"
        "3. NEVER use your own pre-trained knowledge to invent or supply recipes that are missing from the text below.\n"
        "4. Be concise and completely honest about your context boundaries."
    )
    
    user_content = f"Context:\n{retrieved_context}\n\nUser Request: {user_prompt}"

    try:
        ai_response = openai_client.chat.completions.create(
            model="qwen",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0 # CRITICAL: Drop temperature to 0.0 for deterministic, strict answers
        )
        return ai_response.choices[0].message.content
    except Exception as e:
        return f"Error executing generation sequence: {e}"

if __name__ == "__main__":
    print(f"🍽️ Local RAG System Online. Total Indexed Recipes: {collection.count()}")
    while True:
        user_input = input("\n👤 Search item (or 'quit'): ")
        if user_input.lower() in ['quit', 'exit']:
            break
        print(f"\n🤖 AI Chef:\n{query_rag(user_input)}")