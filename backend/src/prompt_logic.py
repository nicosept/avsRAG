from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
import logging

from backend.src.rag import RAG
from backend.src.document_processor import processor
from backend.src.vector_store import store

logger = logging.getLogger(__name__)

async def prompt_logic(websocket: WebSocket):
    """
    Handles websocket communication for RAG queries.
    """
    await websocket.accept()
    logger.info("WebSocket connection established")


    # REALLY TEMPORARY, should be replaced with a proper vector store
    # Current lifespan of the vector store is tied to the websocket connection
    doc_processor = None

    async with RAG(stream=True) as rag:
        logger.info("RAG instance created")
        query_task = None
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    data_json = json.loads(data)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                    await websocket.send_json({"type": "error", "message": "Invalid JSON object passed."})
                    continue

                if isinstance(data_json, dict) and data_json.get("type") == "abort":
                    logger.info("Aborting query")
                    if query_task and not query_task.done():
                        query_task.cancel()
                    await websocket.send_json({"type": "aborted", "message": "Query aborted"})
                    return
                
                # might want to handle this more gracefully with a queue or running multiple queries
                if query_task and not query_task.done():
                    query_task.cancel()

                    
                if store and len(store.store) > 0:
                    logger.info("Using existing vector store")
                    doc_processor = processor()
                    logger.info("Document processor initialized")
                else:
                    doc_processor = None

                query_task = asyncio.create_task(query_send_data(data_json, rag, websocket, doc_processor))

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"Unknown error: {str(e)}")
            await websocket.close(code=1000, reason=str(e))

async def query_send_data(data, rag: RAG, websocket: WebSocket, doc_processor: processor = None):
    try:
        if doc_processor:
            logger.info("Processing prompt")
            vector_prompt = doc_processor.embed_prompt(data)
            results = store.search_vectors(vector_prompt)
            context = "\n".join(results) if results else None
            rag.set_context(context)

        async for chunk in rag.query(data):
            if chunk is None:
                continue
            await websocket.send_json(
                {"type": "message", "content": chunk}
            )
    except asyncio.CancelledError:
        logger.info("Query task cancelled")
    except ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        await websocket.send_json({"type": "error", "message": str(e)})
        return
    except Exception as e:
        logger.error(f"Error during query: {str(e)}")
        await websocket.send_json({"type": "error", "message": str(e)})
        return
