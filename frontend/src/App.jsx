// import React, { useState } from 'react';
// import './App.css';

// try {
//   // Use a conditional import or block to avoid parser noise
// } catch(e) {}

// function App() {
//   // Database Search State (Left Side)
//   const [searchQuery, setSearchQuery] = useState('');
//   const [recipes, setRecipes] = useState([]);
//   const [loadingRecipes, setLoadingRecipes] = useState(false);

//   // AI Chatbot State (Right Side)
//   const [chatQuery, setChatQuery] = useState('');
//   const [chatHistory, setChatHistory] = useState([
//     { role: 'assistant', text: 'Hello! I am your AI Chef. Search for recipes on the left, or ask me any culinary questions here!' }
//   ]);
//   const [loadingChat, setLoadingChat] = useState(false);

//   // 1. Fetch raw matching recipes from ChromaDB metadata
//   const handleRecipeSearch = async (e) => {
//     e.preventDefault();
//     if (!searchQuery.trim()) return;

//     setLoadingRecipes(true);
//     try {
//       const response = await fetch(`http://127.0.0.1:8000/api/recipes?q=${encodeURIComponent(searchQuery)}`);
//       const data = await response.json();
//       setRecipes(data.recipes || []);
//     } catch (error) {
//       console.error("Error fetching recipes:", error);
//     } finally {
//       setLoadingRecipes(false);
//     }
//   };

//   // 2. Send prompts to the strict RAG pipeline
//   const handleChatSubmit = async (e) => {
//     e.preventDefault();
//     if (!chatQuery.trim() || loadingChat) return;

//     const userMessage = chatQuery;
//     setChatQuery(''); // Clear input bar immediately
//     setChatHistory(prev => [...prev, { role: 'user', text: userMessage }]);
//     setLoadingChat(true);

//     try {
//       const response = await fetch('http://127.0.0.1:8000/api/chat', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ query: userMessage })
//       });
//       const data = await response.json();
      
//       setChatHistory(prev => [...prev, { role: 'assistant', text: data.reply }]);
//     } catch (error) {
//       setChatHistory(prev => [...prev, { role: 'assistant', text: '❌ Failed to communicate with the kitchen backend.' }]);
//     } finally {
//       setLoadingChat(false);
//     }
//   };

//   return (
//     <div className="app-container">
      
//       <div className="panel database-panel">
//         <h2>🔍 Vector DB Explorer</h2>
//         <p className="subtitle">Queries match semantically against 8,000+ CSV records</p>
        
//         <form onSubmit={handleRecipeSearch} className="search-box">
//           <input 
//             type="text" 
//             placeholder="Search ingredients, cuisines, titles..." 
//             value={searchQuery}
//             onChange={(e) => setSearchQuery(e.target.value)}
//           />
//           <button type="submit">{loadingRecipes ? '...' : 'Search'}</button>
//         </form>

//         <div className="recipe-results">
//           {recipes.length === 0 && !loadingRecipes && (
//             <div className="empty-state">No context rows loaded. Try typing an ingredient above!</div>
//           )}
          
//           {recipes.map((recipe, index) => (
//             <div key={index} className="recipe-card">
//               <h3>{recipe.title}</h3>
//               <div className="badges">
//                 <span className="badge cuisine">{recipe.cuisine}</span>
//                 <span className="badge diet">{recipe.diet}</span>
//               </div>
//               <p>⏱️ Prep: {recipe.prep_time} | Cook: {recipe.cook_time}</p>
//               <div className="rating">⭐ Rating: {recipe.rating} / 5</div>
//               {recipe.url && <a href={recipe.url} target="_blank" rel="noreferrer" className="recipe-link">View Original Recipe ↗</a>}
//             </div>
//           ))}
//         </div>
//       </div>

      
//       <div className="panel chat-panel">
//         <h2>🍳 Interactive AI Chef</h2>
//         <p className="subtitle">Qwen-30B gated strictly by vector context guardrails</p>

//         <div className="chat-stream">
//           {chatHistory.map((msg, idx) => (
//             <div key={idx} className={`message-bubble ${msg.role}`}>
//               <div className="avatar">{msg.role === 'user' ? '👤' : '🤖'}</div>
//               <div className="message-text">{msg.text}</div>
//             </div>
//           ))}
//           {loadingChat && (
//             <div className="message-bubble assistant thinking">
//               <div className="avatar">🤖</div>
//               <div className="message-text">Analyzing database parameters and compounding answer...</div>
//             </div>
//           )}
//         </div>

