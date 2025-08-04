import os
from fastapi import FastAPI, Request, WebSocket, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import logging

from routes import prompts, uploads

# Load environment variables
load_dotenv()
PORT = int(os.environ.get("PORT", 5000))
FRONT_PORT = int(os.environ.get("FRONT_PORT", 5173))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


app.include_router(prompts.router, prefix="/api", tags=["prompts"])
app.include_router(uploads.router, prefix="/api", tags=["uploads"])

if __name__ == "__main__":
    print(f"Running backend on port {PORT}")
    print(f"Current frontend URL: http://localhost:{FRONT_PORT}")
    uvicorn.run("main:app", port=PORT, host="127.0.0.1", reload=True, log_level="error")
