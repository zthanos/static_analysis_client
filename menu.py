import json
from utils.mcp_tools_helper import safe_get_prompt
from utils.config import get_llm_client, LLM_MODEL
from workflows.workflows import WORKFLOWS, list_workflows
from tasks.tasks import task_get_document_info, task_retrieve_file_content
from utils.prompts_utils import print_agent, print_menu, input_prompt
from clients.ollama import chat as ollama_chat

def extract_prompt_text(messages):
    """
    Extracts plain text from a list of message objects (dict or object with 'content.text').

    Args:
        messages (list): List of messages, each either a dict or an object with 'content.text'.

    Returns:
        str: Combined text from all messages, separated by two newlines.
    """
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
    """
    Collects user input for prompt arguments.

    Args:
        prompt_obj: The prompt object with an 'arguments' attribute.

    Returns:
        dict or None: Dictionary of argument values, or None if required arg was missing.
    """
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
                print_agent(f" {arg_name} is required.")
                return None
            args[arg_name] = value
    return args

async def prompt_action_submenu(client, prompt_obj, n):
    """
    Handles submenu actions for a selected prompt (show/run/back).

    Args:
        client: The MCP client.
        prompt_obj: Selected prompt object.
        n (int): Prompt index.
    """
    ollama_client = get_llm_client()
    while True:
        print_menu(f"\n=== Prompt {n}: {prompt_obj.name} ===")
        print_menu("1. Show prompt text")
        print_menu("2. Run prompt with LLM")
        print_menu("b. Back")
        action = input_prompt("Select an action: ").strip().lower()

        if action == "b":
            break
        elif action in ["1", "2"]:
            args = prompt_argument_input(prompt_obj)
            if args is None:
                continue

            data, error = await safe_get_prompt(client, prompt_obj.name, args)
            if error:
                print_agent(f" Error getting prompt: {error}")
                continue

            messages = data.get('messages', []) if isinstance(data, dict) else getattr(data, 'messages', [])
            prompt_text = extract_prompt_text(messages)

            if action == "1":
                print_agent(f" Prompt text:\n{prompt_text}")
            elif action == "2":
                response = ollama_chat(ollama_client, LLM_MODEL, prompt_text)
                print_agent(f" LLM Response: {response}")
        else:
            print_agent(" Invalid selection. Please choose 1, 2, or b.")

async def prompts_menu(client):
    """
    Displays the prompts menu, allowing user to select and run prompts.

    Args:
        client: The MCP client.
    """
    try:
        async with client:
            await client.ping()
            prompts = await client.list_prompts()
            while True:
                print_menu('\n=== Prompts Menu ===')
                for idx, prompt in enumerate(prompts, 1):
                    print_menu(f"{idx}. {prompt.name}: {prompt.description}")
                user_cmd = input_prompt("Select a prompt number or 'b' to go back: ").strip().lower()
                if user_cmd == "b":
                    break
                if not user_cmd.isdigit() or int(user_cmd) < 1 or int(user_cmd) > len(prompts):
                    print_agent(" Invalid selection. Please enter a valid number or 'b'.")
                    continue
                n = int(user_cmd)
                prompt_obj = prompts[n - 1]
                await prompt_action_submenu(client, prompt_obj, n)
    except Exception as e:
        print_agent(f"Could not retrieve prompts:\n{e}")

async def display_menu(client):
    """
    Main menu loop. Loads options from menu.json and routes to submenu handlers.

    Args:
        client: The MCP client.
    """
    with open("menu.json", "r", encoding="utf-8") as f:
        menu = json.load(f)
    while True:
        print_menu("\n=== Main Menu ===")
        for key, value in menu.items():
            print_menu(f"{key}. {value}")
        selection = input_prompt("Select an option or 'b' to go back: ").strip().lower()
        if selection == "b" or selection == "4":
            print_agent(" Returning to main.")
            break
        elif selection == "1":
            await show_tools(client)
        elif selection == "2":
            await prompts_menu(client)
        elif selection == "3":
            await run_workflow_menu(client)
        else:
            print_agent(" Invalid selection. Please try again.")

async def run_workflow_menu(client):
    """
    Lists and executes available workflows.

    Args:
        client: The MCP client.
    """
    list_workflows()
    selection = input_prompt("Select a workflow number or 'b' to go back: ").strip().lower()
    if selection == "b":
        return
    if not selection.isdigit() or int(selection) < 1 or int(selection) > len(WORKFLOWS):
        print_agent(" Invalid selection.")
        return
    workflow = WORKFLOWS[int(selection) - 1]
    params = prompt_for_parameters(workflow["params"])
    result = await workflow["function"](client, **params)

def prompt_for_parameters(params):
    """
    Collects user input for workflow parameters.

    Args:
        params (list): List of parameter names.

    Returns:
        dict: Parameter values keyed by name.
    """
    values = {}
    for param in params:
        values[param] = input_prompt(f"Enter value for {param}: ")
    return values

async def show_tools(client):
    """
    Lists available MCP tools and runs selected tool with optional arguments.

    Args:
        client: The MCP client.
    """
    try:
        async with client:
            await client.ping()
            tools = await client.list_tools()
            while True:
                print_menu('\n=== Available Tools ===')
                for idx, tool in enumerate(tools, 1):
                    print_menu(f"{idx}. {tool.name}: {tool.description}")
                selection = input_prompt("Select a tool number or 'b' to go back: ").strip().lower()
                if selection == 'b':
                    break
                if not selection.isdigit() or int(selection) < 1 or int(selection) > len(tools):
                    print_agent(" Invalid selection.")
                    continue
                tool = tools[int(selection) - 1]
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
                    for t in data:
                        print_agent(f" Tool result: {t.text}")
                except Exception as e:
                    print_agent(f" Exception running tool: {e}")
    except Exception as e:
        print_agent(f"Could not retrieve tools:\n{e}")

async def wf_get_document_flow(client, repository_name: str, filename: str):
    """
    Workflow function to retrieve document info and file content.

    Args:
        client: The MCP client.
        repository_name (str): Repository name.
        filename (str): Filename to fetch.

    Returns:
        dict or None: Combined document info and file content, or None on failure.
    """
    document_info = await task_get_document_info(client, repository_name, filename)
    if document_info:
        language = document_info["language"]
        source_code = await task_retrieve_file_content(client, repository_name, filename)
        if source_code:
            result = dict(document_info)
            result["filecontent"] = source_code
            print_agent(" Document Info with File Content:")
            print(json.dumps(result, indent=2))
            return result
    print_agent(" Could not retrieve document info or file content.")
    return None
