import ollama
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b") # Future work for non ollama models will be needed
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
USER_ROLE = os.getenv("USER_ROLE", "user")
ASSISTANT_ROLE = os.getenv("ASSISTANT_ROLE", "assistant") # Gemma 3 uses "model" as the assistant role

class RAG:
    """RAG (Retrieval-Augmented Generation) class for querying Ollama models.
    This class allows you to query a specified Ollama model with a list of messages
    and an optional context. It can handle both streaming and non-streaming responses.
    """


    def __init__(self, context: str = None, stream: bool = False):
        self.model = OLLAMA_MODEL
        self.llm_client = ollama.AsyncClient(host=OLLAMA_URL)
        self.stream = stream
        self.history = []
        self.context = context

    async def close(self):
        await self.llm_client._client.aclose()



    def set_context(self, context: str):
        """Set the context for the RAG instance based."""
        self.context = context

    async def query(self, prompt: str):
        """Query the Ollama model with the provided prompt and context.
        Args:
            prompt (list): A list of messages to send to the model.
        Yields:
            str: The response from the model, either as a full response or in chunks if streaming is enabled.
        """

        try:
            if self.context:
                prompt = "You are a helpful assistant. Please use the following context to aide in the conversation:\n" + self.context + "\n\nPrompt:\n" + prompt

            self.history.append({"role": USER_ROLE, "content": prompt})

            response = await self.llm_client.chat(
                model=self.model, 
                messages=self.history, 
                stream=self.stream
                )
            if not response:
                raise ollama.ResponseError("No response from model.")

            if self.stream:
                model_reply = ""
                async for chunk in response:
                    content = chunk["message"]["content"]
                    model_reply += content
                    yield content
                self.history.append({"role": ASSISTANT_ROLE, "content": model_reply})
            else:
                response = await response
                self.history.append(response)
                yield response["message"]["content"]


        except ollama.ResponseError as e:
            raise RuntimeError(f"Error querying Ollama: {e.message}")
        except httpx.ConnectError as e:
            raise ConnectionError(f"Connection attempt failed. Please check your Ollama server.")
        except Exception as e:
            raise RuntimeError(f"Unexpected error querying Ollama: {str(e)}")

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
