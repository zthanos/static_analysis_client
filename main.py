import asyncio
import json
from utils.config import get_fastmcp_client, LLM_MODEL, get_llm_client

from menu import display_menu
from utils.prompts_utils import print_agent, input_prompt
from utils.logger import get_logger
from utils.message_history import (
    history_collector, 
    add_message_to_history
) 
from clients.ollama import stream_chat

logger = get_logger(__name__)


async def user_input_handler(ollama_client, user_input, client, chat_history):
    """
    Handles user input, dispatching it to menu actions or LLM chat.
    
    Args:
        ollama_client: Ollama client instance.
        user_input (str): User input from prompt.
        client: FastMCP client instance.
        chat_history (list): List of past conversation messages.
    """    
    if user_input.lower() == "menu":
        await display_menu(client)
    elif user_input.lower() == "quit":
        print_agent("Exiting.")
        exit(0)
    else:
        # Prepare subscribers
        subscribers = [
            lambda chunk: print_agent(chunk, True),
            history_collector(chat_history)
        ]

        # Start streaming
        chat_history = add_message_to_history(chat_history, "user", user_input)
        collect, finalize = history_collector(chat_history)

        async for chunk in stream_chat(ollama_client, LLM_MODEL, chat_history):
            print_agent(chunk, True)
            collect(chunk)
        print()

        chat_history = finalize()        

async def main():
    """
    Main event loop for the Static Analysis Client.
    Initializes clients, greets the user, and enters the input loop.
    """    
    logger.info("Starting client!")
    client = get_fastmcp_client()
    ollama_client = get_llm_client()
    chat_history = []

     # Welcome messages
    print_agent("Agent -> Welcome to the Static Analysis Client!")
    print_agent("\t Type menu for specific actions, or Quit to exit. ")
    print_agent("\t What can I do for you today?")

    # User interaction loop
    while True:
        user_input = input_prompt("", "User").strip()
        if not user_input:
            continue
        await user_input_handler(ollama_client, user_input, client, chat_history)


if __name__ == "__main__":
    asyncio.run(main())






        # data = await task_get_repository_summary(client, "DOGECICS")
        # if isinstance(data, list):
        #     for document in data:
        #         if document["analysis"]:
        #             # print(document)        
        #             msg = f"filename {document["filename"]} analysis {json.dumps(document["analysis"])} "
        #             summary = send_message_to_llm_old(get_ollama_client(), f"summarize analysis {msg}")

        #             chat_history.append( {"role": "assistant", "content": summary})
        #     # for msg in chat_history:
        #     #     print(msg)
# def send_message_to_llm(ollama_client, prompt, history):
#     ollama_client = get_ollama_client()
#     directions = "Use prompt messages as your context, the prompt contains a software system context"
#     messages = [
#             {"role": "assistant", "content": directions},
#             {"role": "assistant", "content": history},
#             {"role": "user", "content": prompt}
#     ]
#     logger.debug(messages)
#     response = ollama_client.chat(
#         model=OLLAMA_MODEL,
#         messages=messages,
#         options={'temperature': 0}
#     )
#     return response['message']['content']

# def send_message_to_llm(prompt):
#     ollama_client = get_ollama_client()
#     directions = "Use prompt messages as your context, the prompt contains a software system context"


#     chat_history.append({"role": "user", "content": prompt})


#     try:
#         response = ollama_client.chat(
#             model=OLLAMA_MODEL,
#             messages=chat_history,
#             options={'temperature': 0}
#         )
#         content = response.get('message', {}).get('content', '')
#         if not content:
#             logger.warning("LLM response is empty or missing 'message.content'")
#         return content
#     except Exception as e:
#         logger.error("Error while communicating with LLM: %s", e)
#         return ""


# async def user_input_handler(ollama_client, user_input, client):
#     if user_input.lower() == "menu":
#         await display_menu(client)
#     elif user_input.lower() == "quit":
#         print_agent("Exiting.")
#         exit(0)
#     else:
#         stream = stream_chat(ollama_client, 'mistral', chat_history, 'Hello!')
#         subscribers = [
#             lambda chunk: print_agent(chunk),
#             history_collector(chat_history)
#         ]

#         async for chunk in stream:
#             for subscriber in subscribers:
#                 subscriber(chunk)