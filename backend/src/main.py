import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from rag import query_ollama

load_dotenv()
PORT = int(os.environ.get("PORT", 5000))
VITE_PORT = int(os.environ.get("VITE_PORT", 5173))

app = FastAPI()
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "The resource you are looking for was not found."}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{VITE_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/prompt/{prompt}')
async def prompt(prompt: str):
    return {"message": query_ollama("gemma3:4b", prompt)}

if __name__ == "__main__":
    import uvicorn
    print(f"Running on port {PORT}, Vite on {VITE_PORT}")
    uvicorn.run("main:app", port=PORT, host="127.0.0.1", reload=True)