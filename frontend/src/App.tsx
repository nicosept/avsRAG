import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState<string | null>(null);
  const [prompt, setPrompt] = useState<string>("");

  const fetchData = async () => {
    if (prompt && prompt.trim() !== "") {
      try {
        const response = await fetch("http://localhost:5000/api/prompt/" + encodeURIComponent(prompt));
        const jsonData = await response.json();
        setData(jsonData.message);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }
  }

  const wsPrompt = async () => {
    if (prompt && prompt.trim() !== "") {
      const ws = new WebSocket("ws://localhost:5000/ws/prompt");
      ws.onopen = () => {
        ws.send(prompt);
      };
      ws.onmessage = (event) => {
        setData(prevData => prevData ? prevData + event.data : event.data);
      };
      ws.onclose = () => {
        console.log("WebSocket connection closed");
      };
      return () => {
        ws.close();
      };
    }
  };

  return (
    <>
      <h1>ollama UI</h1>

      <p className="read-the-docs" style={{ whiteSpace: 'pre-line', textAlign: 'left' }}>
        {data ? data : "No response yet."}
      </p>
      <input
        type="text"
        placeholder="Type your question here"
        value={prompt || ""}
        onChange={e => setPrompt(e.target.value)}
      />
      <button onClick={() => wsPrompt()} disabled={!prompt}>
        Ask
      </button>
    </>
  )
}

export default App
