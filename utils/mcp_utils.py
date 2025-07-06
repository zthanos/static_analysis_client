# utils/mcp_utils.py
from utils.config import get_ollama_client, get_ollama_model
import json

def pretty_print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

