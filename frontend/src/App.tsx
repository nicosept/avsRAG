import { useEffect, useState, useRef } from 'react'
import useWebSocket from './hooks/useWebSocket'
import ReactMarkdown from 'react-markdown'

import { showToast, ToastContainer } from './components/Toast'
import { FileUpload } from './FileUpload'
import './App.css'
import './AppChat.css'


const USER_ROLE = import.meta.env.USER_ROLE || "user";
const ASSISTANT_ROLE = import.meta.env.ASSISTANT_ROLE || "model"; // Gemma 3 uses "model" as the assistant role
const debug = true;

function App() {
  const [history, setHistory] = useState<{ role: string; content: string, flags?: string }[]>([]);
  const [prompt, setPrompt] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);

  const responseRef = useRef<HTMLDivElement>(null);

  const [sendMessage] = useWebSocket((event: MessageEvent) => {
    let data: any;
    try {
      data = typeof event.data === "string" ? JSON.parse(event.data) : event.data;
    } catch {
      if (debug) console.error("Failed to parse WebSocket message:", event.data);
      return;
    }
    if (data.type === "error") {
      const errorMessage = data.content || "An unknown error occurred";
      if (debug) console.error(`WebSocket Error: ${errorMessage}`);
      showToast(`❗ ${errorMessage}`, 5000);
      return;
    }
    if (data.type === "info") {
      const statusMessage = data.content || "Unknown status.";
      showToast(`ℹ️ ${statusMessage}`, 3000);
      return;
    }
    if (data.type === "done") {
      setBusy(false);
      return;
    }
    if (data.type === "message") {
      const chunk = data.content || "";
      setHistory(prevHistory => {
        const newHistory = [...prevHistory];
        const lastEntry = newHistory[newHistory.length - 1];

        if (lastEntry && lastEntry.role === ASSISTANT_ROLE) {
          newHistory[prevHistory.length - 1] = {
            ...newHistory[prevHistory.length - 1],
            content: newHistory[prevHistory.length - 1].content + chunk
          };
          return newHistory;
        }
        else {
          return [...prevHistory, { role: ASSISTANT_ROLE, content: chunk }];
        }
      });
    }
  }, debug)

  useEffect(() => {
    if (responseRef.current) {
      responseRef.current.scrollTo({ top: responseRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [history]);

  const wsPrompt = async () => {
    if (!prompt || prompt.trim() === "") return;
    setBusy(true);

    const newHistory = [...history, { role: USER_ROLE, content: prompt }];
    setHistory(newHistory);
    const built_prompt = {
      type: "content",
      content: prompt,
    };
    sendMessage(JSON.stringify(built_prompt));
    setPrompt("");
  };

  const handleAbort = () => {
    if (debug) console.log("Aborting current operation");
    sendMessage(JSON.stringify({ type: "abort" }));
    setBusy(false);
    setHistory(prevHistory => {
      const lastEntry = prevHistory[prevHistory.length - 1];
      if (lastEntry && lastEntry.role === ASSISTANT_ROLE) {
        lastEntry.flags = "aborted";
      }
      return prevHistory;
    });
  }

  return (
    <>
      <ToastContainer />
      <h1 className='header'>🧠🗃️</h1>
      <div className='wrapper'>
        <div className='response-container' ref={responseRef}>
          {history.length === 0
            ? (<div className="default-message"></div>)
            : history.map((log, index) => {
              return (
                <div key={index} className={log.role === USER_ROLE ? "user-container" : "model-container"}>
                  {log.role === USER_ROLE && <div className='user-message'>

                    <span className='content'>{log.content}</span>
                  </div>}
                  {log.role === ASSISTANT_ROLE && <div className={`model-message ${log.flags || ""}`}>

                    <span className='content'>
                      <ReactMarkdown>{log.content}</ReactMarkdown>
                    </span>
                  </div>}
                </div>
              );
            })}
        </div>
        <div className='bottom'>
          <div className='input-container'>
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
            <button onClick={busy ? handleAbort : wsPrompt} disabled={busy ? false : !prompt}>
              {busy ? "⏳" : "🪄"}
            </button>
          </div>
          <FileUpload />
        </div>
      </div>
    </>
  )
}

export default App
