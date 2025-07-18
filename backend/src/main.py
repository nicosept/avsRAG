import os
from fastapi import FastAPI, Request, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from backend.src.rag import RAG
import asyncio
import json

load_dotenv()
PORT = int(os.environ.get("PORT", 5000))
FRONT_PORT = int(os.environ.get("FRONT_PORT", 5173))

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


@app.websocket("/ws/prompt")
async def websocket_prompt(websocket: WebSocket):
    await websocket.accept()
    async with RAG(stream=True) as rag:
        print("WebSocket connection established")
        query_task = None
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    data_json = json.loads(data)
                except json.JSONDecodeError:
                    data_json = [data]

                if isinstance(data_json, dict) and data_json.get("type") == "abort":
                    print("Aborting query")
                    query_task.cancel()
                    await websocket.send_json(
                        {"type": "aborted", "message": "Query aborted"}
                    )
                    return
                
                # If a query task is already running, cancel it
                # might want to handle this more gracefully with a queue or running multiple queries
                if query_task and not query_task.done():
                    query_task.cancel()
                

                async def query_send_data(data):
                    try:
                        async for chunk in rag.query(data):
                            if chunk is None:
                                continue
                            await websocket.send_json(
                                {"type": "message", "content": chunk}
                            )
                    except asyncio.CancelledError:
                        print("Query task cancelled")
                        pass

                query_task = asyncio.create_task(query_send_data(data_json))

        except WebSocketDisconnect:
            print("WebSocket disconnected")
        except ConnectionError as e:
            print(f"Connection error: {str(e)}")
            await websocket.send_json({"type": "error", "message": str(e)})
            await websocket.close(code=4000, reason=str(e))
        except Exception as e:
            print(f"Unknown error: {str(e)}")
            await websocket.close(code=1000, reason=str(e))


if __name__ == "__main__":
    print(f"Running backend on port {PORT}, frontend on port {FRONT_PORT}")
    uvicorn.run("main:app", port=PORT, host="127.0.0.1", reload=True, log_level="error")
