import json
from utils.mcp_tools_helper import safe_get_prompt
from utils.config import get_ollama_client, OLLAMA_MODEL
from workflows.workflows import WORKFLOWS, list_workflows
from tasks.tasks import task_get_document_info, task_retrieve_file_content

def extract_prompt_text(messages):
    texts = []
    for m in messages:
        if isinstance(m, dict):
            text = m.get('content', {}).get('text', '')
        else:
            text = getattr(getattr(m, 'content', None), 'text', '')
        if text:
            texts.append(text)
    return '\n\n'.join(texts)

def prompt_argument_input(prompt_obj):
    args = {}
    arguments = getattr(prompt_obj, 'arguments', None)
    if arguments:
        print(f"Agent -> Please provide argument values for '{prompt_obj.name}':")
        for arg in arguments:
            arg_name = getattr(arg, 'name', str(arg))
            required = getattr(arg, 'required', False)
            prompt_text = f"Enter value for {arg_name}" + (" (required): " if required else ": ")
            value = input(prompt_text)
            if required and not value:
                print(f"Agent -> {arg_name} is required.")
                break
            args[arg_name] = value
    else:
        print("Agent -> No arguments found for this prompt.")
    return args

async def prompt_action_submenu(client, prompt_obj, args, n):
    while True:
        print(f"\n=== Prompt Action Menu (Prompt {n}) ===")
        print("1. Run\n2. Show\n3. Back")
        action = input("User -> Select an option: ").strip()
        if action == "1":
            data, error = await safe_get_prompt(client, prompt_obj.name, args)
            if error:
                print(f"Agent -> Error getting prompt: {error}")
            else:
                messages = data.get('messages', []) if isinstance(data, dict) else getattr(data, 'messages', [])
                prompt_text = extract_prompt_text(messages)
                ollama_client = get_ollama_client()
                response = ollama_client.chat(
                    model=OLLAMA_MODEL,
                    messages=[{"role": "user", "content": prompt_text}],
                    options={'temperature': 0}
                )
                print(f"Agent -> LLM Response: {response['message']['content']}")
        elif action == "2":
            data, error = await safe_get_prompt(client, prompt_obj.name, args)
            if error:
                print(f"Agent -> Error getting prompt: {error}")
            else:
                messages = data.get('messages', []) if isinstance(data, dict) else getattr(data, 'messages', [])
                prompt_text = extract_prompt_text(messages)
                print(f"Agent -> Prompt text:\n{prompt_text}")
        elif action == "3":
            break
        else:
            print("Agent -> Invalid selection. Please choose 1, 2, or 3.")

async def prompts_menu(client):
    try:
        async with client:
            await client.ping()
            prompts = await client.list_prompts()
            while True:
                print('\n=== Prompts Menu ===')
                for idx, prompt in enumerate(prompts, 1):
                    print(f"{idx}. {prompt.name}: {prompt.description}")
                user_cmd = input("User -> Select a prompt by number or type 'back': ").strip().lower()
                if user_cmd == "back":
                    break
                if not user_cmd.isdigit() or int(user_cmd) < 1 or int(user_cmd) > len(prompts):
                    print("Agent -> Invalid selection. Please enter a valid prompt number or 'back'.")
                    continue
                n = int(user_cmd)
                prompt_obj = prompts[n-1]
                args = prompt_argument_input(prompt_obj)
                await prompt_action_submenu(client, prompt_obj, args, n)
    except Exception as e:
        print("Could not retrieve prompts:", e)

async def display_menu(client):
    with open("menu.json", "r", encoding="utf-8") as f:
        menu = json.load(f)
    while True:
        print("\n=== Main Menu ===")
        for key, value in menu.items():
            print(f"{key}. {value}")
        selection = input("User -> Select an option (or '4' to go back): ").strip()
        if not selection:
            continue
        if selection == "1":
            await show_tools(client)
        elif selection == "2":
            await prompts_menu(client)
        elif selection == "3":
            await run_workflow_menu(client)
        elif selection == "4":
            print("Agent -> Returning to main.")
            break
        else:
            print("Agent -> Invalid selection. Please try again.")

async def run_workflow_menu(client):
    list_workflows()
    choice = int(input("Select a workflow by number: ")) - 1
    workflow = WORKFLOWS[choice]
    params = prompt_for_parameters(workflow["params"])
    result = await workflow["function"](client, **params)



def prompt_for_parameters(params):
    values = {}
    for param in params:
        values[param] = input(f"Enter value for {param}: ")
    return values


async def show_tools(client):
    try:
        async with client:
            await client.ping()
            tools = await client.list_tools()
            print('Available tools:')
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")
    except Exception as e:
        print("Could not retrieve prompts:", e)    

async def wf_get_document_flow(client, repository_name: str, filename: str):
    document_info = await task_get_document_info(client, repository_name, filename)
    if document_info:
        language = document_info["language"]
        source_code = await task_retrieve_file_content(client, repository_name, filename)
        if source_code:
            # Combine document_info and filecontent
            result = dict(document_info)
            result["filecontent"] = source_code
            print("Agent -> Document Info with File Content:")
            print(json.dumps(result, indent=2))
            return result
    print("Agent -> Could not retrieve document info or file content.")
    return None    