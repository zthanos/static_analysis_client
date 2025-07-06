import json
from utils.logger import get_logger

logger = get_logger(__name__)


def get_first_text(response_list):
    if not response_list:
        return None
    return getattr(response_list[0], "text", None)


def get_all_texts(response_list):
    return [getattr(item, "text", None) for item in response_list or []]


def has_error(response_obj):
    return getattr(response_obj, "error", None)


def parse_json_safe(text):
    if text is None:
        return None
    try:
        return json.loads(text)
    except Exception as ex:
        logger.error(f"JSON parsing failed: {ex}")
        return None


def parse_first_json(response_list):
    return parse_json_safe(get_first_text(response_list))


def parse_all_json(response_list):
    return [parse_json_safe(text) for text in get_all_texts(response_list)]


async def safe_call_tool(client, tool_name, arguments=None, timeout=None, progress_handler=None, parse_json=False):
    """
    Generic safe tool caller with optional JSON parsing.
    """
    try:
        response = await client.call_tool(
            tool_name,
            arguments,
            timeout=timeout,
            progress_handler=progress_handler
        )
        logger.info(f"Tool call '{tool_name}' succeeded.")
        data = parse_first_json(response) if parse_json else response
        return data, None
    except Exception as e:
        logger.error(f"Tool call '{tool_name}' failed: {e}")
        return None, str(e)


async def safe_call_tool_text(client, tool_name, arguments=None, timeout=None, progress_handler=None):
    return await safe_call_tool(client, tool_name, arguments, timeout, progress_handler, parse_json=False)


async def safe_call_tool_json(client, tool_name, arguments=None, timeout=None, progress_handler=None):
    return await safe_call_tool(client, tool_name, arguments, timeout, progress_handler, parse_json=True)


async def safe_get_prompt(client, name, arguments=None):
    """
    Calls a prompt, logs the process, returns (data, error).
    """
    logger.info(f"Getting prompt {name}")
    try:
        response = await client.get_prompt(name, arguments)
        logger.info(f"Prompt '{name}' response: {response}")
        return response, None
    except Exception as e:
        logger.error(f"Prompt call '{name}' failed: {e}")
        return None, str(e)
