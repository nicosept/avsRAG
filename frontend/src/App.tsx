import { useEffect, useRef, useState } from 'react'
import './App.css'

function App() {
  const [history, setHistory] = useState<{ role: "user" | "model"; content: string }[]>([]);
  const [prompt, setPrompt] = useState<string>("");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    wsRef.current = new WebSocket("ws://localhost:5000/ws/prompt");
    wsRef.current.onopen = () => {
      console.log("WebSocket connection established");
    };
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        console.log("WebSocket connection closed");
      }
    };
  }, []);

  const wsPrompt = async () => {
    if (!prompt && prompt.trim() === "") return;

    // Append latest prompt to history
    const newHistory = [...history, { role: "user" as const, content: prompt }];
    setHistory(newHistory);

    // Clear prompt and response
    setPrompt("");


    const ws = wsRef.current;
    if (!ws) {
      console.error("WebSocket is not initialized");
      return;
    }
    ws.send(JSON.stringify(newHistory));

    ws.onmessage = (event) => {
      if (event.data === "__END__") {

      } else {
        setHistory(prevHistory => {
          const lastEntry = prevHistory[prevHistory.length - 1];
          if (lastEntry && lastEntry.role === "model") {
            return [
              ...prevHistory.slice(0, -1),
              { ...lastEntry, content: lastEntry.content + event.data }
            ];
          }
          else {
            return [
              ...prevHistory,
              { role: "model", content: event.data }
            ];
          }
        });
      }
    };
    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };
  };

  return (
    <>
      <h1 className='header'>avsUI</h1>


      <div className='wrapper'>
        <div className='response-container'>
          <div className='response' style={{ whiteSpace: 'pre-line', textAlign: 'left' }}>
            
            {history ? history.map((log, index) => {
              return (
                <div key={index} className={log.role}>
                  <span className='role'>{log.role === "user" ? "User: " : "Model: "}</span>
                  <span className='content'>{log.content}</span>
                </div>
              );
            }) : "Type your question..."}
          </div>
          <div className="shade" />
        </div>
        <div className='bottom'>
          <input
            type="text"
            placeholder="Type your question here"
            value={prompt || ""}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => {
              if (e.key === "Enter" && prompt) {
                wsPrompt();
              }
            }}
          />
          <button onClick={wsPrompt} disabled={!prompt}>
            🪄
          </button>
        </div>
      </div>
    </>
  )
}

export default App
