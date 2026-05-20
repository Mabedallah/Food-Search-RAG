import os
import pandas as pd
import chromadb
from openai import OpenAI

def ingest_recipes_from_csv(csv_filename="food_recipes.csv"):
    # 1. Coordinate absolute file paths for Windows
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "data", csv_filename)
    db_path = os.path.join(current_dir, "chroma_db")
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: Could not find your CSV file at: {csv_path}")
        print("Please ensure your CSV sits inside the 'rag_engine/data/' directory.")
        return

    print(f"📖 Reading data from {csv_path}...")
    
    # Load dataset with Windows encoding protection
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='latin1')
        
    # Safeguard against NaN/null cells across your schema
    fill_defaults = {
        'recipe_title': 'Untitled Recipe', 'url': '', 'record_health': 'Unknown',
        'vote_count': 0, 'rating': 0.0, 'description': '', 'cuisine': 'Generic',
        'course': 'Main Course', 'diet': 'General', 'prep_time': '0 mins',
        'cook_time': '0 mins', 'ingredients': '', 'instructions': '',
        'author': 'Anonymous', 'tags': '', 'category': 'Food'
    }
    for col, val in fill_defaults.items():
        if col in df.columns:
            df[col] = df[col].fillna(val)

    # 2. Direct OpenAI Client Initialization targeting local Llama.cpp agent
    openai_client = OpenAI(
        base_url="http://localhost:8080/v1",
        api_key="local-no-key-needed"
    )

    # 3. Direct ChromaDB Initialization (No embedding function passed here!)
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    try:
        chroma_client.delete_collection(name="recipes")
        print("🗑️ Wiped old database collection to guarantee fresh calculations.")
    except Exception:
        pass

    # We do NOT pass an embedding_function. We manage vectors completely on our own.
    collection = chroma_client.create_collection(name="recipes")

    print(f"🚀 Ingesting {len(df)} rows. Requesting mathematical float maps directly from OpenAI client...")
    
    # Process dataset records into memory arrays
    raw_texts = []
    metadatas = []
    ids = []

    for index, row in df.iterrows():
        formatted_text = (
            f"Recipe Title: {row['recipe_title']}\n"
            f"Description: {row['description']}\n"
            f"Cuisine: {row['cuisine']} | Course: {row['course']} | Diet Type: {row['diet']}\n"
            f"Prep Time: {row['prep_time']} | Cook Time: {row['cook_time']}\n"
            f"Ingredients: {row['ingredients']}\n"
            f"Instructions: {row['instructions']}\n"
            f"Tags & Category: {row['tags']}, {row['category']}"
        )
        raw_texts.append(formatted_text)
        
        metadatas.append({
            "title": str(row['recipe_title']),
            "url": str(row['url']),
            "cuisine": str(row['cuisine']),
            "diet": str(row['diet']),
            "rating": float(row['rating']),
            "prep_time": str(row['prep_time']),
            "cook_time": str(row['cook_time'])
        })
        ids.append(f"recipe_csv_{index}")

    # 4. Batching Loop: Fetch vectors from OpenAI, then explicitly store them in Chroma
    batch_size = 32 # Local models handle manual batch sizing reliably at 32
    for i in range(0, len(raw_texts), batch_size):
        end_idx = i + batch_size
        
        batch_texts = raw_texts[i:end_idx]
        batch_metadatas = metadatas[i:end_idx]
        batch_ids = ids[i:end_idx]

        try:
            # --- THE DIRECT OPENAI EMBEDDING CALL ---
            # Explicitly demanding raw vector weights for our chunks
            response = openai_client.embeddings.create(
                input=batch_texts,
                model="qwen" # Name matches configuration in your llama-server initialization
            )
            
            # Extract raw float lists out of response payloads
            # response.data contains objects with .embedding arrays
            batch_embeddings = [record.embedding for record in response.data]

            # --- MANUALLY DELIVERING EMBEDDINGS TO CHROMADB ---
            # Because we deliver computed arrays, Chroma saves them directly without secondary calls
            collection.add(
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            print(f"✓ Explicitly processed and stored vectors for rows {i} through {min(end_idx, len(raw_texts))}")

        except Exception as error:
            print(f"❌ Critical pipeline stall during batch sequence {i}: {error}")
            return

    print(f"\n🎉 Direct RAG Ingestion successful! Stored collection registry count: {collection.count()}")

if __name__ == "__main__":
    # Matches your filename exactly
    ingest_recipes_from_csv("food_recipes.csv")