# FoodSearch - AI-Powered Recipe Search Application

FoodSearch is a full-stack web application that combines a vector database with a language model to provide intelligent recipe search and recommendation capabilities. The application allows users to search for recipes using natural language queries and receive personalized culinary suggestions based on a database of over 8,000 recipes.

## 🚀 Features

- **Vector Database Search**: Search recipes using natural language queries that match semantically against recipe content
- **AI-Powered Chat Interface**: Interactive conversation with an AI chef that provides recipe recommendations and culinary advice
- **Recipe Cards Display**: Visual presentation of search results with key recipe information
- **Semantic Search**: Understands context and intent behind search queries, not just keywords
- **Strict Context Guardrails**: AI responses are constrained to only information available in the recipe database

## 🛠️ Technologies Used

### Backend
- **FastAPI**: High-performance web framework for building APIs
- **ChromaDB**: Vector database for storing and retrieving recipe embeddings
- **OpenAI Client**: For embedding generation and LLM interactions (using local Llama.cpp server)
- **Pandas**: Data processing and CSV handling

### Frontend
- **React**: JavaScript library for building user interfaces
- **JavaScript/ES6**: Core frontend logic and state management
- **CSS**: Styling and responsive design

### AI/ML Components
- **Qwen-30B**: Large language model (configured for local execution)
- **Local Llama.cpp Server**: For running the language model locally
- **Embedding Models**: For converting text to vector representations

## 📁 Project Structure

```
.
├── backend/
│   └── main.py          # FastAPI backend with REST endpoints
├── frontend/
│   └── src/
│       └── App.jsx      # React frontend component
├── rag_engine/
│   ├── ingest.py        # Data ingestion and vector embedding pipeline
│   └── search.py        # Search and retrieval augmented generation logic
├── data/
│   └── food_recipes.csv     # Recipe dataset
└── README.md
```

## 📊 Data Pipeline

1. **Data Ingestion** (`rag_engine/ingest.py`):
   - Loads recipe data from CSV file
   - Processes and cleans recipe information
   - Generates vector embeddings using OpenAI client
   - Stores vectors in ChromaDB database

2. **Search & Retrieval** (`rag_engine/search.py`):
   - Implements hybrid search combining keyword matching and vector similarity
   - Uses semantic search to find relevant recipes
   - Applies strict context guardrails to prevent hallucinations

3. **API Layer** (`backend/main.py`):
   - Exposes REST endpoints for frontend communication
   - Routes recipe search requests to RAG pipeline
   - Handles chat interactions with AI chef

4. **Frontend Interface** (`frontend/src/App.jsx`):
   - Dual-panel interface with recipe search and AI chat
   - Real-time search results display
   - Interactive chat interface with scrolling behavior

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (optional, for local LLM server)
- Local Llama.cpp server running on port 8080

### Installation Steps

1. **Backend Setup**:
```bash
cd backend
pip install fastapi uvicorn pandas chromadb openai python-dotenv
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
```

3. **Data Preparation**:
   - Ensure `food_recipes.csv` is in the correct location
   - Run the ingestion script:
```bash
python rag_engine/ingest.py
```

4. **Start Services**:
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

## 📖 Usage

### Recipe Search
1. Enter search terms in the left panel (e.g., "spicy Italian pasta")
2. See relevant recipes displayed in card format with key information
3. Click on "View Original Recipe" to access full recipe details

### AI Chef Chat
1. Type questions in the right panel (e.g., "How to make a vegetarian version of this recipe?")
2. Get AI-generated responses based only on the information in your recipe database
3. The AI ensures responses are strictly grounded in the provided context

## 🏗️ Architecture Overview

```
[Frontend (React)] ←→ [Backend (FastAPI)] ←→ [RAG Engine] ←→ [ChromaDB]
                              ↓
                      [Local LLM Server (Llama.cpp)]
```

## 🔒 Safety Features

- **Context Guardrails**: AI responses are strictly constrained to the recipe database
- **No Hallucinations**: The system will explicitly state when it doesn't have information
- **Semantic Search**: Prevents keyword-based misinterpretation

## 📦 Requirements

### Backend Dependencies
- fastapi
- uvicorn
- pandas
- chromadb
- openai
- python-dotenv

### Frontend Dependencies
- react
- react-dom
- npm (or yarn)

## 🤝 Contributing

This project is designed as a demonstration of RAG (Retrieval Augmented Generation) capabilities for recipe search. Contributions are welcome, especially for:

- Improving the recipe dataset
- Enhancing search algorithms
- Adding new features to the frontend
- Optimizing the vector search performance

## 📄 License

This project is created for demonstration purposes showing the implementation of a recipe search system using RAG architecture.

## 🙏 Acknowledgements

- Built with FastAPI and React for a modern web experience
- Uses ChromaDB for vector storage and retrieval
- Leverages local LLM capabilities for intelligent responses
