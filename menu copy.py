import json
from utils.mcp_tools_helper import safe_get_prompt
from utils.config import get_llm_client, LLM_MODEL
from workflows.workflows import WORKFLOWS, list_workflows
from tasks.tasks import task_get_document_info, task_retrieve_file_content
from utils.prompts_utils import print_agent, print_menu, input_prompt

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
        print_agent(f" Please provide argument values for '{prompt_obj.name}':")
        for arg in arguments:
            arg_name = getattr(arg, 'name', str(arg))
            required = getattr(arg, 'required', False)
            prompt_text = f"Enter value for {arg_name}" + (" (required): " if required else ": ")
            value = input_prompt(prompt_text)
            if required and not value:
                print(f" {arg_name} is required.")
                break
            args[arg_name] = value
    else:
        print_agent(" No arguments found for this prompt.")
    return args

async def prompt_action_submenu(client, prompt_obj, args, n):
    while True:
        print_menu(f"\n=== Prompt Action Menu (Prompt {n}) ===")
        print_menu("1. Run\n2. Show\n3. Back")
        action = input_prompt("User -> Select an option: ").strip()
        if action == "1":
            data, error = await safe_get_prompt(client, prompt_obj.name, args)
            if error:
                print_agent(f" Error getting prompt: {error}")
            else:
                messages = data.get('messages', []) if isinstance(data, dict) else getattr(data, 'messages', [])
                prompt_text = extract_prompt_text(messages)
                ollama_client = get_llm_client()
                response = ollama_client.chat(
                    model=LLM_MODEL,
                    messages=[{"role": "user", "content": prompt_text}],
                    options={'temperature': 0}
                )
                print_agent(f" LLM Response: {response['message']['content']}")
        elif action == "2":
            data, error = await safe_get_prompt(client, prompt_obj.name, args)
            if error:
                print_agent(f" Error getting prompt: {error}")
            else:
                messages = data.get('messages', []) if isinstance(data, dict) else getattr(data, 'messages', [])
                prompt_text = extract_prompt_text(messages)
                print_agent(f" Prompt text:\n{prompt_text}")
        elif action == "3":
            break
        else:
            print_agent(" Invalid selection. Please choose 1, 2, or 3.")

async def prompts_menu(client):
    try:
        async with client:
            await client.ping()
            prompts = await client.list_prompts()
            while True:
                print_menu('\n=== Prompts Menu ===')
                for idx, prompt in enumerate(prompts, 1):
                    print_menu(f"{idx}. {prompt.name}: {prompt.description}")
                user_cmd = input_prompt("User -> Select a prompt by number or type 'back': ").strip().lower()
                if user_cmd == "back":
                    break
                if not user_cmd.isdigit() or int(user_cmd) < 1 or int(user_cmd) > len(prompts):
                    print_agent(" Invalid selection. Please enter a valid prompt number or 'back'.")
                    continue
                n = int(user_cmd)
                prompt_obj = prompts[n-1]
                args = prompt_argument_input(prompt_obj)
                await prompt_action_submenu(client, prompt_obj, args, n)
    except Exception as e:
        print_agent(f"Could not retrieve prompts:\n{e}")

async def display_menu(client):
    with open("menu.json", "r", encoding="utf-8") as f:
        menu = json.load(f)
    while True:
        print_menu("\n=== Main Menu ===")
        for key, value in menu.items():
            print_menu(f"{key}. {value}")
        selection = input_prompt("Select an option (or '4' to go back): ")
        if not selection:
            continue
        if selection == "1":
            await show_tools(client)
        elif selection == "2":
            await prompts_menu(client)
        elif selection == "3":
            await run_workflow_menu(client)
        elif selection == "4":
            print_agent(" Returning to main.")
            break
        else:
            print_agent(" Invalid selection. Please try again.")

async def run_workflow_menu(client):
    list_workflows()
    choice = int(input_prompt("Select a workflow by number: ")) - 1
    workflow = WORKFLOWS[choice]
    params = prompt_for_parameters(workflow["params"])
    result = await workflow["function"](client, **params)



def prompt_for_parameters(params):
    values = {}
    for param in params:
        values[param] = input_prompt(f"Enter value for {param}: ")
    return values


async def show_tools(client):
    try:
        async with client:
            await client.ping()
            tools = await client.list_tools()
            while True:
                print_menu('\n=== Available Tools ===')
                for idx, tool in enumerate(tools, 1):
                    print_menu(f"{idx}. {tool.name}: {tool.description}")
                print_menu("b. Back")
                selection = input_prompt("Select a tool by number or 'b' to go back: ").strip().lower()
                if selection == 'b':
                    break
                if not selection.isdigit() or int(selection) < 1 or int(selection) > len(tools):
                    print_agent(" Invalid selection. Please enter a valid tool number or 'b'.")
                    continue
                tool = tools[int(selection) - 1]
                # Parse inputSchema for arguments
                args = {}
                input_schema = getattr(tool, 'inputSchema', None)
                if input_schema and 'properties' in input_schema:
                    properties = input_schema['properties']
                    required = input_schema.get('required', [])
                    for arg_name, arg_info in properties.items():
                        is_required = arg_name in required
                        prompt_text = f"Enter value for {arg_name}" + (" (required): " if is_required else ": ")
                        value = input_prompt(prompt_text)
                        if is_required and not value:
                            print(f" {arg_name} is required.")
                            break
                        args[arg_name] = value
                try:
                    data = await client.call_tool(tool.name, args)
                    error = None
                    for t in data:
                        print_agent(f" Tool result: {t.text}")
                except Exception as e:
                    print_agent(f" Exception running tool: {e}")
    except Exception as e:
        print("Could not retrieve tools:", e)

async def wf_get_document_flow(client, repository_name: str, filename: str):
    document_info = await task_get_document_info(client, repository_name, filename)
    if document_info:
        language = document_info["language"]
        source_code = await task_retrieve_file_content(client, repository_name, filename)
        if source_code:
            # Combine document_info and filecontent
            result = dict(document_info)
            result["filecontent"] = source_code
            print_agent(" Document Info with File Content:")
            print(json.dumps(result, indent=2))
            return result
    print_agent(" Could not retrieve document info or file content.")
    return None    