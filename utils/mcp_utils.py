# utils/mcp_utils.py

import json

def pretty_print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

