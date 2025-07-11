# 🛠️ Static Analysis Client

A CLI client to interact with the **FastMCP server** and **Ollama LLM**, providing static analysis, prompt execution, and workflow automation.

## ✨ Features

* List available tools, prompts, and workflows from the MCP server.
* Run LLM prompts (with or without chat history).
* Stream LLM responses and collect them in real time.
* Modular architecture with clean separation of history, config, and handlers.
* Async event loop for responsive CLI interaction.
* Configurable backends (FastMCP, Ollama).

## ⚙️ Configuration

Edit `utils/config.py` to set:

* `OLLAMA_HOST`: Ollama server (default `http://localhost:11434`)
* `LLM_MODEL`: model name (e.g., `deepseek-coder-v2:latest` or `mistral:latest`)
* `FASTMCP_URL`: FastMCP server URL (default `http://localhost:9000/sse`)

## 🚀 Installation & Run

### Install with `uv` (recommended)

```bash
uv venv .venv
uv pip install -r requirements.txt
```

### Run the client

```bash
uv run python main.py
```

### Alternative with plain Python

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 📋 Available Commands

Inside the CLI, you can:

* Type `menu` → to open the main menu:

  * `1`: List Available Tools
  * `2`: List Available Prompts
  * `3`: List Available Workflows
  * `4`: Exit to main prompt

* Type any **free text** → to send directly to the LLM (with streaming response).

* Type `quit` → to exit the application.

## 🏗️ Workflows

Workflows are predefined sequences combining tools and tasks, e.g.:

* **Fetch and Classify Repository**
* **Get Document Info**
* **Extract Document Flow**

They are defined in `workflows/workflows.py` and listed dynamically inside the CLI.

## 🔌 Extending

* To add a **new tool integration**, update `tasks/tasks.py`.
* To add a **new workflow**, add it in `workflows/workflows.py` and register it in the `WORKFLOWS` list.
* To add a **new menu item**, edit `menu.json`.

## 💬 Contact

For questions or improvements, feel free to suggest via issues or PR!



# ✅ Προτεινόμενα ερωτήματα που μπορούν να απαντηθούν σωστά

Μπορείς να κάνεις ερωτήσεις όπως:

## 💥 Για το συνολικό σύστημα:

- What systems are involved in the solution?

- What are the main external systems or services integrated?

- What are the critical paths in the overall system?

- What external databases or files does the system use?

## 💥 Για συγκεκριμένα προγράμματα:

- What is the execution flow of DOGEMAIN?

- What external interactions are used by DOGESEND?

- Does DOGEQUIT interact with external systems?

- Which programs interact with CICS?

- Which scripts use the VSAM files?

## 💥 Για dependencies & architecture:

- Which components depend on KICKS framework?

- Which programs are linked together in the compile_cobol.jcl job?

- What Python components are involved, and what is their role?

- What is the purpose of dogedcams.py, and how does it interact with the system?

## 💥 Για τεχνικές λεπτομέρειες:

- Which programs handle user input?

- How are random numbers generated in the system?

- How is the printer integration implemented?

- What are the COBOL programs compiled for the Dogecoin application?