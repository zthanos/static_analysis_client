from fastmcp import Client as FastMCPClient
from tasks.tasks import (
    task_fetch_repository,
    task_classify_repository,
    task_processed_repository,
    task_get_document_info,
    task_retrieve_file_content,
    task_get_language_specific_prompt
)
from utils.logger import get_logger

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

WORKFLOWS = [
    {
        "name": "Fetch and Classify Repository",
        "function": workflow_fetch_and_classify_repository,
        "params": ["repo_url"],
        "description": "Fetch a repository and classify it."
    },
    {
        "name": "List Files in Repository",
        "function": workflow_fetch_classify_and_list_files,
        "params": ["repo_url"],
        "description": "List all files in a repository."
    },
    # Add more workflows here
]

def list_workflows():
    print("Available workflows:")
    for idx, wf in enumerate(WORKFLOWS, 1):
        print(f"{idx}. {wf['name']} - {wf['description']}")


            # task_get_language_specific_prompt

