from fastmcp import Client as FastMCPClient
import json
from utils.mcp_tools_helper import safe_call_tool
from utils.logger import get_logger

logger = get_logger(__name__)


async def task_fetch_repository(client: FastMCPClient, repo_url: str):
    logger.info("Fetching repository")
    data, error = await safe_call_tool(
        client, "fetch_repository", {"repo_url": repo_url}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    return data


async def task_processed_repository(client: FastMCPClient, repository_name: str):
    logger.info("Processing repository")
    data, error = await safe_call_tool(
        client, "processed_repository", {"repository": repository_name}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    return data


async def task_get_map_files(client: FastMCPClient, repository_name: str):
    logger.info("Fetching maps")
    data, error = await safe_call_tool(
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
    data, error = await safe_call_tool(
        client, "find_edges", {"repository": repository_name, "filename": filename}
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_extract_flow(client: FastMCPClient, repository_name: str, filename: str):
    logger.info("Extracting flow")
    logger.info(f"Repository: {repository_name} Filename: {filename}")
    data, error = await safe_call_tool(
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
    data, error = await safe_call_tool(client, "return_workspace", {})
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_classify_repository(client: FastMCPClient, repository_name: str):
    logger.info("classify_repository")
    data, error = await safe_call_tool(
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
    data, error = await safe_call_tool(
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
    data, error = await safe_call_tool(
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
):
    logger.info("get_language_specific_prompt")
    data, error = await safe_call_tool(
        client,
        "extract_language_specific_flow",
        {
            "language": language,
            "source_code": source_code,
            "repository_name": repository_name,
            "filename": filename,
        },
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.info(data)


async def task_get_document_info(client: FastMCPClient, repository: str, filename: str):

    data, error = await safe_call_tool(
        client=client,
        tool_name="get_document_info",
        arguments={"repository": repository, "filename": filename},
        json_response=True,
    )
    if error:
        logger.error(f"Error: {error}")
        return None
    logger.debug(data)
    return data
