import os
from fastapi import FastAPI, Request, WebSocket, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import logging

from backend.src.prompt_logic import prompt_logic
from backend.src.document_processor import processor

load_dotenv()
PORT = int(os.environ.get("PORT", 5000))
FRONT_PORT = int(os.environ.get("FRONT_PORT", 5173))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the vector store is initialized TEMP SOLUTION
from backend.src.vector_store import store

# Initialize FastAPI app
app = FastAPI()

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "The resource you are looking for was not found."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{FRONT_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Currently every upload clears the store, this should be improved.
# Also, only .txt files are allowed for now.

@app.post("/api/upload")
async def upload_file(file: UploadFile):
    if not store:
        raise HTTPException(status_code=500, detail="Vector store is not initialized.")
    logger.info(f"Received file upload: {file.filename}")
    store.clear_store()
    if not file.filename.endswith('.txt'):
        return {"error": "Invalid file type. Only .txt files are allowed."}
    contents = await file.read()
    if not contents:
        return {"error": "File is empty."}
    docu_processor = processor()
    processed_document = docu_processor.process_document(contents.decode('utf-8'))
    document_vectors = docu_processor.embed_texts(processed_document)
    store.add_vectors(document_vectors)
    logger.info(f"Processed and stored {len(document_vectors)} vectors from the document.")
    return {"message": "File processed and vectors stored successfully."}


@app.websocket("/ws/prompt")
async def websocket_prompt(websocket: WebSocket):
    await prompt_logic(websocket)


if __name__ == "__main__":
    print(f"Running backend on port {PORT}")
    print(f"Current frontend URL: http://localhost:{FRONT_PORT}")
    uvicorn.run("main:app", port=PORT, host="127.0.0.1", reload=True, log_level="error")
