import ollama


def query_ollama(model: str, prompt: str, context: str = None, stream: bool = False):
    if context:
        prompt = f"You are a helpful chatbot. Use only the following pieces of context to answer the question. Do not hallucinate nor make up new information. You are free to reply that you do not have enough context if you do not know the answer to something, not knowing is not a mistake. Only mention the context you have if DIRECTLY asked for it: {context}.\n\nQuestion: {prompt}"
        
    try:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}], stream=stream)

        if not stream:
            return response["message"]["content"]
        
        for chunk in response:
            yield chunk["message"]["content"]

    except ollama.ResponseError as e:
        if not stream:
            return f"Error querying Ollama: {e.message}"
        else:
            yield f"Error querying Ollama: {e.message}"
