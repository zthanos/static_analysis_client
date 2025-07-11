import colorama
colorama.init()

# Χρωματιστές Σταθερές ANSI
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

def print_agent(message: str, chunk = False):
    if chunk:
        print(f"{message}", end='', flush=True)
    else :
        print(f"{GREEN}[Agent]{RESET} {message}")

def print_user(message: str):
    print(f"{BLUE}[User]{RESET} {message}")

def print_menu(message: str):
    print(f"{YELLOW}[Menu]{RESET} {message}")

def print_llm_response(message: str):
    print(f"{MAGENTA}[LLM]{RESET} {message}")

def print_prompt_colored(system_prompt: str, llm_prompt: str):
    """Εκτυπώνει το system_prompt και το llm_prompt με χρώματα στο console."""
    print(f"{GREEN}System Prompt:{RESET}\n{system_prompt}\n")
    print(f"{CYAN}LLM Prompt:{RESET}\n{llm_prompt}\n")

def input_prompt(message, actor="Agent"):
    return input(f"{GREEN}[{actor}]{RESET}{message} ").strip()
