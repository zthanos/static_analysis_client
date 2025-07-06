from fastmcp import Client as FastMCPClient
from ollama import Client as OllamaClient

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-coder-v2:latest"
FASTMCP_URL = "http://localhost:9000/sse"

_ollama_client = None
_fastmcp_client = None

def get_fastmcp_client():
    global _fastmcp_client
    if not _fastmcp_client:
        _fastmcp_client = FastMCPClient(FASTMCP_URL, sampling_handler=ollana_sampling_handler)
    return _fastmcp_client


def get_ollama_client():
    global _ollama_client
    if not _ollama_client:
        _ollama_client = OllamaClient(host=OLLAMA_HOST)
    return _ollama_client

def get_ollama_model():
    return OLLAMA_MODEL

def get_fastmcp_url():
    return FASTMCP_URL


async def ollana_sampling_handler(
    messages: list,
    params,
    context,
) -> str:
    ollama_client = get_ollama_client()
    OLLAMA_MODEL = get_ollama_model()
    prompt = ""
    
    if params.systemPrompt:
        prompt += f"{params.systemPrompt}\n\n"
    
    for m in messages:
        prompt += f"{m.role}: {m.content.text}\n"
    
    prompt += "\nReturn your answer as a JSON object."

    response = ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={'temperature': 0}
    )

    return response['message']['content']