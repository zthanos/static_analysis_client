from typing import Dict
from math import log
from fastmcp import Client as FastMCPClient
import json
from utils.mcp_tools_helper import safe_call_tool_text, safe_call_tool_json, get_first_text
from utils.logger import get_logger

logger = get_logger(__name__)


async def task_fetch_repository(client: FastMCPClient, repo_url: str):
    logger.info("Fetching repository")
    data, error = await safe_call_tool_text(
        client, "fetch_repository", {"repo_url": repo_url}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    return get_first_text(data)


async def task_processed_repository(client: FastMCPClient, repository_name: str):
    logger.info("Processing repository")
    data, error = await safe_call_tool_text(
        client, "processed_repository", {"repository": repository_name}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    return data


async def task_get_map_files(client: FastMCPClient, repository_name: str):
    logger.info("Fetching maps")
    data, error = await safe_call_tool_text(
        client, "get_map_files", {"repository": repository_name}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_extract_edges(
    client: FastMCPClient, repository_name: str, filename: str
):
    logger.info("Extracting edges")
    logger.info(f"Repository: {repository_name} Filename: {filename}")
    data, error = await safe_call_tool_text(
        client, "find_edges", {"repository": repository_name, "filename": filename}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_extract_flow(client: FastMCPClient, repository_name: str, filename: str):
    logger.info("Extracting flow")
    logger.info(f"Repository: {repository_name} Filename: {filename}")
    data, error = await safe_call_tool_text(
        client, "extract_flow", {"repository": repository_name, "filename": filename}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_return_workspace(
    client: FastMCPClient, repository_name: str, filename: str
):
    logger.info("return_workspace")
    data, error = await safe_call_tool_text(client, "return_workspace", {})
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_classify_repository(client: FastMCPClient, repository_name: str):
    logger.info("classify_repository")
    data, error = await safe_call_tool_text(
        client, "classify_repository", {"repository_name": repository_name}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_retrieve_file_content(
    client: FastMCPClient, repository_name: str, filename: str
):
    logger.info("retrieve_file_content")
    data, error = await safe_call_tool_text(
        client,
        "retrieve_file_content",
        {"repository_name": repository_name, "filename": filename},
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.debug(f"{filename} Content: {data}")
    return data


async def task_classify_document(
    client: FastMCPClient, repository_name: str, filename: str
):
    logger.info("file_classification")
    data, error = await safe_call_tool_text(
        client,
        "file_classification",
        {"repository_name": repository_name, "filename": filename},
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_get_language_specific_prompt(
    client: FastMCPClient,
    language: str,
    source_code: str,
    repository_name: str,
    filename: str,
) -> Dict:

    logger.info("get_language_specific_prompt")
    logger.debug(f"Language: {language}")
    logger.debug(f"repository_name: {repository_name}, filename: {filename}")

    data, error = await safe_call_tool_json(
        client,
        "get_language_specific_prompt",
        {
            "language": language,
            "source_code": source_code,
            "repository_name": repository_name,
            "filename": filename,
        },
    )

    if error:
        logger.error(f"Tool call error: {error}")
        return {}

    if not data or "system_prompt" not in data or "llm_prompt" not in data:
        logger.error("Invalid response structure.")
        return {}

    logger.debug(f"System Prompt: {data['system_prompt'][:200]}...")  # κόβεις για ασφάλεια μεγέθους
    logger.debug(f"LLM Prompt: {data['llm_prompt'][:200]}...")

    return {
        "system_prompt": data["system_prompt"],
        "llm_prompt": data["llm_prompt"]
    }


async def task_extract_flow_with_prompt(
    client: FastMCPClient,
    system_prompt: str,
    llm_prompt: str,
) -> Dict:

    logger.info("task_extract_flow_with_prompt")
    logger.debug(f"system_prompt: {system_prompt}")
    logger.debug(f"llm_prompt: {llm_prompt}")

    data, error = await safe_call_tool_json(
        client,
        "extract_flow_with_specific_prompt",
        {
            "system_prompt": system_prompt,
            "llm_prompt": llm_prompt,
        },
    )

    if error:
        logger.error(f"Tool call error: {error}")
        return {}

    if not data or not isinstance(data, dict):
        logger.error("Invalid response structure.")
        return {}

    logger.debug(f"Data: {str(data)[:200]}...")  # κόβεις για ασφάλεια μεγέθους

    return data



async def task_get_document_info(client: FastMCPClient, repository: str, filename: str):

    data, error = await safe_call_tool_json(
        client=client,
        tool_name="get_document_info",
        arguments={"repository": repository, "filename": filename}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.debug(data)
    return data
