from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
import logging
from backend.src.rag import RAG

# Temporary import for the vector store, should be replaced with a proper implementation
from dependencies import store, embedding_manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/prompt/")
async def websocket_prompt(websocket: WebSocket):
    """
    Handles websocket communication for RAG queries.
    """
    await websocket.accept()
    logger.debug("WebSocket connection established")

    async with RAG(stream=True) as rag:
        logger.info("RAG instance created")
        query_task = None
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    data_json = json.loads(data)
                except json.JSONDecodeError:
                    logger.error("Received invalid JSON data")
                    await websocket.send_json({"type": "error", "content": "Invalid JSON object passed."})
                    continue
                if isinstance(data_json, dict) and data_json.get("type") == "abort":
                    logger.info("Aborting query")
                    if query_task and not query_task.done():
                        query_task.cancel()
                    await websocket.send_json({"type": "info", "content": "Query aborted"})
                    continue

                
                # might want to handle this more gracefully with a queue or running multiple queries
                if query_task and not query_task.done():
                    query_task.cancel()

                query_task = asyncio.create_task(query_send_data(rag, websocket, data_json))

        except WebSocketDisconnect:
            logger.debug("WebSocket disconnected")
        except Exception as e:
            logger.error(f"Unknown error: {str(e)}")
            await websocket.close(code=1000, reason=str(e))

async def query_send_data(rag: RAG, websocket: WebSocket, data_json: dict):
    try:
        data = data_json.get("content")
        if not data:
            await websocket.send_json({"type": "error", "content": "No content provided in the content."})
            return
        if embedding_manager and len(store.store) > 0:
            vector_prompt = embedding_manager.embed_text(data)
            results = store.search_vectors(vector_prompt)
            if not results:
                rag.set_context(None)
            else:
                context = "\n".join(results)
                rag.set_context(context)

        async for chunk in rag.query(data):
            if chunk is None:
                continue
            await websocket.send_json({
                "type": "message", 
                "content": chunk
            })
        await websocket.send_json({
            "type": "done", 
            "content": "Query completed successfully."
        })

    except asyncio.CancelledError:
        logger.info("Query task cancelled")
        print(rag.history)
    except ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        await websocket.send_json({"type": "error", "content": str(e)})
        return
    except Exception as e:
        logger.error(f"Error during query: {str(e)}")
        await websocket.send_json({"type": "error", "content": str(e)})
        return
