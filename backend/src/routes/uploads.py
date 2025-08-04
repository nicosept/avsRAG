from fastapi import APIRouter, UploadFile, HTTPException
import logging
from dependencies import store, embedding_manager
from backend.src.document_processor import process_document

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile):
    logger.info(f"Received file upload: {file.filename}")
    store.clear_store()
    if not file.filename or not file.filename.endswith('.txt'):
        return {"error": "Invalid file type. Only .txt files are allowed."}
    contents = await file.read()
    if not contents:
        return {"error": "File is empty."}
    processed_document = process_document(contents.decode('utf-8'))
    document_vectors = embedding_manager.embed_texts(processed_document)
    store.add_vectors(document_vectors)
    logger.info(f"Processed and stored {len(document_vectors)} vectors from the document.")
    return {"type": "info", "message": "File processed and vectors stored successfully."}

@router.get("/clear-store")
async def clear_store():
    store.clear_store()
    logger.info("Cleared the vector store.")
    return {"type": "info", "message": "Vector store cleared successfully."}