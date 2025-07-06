from fastmcp import Client as FastMCPClient
from tasks.tasks import (
    task_fetch_repository,
    task_classify_repository,
    task_processed_repository,
    task_get_document_info,
    task_retrieve_file_content,
    task_get_language_specific_prompt,
    task_extract_flow_with_prompt
)
from utils.logger import get_logger
from utils.mcp_utils import pretty_print_json
from utils.mcp_tools_helper import get_first_text

import json

logger = get_logger(__name__)

async def workflow_fetch_and_classify_repository(client, repo_url):
    logger.info("Starting workflow: fetch and classify repository")
    repo_name = await task_fetch_repository(client, repo_url)
    if not repo_name:
        logger.error("Failed to fetch repository.")
        return None
    classification = await task_classify_repository(client, repo_name)
    return repo_name, classification

async def workflow_fetch_classify_and_list_files(client, repo_url):
    logger.info("Starting workflow: fetch, classify, and list files")
    repo_name = await task_fetch_repository(client, repo_url)
    if not repo_name:
        logger.error("Failed to fetch repository.")
        return None
    classification = await task_classify_repository(client, repo_name)
    files = await task_processed_repository(client, repo_name)
    return repo_name, classification, files

async def wf_get_document_flow(client: FastMCPClient, repository_name: str, filename: str):
    document_info = await task_get_document_info(client, repository_name, filename)
    if document_info:
        language = document_info["language"]
        source_code = await task_retrieve_file_content(client, repository_name, filename)
        if source_code:
            await task_get_language_specific_prompt(client=client, language=language, source_code=source_code, repository_name=repository_name, filename=filename)

async def workflow_get_document_information(client: FastMCPClient, repo_name: str, filename: str):
    try:
        async with client:
            await client.ping()

            document_info = await task_get_document_info(client=client, repository=repo_name, filename=filename)
            filecontent = await task_retrieve_file_content(client=client, repository_name=repo_name, filename=filename)

            if document_info is None or filecontent is None:
                logger.warning("Agent -> Could not retrieve document info or file content.")
                return None

            # Σύνθεση του JSON αποτελέσματος
            file_text = getattr(filecontent[0], "text", None) if isinstance(filecontent, list) and filecontent else str(filecontent)

            result = dict(document_info)
            result["filecontent"] = file_text

            print("Agent -> Document Info:")
            print(json.dumps({k: v for k, v in result.items() if k != "filecontent"}, indent=2))

            print("\nFile Content:\n")
            print(result["filecontent"])  # Εδώ οι αλλαγές γραμμής αποδίδονται οπτικά
            return result

    except Exception as e:
        logger.error(f"Could not run workflow: {e}")
        return None


async def workflow_get_document_flow(client: FastMCPClient, repo_name: str, filename: str):
    try:
        async with client:
            await client.ping()

            document_info = await task_get_document_info(client=client, repository=repo_name, filename=filename)
            if not document_info:
                logger.error("Could not retrieve document info.")
                return None

            source_code = await task_retrieve_file_content(client=client, repository_name=repo_name, filename=filename)
            if not source_code:
                logger.error("Could not retrieve source code.")
                return None

            language = dict(document_info).get("language")
            if not language:
                logger.error("Language not detected in document info.")
                return None

            prompts = await task_get_language_specific_prompt(
                client=client,
                language=language,
                source_code=str(get_first_text(source_code)),
                repository_name=repo_name,
                filename=filename
            )

            json_data = await task_extract_flow_with_prompt(
                client=client,
                system_prompt=str(prompts.get("system_prompt")),
                llm_prompt=str(prompts.get("llm_prompt"))
            )

            print(json_data)
            return json_data
    except Exception as e:
        logger.error(f"Could not run workflow: {e}")
        return None


        

WORKFLOWS = [
    {
        "name": "Fetch and Classify Repository",
        "function": workflow_fetch_and_classify_repository,
        "params": ["repo_url"],
        "description": "Fetch a repository and classify it."
    },
    {
        "name": "Get Document Info",
        "function": workflow_get_document_information,
        "params": ["repo_name", "filename"],
        "description": "Get Documnet Information."
    },
    {
        "name": "Extract Document Flow",
        "function": workflow_get_document_flow,
        "params": ["repo_name", "filename"],
        "description": "Extracts the execution flow of a program, starting from its primary entry point, and returns it in a structured JSON format."
    }    
    # Add more workflows here
]

def list_workflows():
    print("Available workflows:")
    for idx, wf in enumerate(WORKFLOWS, 1):
        print(f"{idx}. {wf['name']} - {wf['description']}")


            # task_get_language_specific_prompt

