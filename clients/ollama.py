from utils.logger import get_logger

logger = get_logger(__name__)

async def stream_chat(ollama_client, llm_model, chat_history):
    """
    Asynchronous generator that streams LLM responses chunk by chunk.

    Args:
        ollama_client: Ollama client instance.
        llm_model (str): Model name to use (e.g., 'mistral').
        chat_history (list): List of message dictionaries with roles and content.

    Yields:
        str: A chunk of the LLM's response content.
    """
    try:
        completion = ollama_client.chat(
            model=llm_model,
            messages=chat_history,
            stream=True  # Enable streaming
        )
    except Exception as e:
        # Log or handle connection error at start
        logger.error(f"[Error] Failed to start streaming: {e}")
        return

    # Yield response chunks as they arrive
    for chunk in completion:
        try:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']
        except Exception as e:
            # Log or skip individual bad chunk
            logger.error(f"[Warning] Skipping bad chunk: {e}")
            continue


def chat(ollama_client, llm_model, prompt):
    """
    Synchronous LLM call that returns the full response (non-streaming).

    Args:
        ollama_client: Ollama client instance.
        llm_model (str): Model name to use (e.g., 'mistral').
        prompt (str): User input to send.

    Returns:
        str: Full content of the LLM's response.
    """
    try:
        response = ollama_client.chat(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            options={'temperature': 0}
        )
        return response['message']['content']
    except Exception as e:
        # Log or handle call failure
        logger.error(f"[Error] Failed to get response: {e}")
        return ""
