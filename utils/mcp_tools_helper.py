import json
from utils.logger import get_logger

logger = get_logger(__name__)

def get_first_text(response_list):
    """
    Returns the .text attribute of the first response object.
    """
    if not response_list:
        return None
    return getattr(response_list[0], "text", None)

def get_all_texts(response_list):
    """
    Returns a list of .text attributes from all response objects.
    """
    return [getattr(item, "text", None) for item in response_list]

def has_error(response_obj):
    return getattr(response_obj, "error", None)

def parse_first_json(response_list):
    """
    Parses the .text attribute of the first response object as JSON.
    Returns the parsed object, or None if parsing fails.
    """
    text = get_first_text(response_list)
    if text is None:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None

def parse_all_json(response_list):
    """
    Parses all .text attributes as JSON.
    Returns a list of parsed objects (or None for failed parses).
    """
    results = []
    for text in get_all_texts(response_list):
        try:
            if text is not None:
                results.append(json.loads(text))
            else:
                results.append(None)
        except Exception:
            results.append(None)
    return results

async def safe_call_tool(client, tool_name, arguments=None, timeout=None, progress_handler=None):
    """
    Calls a tool on the server, handling ToolError and RuntimeError.
    Returns (data, error): data is the parsed response, error is an error message or None.
    """
    try:
        response = await client.call_tool(
            tool_name,
            arguments,
            timeout=timeout,
            progress_handler=progress_handler
        )
        data = parse_first_json(response)
        logger.info(f"Tool call '{tool_name}' succeeded.")
        return data, None
    except Exception as e:
        logger.error(f"Tool call '{tool_name}' failed: {e}")
        return None, str(e)


async def safe_get_prompt(client, name, arguments=None):
    """
    Calls a tool on the server, handling ToolError and RuntimeError.
    Returns (data, error): data is the parsed response, error is an error message or None.
    """
    logger.info(f"Getting prompt {name}")
    try:
        response = await client.get_prompt(
            name,
            arguments
        )
        logger.info(f"Response: {response}")
        # data = parse_first_json(response)
        return response, None
    except Exception as e:
        logger.error(f"Tool call '{name}' failed: {e}")
        return None, str(e)