//         <form onSubmit={handleChatSubmit} className="chat-input-bar">
//           <input 
//             type="text" 
//             placeholder="Ask the AI Chef to adapt a recipe, build meal plans, or check ingredients..." 
//             value={chatQuery}
//             onChange={(e) => setChatQuery(e.target.value)}
//             disabled={loadingChat}
//           />
//           <button type="submit" disabled={loadingChat}>Send</button>
//         </form>
//       </div>
//     </div>
//   );
// }

// export default App;

import React, { useState, useEffect, useRef } from 'react'; // 1. Added useEffect and useRef
import './App.css';

function App() {
  // Database Search State (Left Side)
  const [searchQuery, setSearchQuery] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [loadingRecipes, setLoadingRecipes] = useState(false);

  // AI Chatbot State (Right Side)
  const [chatQuery, setChatQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', text: 'Hello! I am your AI Chef. Search for recipes on the left, or ask me any culinary questions here!' }
  ]);
  const [loadingChat, setLoadingChat] = useState(false);

  // 2. Create a reference pointer for the bottom of the chat box
  const chatBottomRef = useRef(null);

  // 3. Automatically trigger scroll behavior when history changes or thinking starts
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, loadingChat]);

  // 1. Fetch raw matching recipes from ChromaDB metadata
  const handleRecipeSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoadingRecipes(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/recipes?q=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      setRecipes(data.recipes || []);
    } catch (error) {
      console.error("Error fetching recipes:", error);
    } finally {
      setLoadingRecipes(false);
    }
  };

  // 2. Send prompts to the strict RAG pipeline
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatQuery.trim() || loadingChat) return;

    const userMessage = chatQuery;
    setChatQuery(''); // Clear input bar immediately
    setChatHistory(prev => [...prev, { role: 'user', text: userMessage }]);
    setLoadingChat(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
      });
      const data = await response.json();
      
      setChatHistory(prev => [...prev, { role: 'assistant', text: data.reply }]);
    } catch (error) {
      setChatHistory(prev => [...prev, { role: 'assistant', text: '❌ Failed to communicate with the kitchen backend.' }]);
    } finally {
      setLoadingChat(false);
    }
  };

  return (
    <div className="app-container">
      {/* LEFT SIDEBAR: VECTOR DATABASE TRACKER */}
      <div className="panel database-panel">
        <h2>🔍 Vector DB Explorer</h2>
        <p className="subtitle">Queries match semantically against 8,000+ CSV records</p>
        
        <form onSubmit={handleRecipeSearch} className="search-box">
          <input 
            type="text" 
            placeholder="Search ingredients, cuisines, titles..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit">{loadingRecipes ? '...' : 'Search'}</button>
        </form>

        <div className="recipe-results">
          {recipes.length === 0 && !loadingRecipes && (
            <div className="empty-state">No context rows loaded. Try typing an ingredient above!</div>
          )}
          
          {recipes.map((recipe, index) => (
            <div key={index} className="recipe-card">
              <h3>{recipe.title}</h3>
              <div className="badges">
                <span className="badge cuisine">{recipe.cuisine}</span>
                <span className="badge diet">{recipe.diet}</span>
              </div>
              <p>⏱️ Prep: {recipe.prep_time} | Cook: {recipe.cook_time}</p>
              <div className="rating">⭐ Rating: {recipe.rating} / 5</div>
              {recipe.url && <a href={recipe.url} target="_blank" rel="noreferrer" className="recipe-link">View Original Recipe ↗</a>}
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT SIDEBAR: STRICT RAG CHAT INTERFACE */}
      <div className="panel chat-panel">
        <h2>🍳 Interactive AI Chef</h2>
        <p className="subtitle">Qwen-30B gated strictly by vector context guardrails</p>

        <div className="chat-stream">
          {chatHistory.map((msg, idx) => (
            <div key={idx} className={`message-bubble ${msg.role}`}>
              <div className="avatar">{msg.role === 'user' ? '👤' : '🤖'}</div>
              <div className="message-text">{msg.text}</div>
            </div>
          ))}
          {loadingChat && (
            <div className="message-bubble assistant thinking">
              <div className="avatar">🤖</div>
              <div className="message-text">Analyzing database parameters and compounding answer...</div>
            </div>
          )}
          
          {/* 4. Invisible anchor element used to calculate viewport offset mapping */}
          <div ref={chatBottomRef} />
        </div>

        <form onSubmit={handleChatSubmit} className="chat-input-bar">
          <input 
            type="text" 
            placeholder="Ask the AI Chef to adapt a recipe, build meal plans, or check ingredients..." 
            value={chatQuery}
            onChange={(e) => setChatQuery(e.target.value)}
            disabled={loadingChat}
          />
          <button type="submit" disabled={loadingChat}>Send</button>
        </form>
      </div>
    </div>
  );
}

export default App;