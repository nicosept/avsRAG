import ollama
import httpx
from typing import Any, AsyncGenerator, Dict, List, Optional
import logging
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b") # Future work for non ollama models will be needed
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
USER_ROLE = os.getenv("USER_ROLE", "user")
ASSISTANT_ROLE = os.getenv("ASSISTANT_ROLE", "assistant") # Gemma 3 uses "model" as the assistant role
CONTEXT_WINDOW = 30 # Number of messages to keep in history for context

# Set up logging
logger = logging.getLogger(__name__)

class RAG:
    """RAG (Retrieval-Augmented Generation) class for querying Ollama models.
    This class allows you to query a specified Ollama model with a list of messages
    and an optional context. It can handle both streaming and non-streaming responses.

    Args:
        context (str): Optional context to prepend to the prompt.
        stream (bool): Whether to stream the response in chunks.
    """

    # No type structure for props like in TS :(
    def __init__(
            self, 
            model_name: Optional[str] = None, 
            model_url: Optional[str] = None, 
            context: Optional[str] = None, 
            stream: bool = False
            ) -> None:
        self.model = model_name or OLLAMA_MODEL
        self.model_url = model_url or OLLAMA_URL
        self.context = context
        self.stream = stream
        self.history: List[Dict[str, str]] = []
        self._client: Optional[ollama.AsyncClient] = None
        

    @property
    def client(self) -> ollama.AsyncClient:
        """Initialization of the Ollama client."""
        if self._client is None:
            self._client = ollama.AsyncClient(host=self.model_url)
            logger.info(f"Initialized RAG with model: {self.model}, hosted at {self.model_url}")
        return self._client

    async def close(self) -> None:
        """Close the Ollama client connection."""
        if self._client:
            try:
                await self.client._client.aclose()
                logger.debug("Ollama client closed successfully.")
            except Exception as e:
                logger.error(f"Error closing Ollama client: {e}")
            finally:
                self._client = None

    def set_context(self, context: str | None) -> None:
        """Set the context for the RAG instance based."""
        self.context = context

    def clear_context(self) -> None:
        """Clear the context for the RAG instance."""
        self.context = None

    def _prepare_prompt(self, prompt: str) -> str:
        """Prepare the prompt by adding context if available."""
        if not self.history and not self.context:
            return prompt
        message = ""
        if self.history:
            prev_history = "Here is all our previous history DO NOT COPY THE FORMAT:\n"
            for i, msg in enumerate(self.history[-CONTEXT_WINDOW:]):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prev_history += f"{role.capitalize()}: {content}\n"
            message += prev_history + "\n"
        if self.context:
            message += f"You are a helpful assistant. Please use the following context to aid in the conversation:\n{self.context}\n\n"
        return message + f"USER PROMPT:\n{prompt}"

    async def query(self, prompt: str) -> AsyncGenerator[str, None]:
        """Query the Ollama model with the provided prompt and context.
        Args:
            prompt (list): A list of messages to send to the model.
        Yields:
            str: The response from the model, either as a full response or in chunks if streaming is enabled.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        prompt = self._prepare_prompt(prompt)

        try:
            if self.stream is True:
                response = await self.client.chat(
                    model=self.model,
                    messages=[{"role": USER_ROLE, "content": prompt}],
                    stream=True
                )
                model_reply = ""
                async for chunk in response:
                    if "message" not in chunk or "content" not in chunk["message"]:
                        logger.error(f"Invalid chunk format: {chunk}")
                        continue
                    content = chunk["message"]["content"]
                    model_reply += content
                    yield content
                
                # Store the full response in history if completed task
                if model_reply:
                    self.history.append({"role": USER_ROLE, "content": prompt})
                    self.history.append({"role": ASSISTANT_ROLE, "content": model_reply})
                    print(self.history)

            elif self.stream is False:
                response = await self.client.chat(
                    model=self.model,
                    messages=self.history,
                    stream=False
                )
                if response is None:
                    raise ollama.ResponseError("Empty response from model.")
                message_content = response["message"]["content"]
                self.history.append({"role": ASSISTANT_ROLE, "content": message_content})
                yield message_content

        # Custom exception classes for the RAG needed
        except ollama.ResponseError as e:
            raise RuntimeError(f"Error querying Ollama: {str(e)}")
        except httpx.ConnectError as e:
            raise ConnectionError(f"Please check your Ollama server {self.model_url}.")
        except Exception as e:
            raise RuntimeError(f"Unexpected error querying Ollama: {str(e)}")

    async def __aenter__(self) -> 'RAG':
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        await self.close()
