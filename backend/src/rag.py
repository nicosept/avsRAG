import ollama
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

USER_ROLE = os.getenv("USER_ROLE", "user")
ASSISTANT_ROLE = os.getenv("ASSISTANT_ROLE", "assistant") # Gemma 3 uses "model" as the assistant role

class RAG:
    """RAG (Retrieval-Augmented Generation) class for querying Ollama models.
    This class allows you to query a specified Ollama model with a list of messages
    and an optional context. It can handle both streaming and non-streaming responses.
    """

    def __init__(self, context: str = None, stream: bool = False):
        self.model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
        self.embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        self.llm_client = ollama.AsyncClient(
            host=os.getenv("OLLAMA_URL", "http://localhost:11434")
        )
        self.history = []
        self.context = context
        self.stream = stream

    async def close(self):
        print("Closing RAG instance")
        await self.llm_client._client.aclose()

    def embed_prompt(self, prompt: str):
        """Convert a prompt string into a vector."""
        vector = ollama.embed(model='')

    def set_context(self, context: str):
        """Set the context for the RAG instance."""
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
                prompt = self.context + "\n\n" + prompt

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


# def query_ollama(model: str, messages: list, context: str = None, stream: bool = False):
#     if context:
#         messages = [ messages, {
#             "role": "user",
#             "content": (
#                 "You are a helpful chatbot. Use only the following pieces of context to answer the question. "
#                 "Do not hallucinate nor make up new information. You are free to reply that you do not have enough context "
#                 "if you do not know the answer to something, not knowing is not a mistake. Only mention the context you have "
#                 "if DIRECTLY asked for it: " + context + "\n\n" + messages[-1]["content"]
#             )
#         }]
#     try:
#         # print(f"Querying Ollama model: {model} with messages: {messages} and stream={stream}")
#         response = ollama.chat(model=model, messages=messages, stream=stream)

#         if not stream:
#             return response["message"]["content"]

#         for chunk in response:
#             yield chunk["message"]["content"]

#     except ollama.ResponseError as e:
#         if not stream:
#             return f"Error querying Ollama: {e.message}"
#         else:
#             yield f"Error querying Ollama: {e.message}"
