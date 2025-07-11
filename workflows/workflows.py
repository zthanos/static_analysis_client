from fastmcp import Client as FastMCPClient
from utils.logger import get_logger
from utils.mcp_tools_helper import (
    safe_call_tool_json,
    safe_call_tool_text,
    get_first_text,
)
from utils.mcp_utils import pretty_print_json
from utils.prompts_utils import print_agent, print_llm_response
from utils.prompts_utils import print_menu
import json

logger = get_logger(__name__)


async def workflow_fetch_and_classify_repository(client, repo_url):
    """
    Fetches a repository from a given URL and classifies it.
    Returns (repository_name, classification).
    """
    async with client:
        await client.ping()
        logger.info("Starting workflow: fetch and classify repository")

        repo_name, error = await safe_call_tool_text(client, "fetch_repository", {"repo_url": repo_url})
        if error or not repo_name:
            logger.error(f"Failed to fetch repository: {error}")
            return None

        classification, error = await safe_call_tool_text(client, "classify_repository", {"repository_name": repo_name})
        if error:
            logger.error(f"Failed to classify repository: {error}")
            return None

        print_agent(f"Repository '{repo_name}' classified as: {classification}")
        return repo_name, classification


async def workflow_get_document_information(client: FastMCPClient, repo_name: str, filename: str):
    """
    Retrieves document metadata and file content.
    Returns a combined dictionary with document info and content.
    """
    async with client:
        await client.ping()

        doc_info, error = await safe_call_tool_json(client, "get_document_info", {"repository": repo_name, "filename": filename})
        if error or not doc_info:
            logger.error(f"Failed to get document info: {error}")
            return None

        filecontent, error = await safe_call_tool_text(client, "retrieve_file_content", {"repository_name": repo_name, "filename": filename})
        if error or not filecontent:
            logger.error(f"Failed to get file content: {error}")
            return None

        result = dict(doc_info)
        result["filecontent"] = get_first_text(filecontent)

        print_agent("Document Info:")
        print_llm_response(json.dumps({k: v for k, v in result.items() if k != "filecontent"}, indent=2))

        print_llm_response("\nFile Content:\n")
        print(result["filecontent"])
        return result


async def workflow_get_document_flow(client: FastMCPClient, repo_name: str, filename: str):
    """
    Extracts execution flow from document using language-specific prompt.
    Returns structured JSON result.
    """
    async with client:
        await client.ping()

        doc_info, error = await safe_call_tool_json(client, "get_document_info", {"repository": repo_name, "filename": filename})
        if error or not doc_info:
            logger.error(f"Failed to get document info: {error}")
            return None

        source_code, error = await safe_call_tool_text(client, "retrieve_file_content", {"repository_name": repo_name, "filename": filename})
        if error or not source_code:
            logger.error(f"Failed to get source code: {error}")
            return None

        language = doc_info.get("language")
        if not language:
            logger.error("Language not detected in document info.")
            return None

        prompts, error = await safe_call_tool_json(
            client,
            "get_language_specific_prompt",
            {
                "language": language,
                "source_code": str(get_first_text(source_code)),
                "repository_name": repo_name,
                "filename": filename,
            }
        )
        if error or not prompts:
            logger.error(f"Failed to get language-specific prompt: {error}")
            return None

        json_data, error = await safe_call_tool_json(
            client,
            "extract_flow_with_specific_prompt",
            {
                "system_prompt": str(prompts.get("system_prompt")),
                "llm_prompt": str(prompts.get("llm_prompt")),
            }
        )
        if error or not json_data:
            logger.error(f"Failed to extract flow: {error}")
            return None

        pretty_print_json(json_data)
        return json_data


WORKFLOWS = [
    {
        "name": "Fetch and Classify Repository",
        "function": workflow_fetch_and_classify_repository,
        "params": ["repo_url"],
        "description": "Fetch a repository and classify it.",
    },
    {
        "name": "Get Document Info",
        "function": workflow_get_document_information,
        "params": ["repo_name", "filename"],
        "description": "Get Document Information.",
    },
    {
        "name": "Extract Document Flow",
        "function": workflow_get_document_flow,
        "params": ["repo_name", "filename"],
        "description": "Extracts the execution flow of a program, starting from its primary entry point, and returns it in structured JSON.",
    },
]


def list_workflows():
    """
    Lists all available workflows with index, name, and description.
    """
    print_menu("Available workflows:")
    for idx, wf in enumerate(WORKFLOWS, 1):
        print_menu(f"{idx}. {wf['name']} - {wf['description']}")
