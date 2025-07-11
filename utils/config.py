from fastmcp import Client as FastMCPClient
from ollama import Client as OllamaClient

OLLAMA_HOST = "http://localhost:11434"
LLM_MODEL = "deepseek-coder-v2:latest"
FASTMCP_URL = "http://localhost:9000/sse"

_ollama_client = None
_fastmcp_client = None


def get_fastmcp_client():
    """Return singleton FastMCP client instance."""
    global _fastmcp_client
    if not _fastmcp_client:
        _fastmcp_client = FastMCPClient(
            FASTMCP_URL,
            sampling_handler=ollama_sampling_handler
        )
    return _fastmcp_client


def get_llm_client():
    """Return singleton Ollama client instance."""
    global _ollama_client
    if not _ollama_client:
        _ollama_client = OllamaClient(host=OLLAMA_HOST)
    return _ollama_client


def get_llm_model():
    """Return configured LLM model name."""
    return LLM_MODEL


def get_fastmcp_url():
    """Return configured FastMCP server URL."""
    return FASTMCP_URL


async def ollama_sampling_handler(messages: list, params, context) -> str:
    """
    Async sampling handler for FastMCP.
    Sends systemPrompt + messages to Ollama LLM and returns response content.
    """
    ollama_client = get_llm_client()
    llm_model = get_llm_model()
    prompt = ""

    if getattr(params, "systemPrompt", None):
        prompt += f"{params.systemPrompt}\n\n"

    for m in messages:
        role = getattr(m, "role", "user")
        content = getattr(getattr(m, "content", None), "text", "")
        prompt += f"{role}: {content}\n"

    prompt += "\nReturn your answer as a JSON object."

    try:
        response = ollama_client.chat(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            options={'temperature': 0}
        )
        return response.get('message', {}).get('content', '')
    except Exception as e:
        # Log and return fallback value
        print(f"[Error] ollama_sampling_handler failed: {e}")
        return '{"error": "LLM call failed."}'
