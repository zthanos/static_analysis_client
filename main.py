import asyncio
import json
from ollama import Client as OllamaClient
from fastmcp import Client as FastMCPClient
# from tabulate import tabulate
from helpers.logger import get_logger

logger = get_logger(__name__)

def init_server():
    #HTTP Server
    return FastMCPClient("http://localhost:9000/sse", sampling_handler=sampling_handler)

ollama_client = OllamaClient(host='http://localhost:11434')
# ollama_model = "deepseek-coder:latest"
ollama_model = "deepseek-coder-v2:latest"

async def sampling_handler(
    messages: list,
    params,
    context,
) -> str:
    
    prompt = ""
    
    if params.systemPrompt:
        prompt += f"{params.systemPrompt}\n\n"
    
    for m in messages:
        prompt += f"{m.role}: {m.content.text}\n"
    
    prompt += "\nReturn your answer as a JSON object."

    response = ollama_client.chat(
        model=ollama_model,
        messages=[{"role": "user", "content": prompt}],
        options={'temperature': 0}
    )

    return response['message']['content']


def send_message_to_llm(ollama_client, prompt):
    response = ollama_client.chat(
        model=ollama_model,
        messages=[{"role": "user", "content": prompt}],
        options={'temperature': 0}
    )
    return response['message']['content']
# client = Client(server)


# client = Client("main.py")


    # print(clasify_repo)

    # print(response)

    # print(f"Repository: {repository_name}")
    # await task_return_workspace(client, "DOGECICS", "DOGESEND")

# async def br_workflow(client: FastMCPClient):
#     repository_name = await task_fetch_repository(client, "https://github.com/zthanos/RuleEngine.git")
#     clasify_repo = await task_classify_repository(client, repository_name)
#     logger.info(clasify_repo)
#     await task_return_workspace(client, "RuleEngine", "RuleAction.cs")
#     files_in_repository = await task_processed_repository(client, repository_name)
#     logger.info("Task 1: files_in_repository completed")
#     source_code_file = "RuleAction.cs"
#     document_info = await task_get_document_info(client, repository_name, source_code_file)
#     logger.info(f"Document info: {document_info}")
#     di = json.loads(document_info)
#     language = di["language"]
#     logger.info(f"Language: {language}")
#     source_code = await task_retrieve_file_content(client, repository_name, source_code_file)
#     if source_code:
#     # print(f"Source code: {source_code}")
#         await task_get_language_specific_prompt(client=client, language=language, source_code=source_code, repository_name=repository_name, filename=source_code_file)


# async def workflow(client: FastMCPClient):
#     repository_name = await task_fetch_repository(client, "https://github.com/mainframed/DOGECICS.git")
#     # clasify_repo = await task_classify_repository(client, repository_name)
#     # print(clasify_repo)

#     logger.info(f"Repository: {repository_name}")
#     await task_return_workspace(client, "DOGECICS", "DOGESEND")

#     # repository_name = "DOGECICS"
#     files_in_repository = await task_processed_repository(client, repository_name)
#     logger.info("Task 1: files_in_repository completed")
#     # maps_data = await task_get_map_files(client, repository_name)
#     logger.info("Task 2: maps_data completed")
#     source_code_files = ["DOGESEND", "DOGEMAIN", "DOGETRAN", "dogedcams.py", "KICKS"]
#     # for source_code_file in source_code_files:

#     #     document_info = await task_get_document_info(client, repository_name, source_code_file)
#     #     language = document_info.language
#     #     print(document_info)
#     #     source_code = await task_retrieve_file_content(client, repository_name, source_code_file)
#     #     await task_get_language_specific_prompt(client=client, language=language, source_code=source_code[0].text, repository_name=repository_name, filename=source_code_file)

#         # print(f"Task 3: File info completed, {source_code_file}")
#         # edges = await task_extract_flow(client=client, repository_name=repository_name, filename=source_code_file)      
#         # print(f"Task 3: File info completed, {edges}")

#     # for source_code_file in source_code_files:
#     #     edges = await task_extract_edges(client, repository_name, source_code_file)
#     #     print(f"Task 3: edges completed, {source_code_file}")

#     # print(edges)
#     # flow = await client.call_tool("extract_edges", {"repository": repository_name, "filename": source_code_file})
#     # print(flow)


  

async def main():
    logger.info("Starting client!")
    client = init_server()
    async with client:
        await client.ping()
        tools = await client.list_tools()
        logger.info('Available tools:')
        for tool in tools:
            logger.info(f'\t {tool.name} -> {tool.description}')

        # await task_classify_document(client, "DOGECICS", "DOGESEND")
        # await task_classify_document(client, "DOGECICS", "DOGEMAIN")
        # await task_classify_document(client, "DOGECICS", "DOGETRAN")
        # await task_extract_flow(client, "DOGECICS", "dogedcams.py")

        # repository_name = "DOGECICS"
        # source_code_files = ["DOGEQUIT", "DOGEDEET"] #, "dogedcams.py", "KICKS", "DOGESEND", "DOGEMAIN", "DOGETRAN", ]
        # for source_code_file in source_code_files:
        #     document_info = await task_get_document_info(client, repository_name, source_code_file)
        #     logger.info(f"Document info: {document_info}")
        #     di = json.loads(document_info)
        #     language = di["language"]
        #     logger.info(f"Language: {language}")
        #     source_code = await task_retrieve_file_content(client, repository_name, source_code_file)
        #     if source_code:
        #         # print(f"Source code: {source_code}")
        #         await task_get_language_specific_prompt(client=client, language=language, source_code=source_code, repository_name=repository_name, filename=source_code_file)


        # await task_extract_flow(client, "DOGECICS", "KICKS")

        # await workflow(client)

if __name__ == "__main__":
    asyncio.run(main())