import asyncio
import json
from utils.config import get_fastmcp_client, OLLAMA_MODEL, get_ollama_client
# from utils.logger import get_logger

from utils.mcp_tools_helper import safe_get_prompt
from menu import display_menu, prompts_menu, prompt_argument_input, prompt_action_submenu, extract_prompt_text



def send_message_to_llm(ollama_client, prompt):
    ollama_client = get_ollama_client()
    response = ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={'temperature': 0}
    )
    return response['message']['content']




async def user_input_handler(user_input, client):
    if user_input.lower() == "menu":
        await display_menu(client)
    elif user_input.lower() == "quit":
        print("Agent -> Exiting.")
        exit(0)
    else:
        llm_response = send_message_to_llm(client, user_input)
        print(f"Agent -> {llm_response}")

async def main():
    print("Agent -> Welcome to the Static Analysis Client!")
    print("\t Type menu for specific actions, or Quit to exit. ")
    print("\t What can I do for you today?")
    # logger.info("Starting client!")
    client = get_fastmcp_client()
    while True:
        user_input = input("User -> ").strip()
        if not user_input:
            continue
        await user_input_handler(user_input, client)

if __name__ == "__main__":
    asyncio.run(main())