# Godot Agent

Godot Agent is a local-first AI development assistant for **Godot 4** built with **Python 3.14** and **Ollama**.

The project is intentionally lightweight. Instead of relying on a large agent framework, it currently uses explicit Python abstractions for the LLM provider, tool selection, official Godot documentation retrieval, lexical documentation search, conversation history, and error handling.

The current command-line application uses the local Ollama model `gemma4` and is designed so the LLM provider can be replaced later without rewriting the core agent.

## Current Status

The current implementation includes the completed foundation from Phases 1 and 2 and early groundwork for working with local Godot projects.

Currently implemented:

- Python 3.14 project
- Local Ollama integration
- Swappable `LLMProvider` abstraction
- Conversation history
- External system and tool-selection prompts
- Structured JSON tool selection
- Official Godot 4 documentation retrieval
- Single- and multi-class documentation requests
- Lightweight lexical retrieval over documentation text
- Graceful Godot documentation failure handling
- Graceful invalid tool-selection handling
- Local Godot project file listing, reading, and searching
- Path traversal protection for project file reads
- Pytest test suite
- GitHub Actions test workflow for pull requests

> **Note:** `GodotProjectTool` is implemented and tested, but it is not yet connected to `GodotAgent`. The active agent tool flow currently supports `godot_docs` only.

## How It Works

At a high level, a user question follows this flow:

```text
User question
    |
    v
GodotAgent.ask()
    |
    +--> Store question in conversation history
    |
    v
Tool-selection LLM call
    |
    +--> No documentation needed / invalid request
    |       |
    |       v
    |   Normal LLM response
    |
    +--> godot_docs requested
            |
            v
       One or more Godot classes
            |
            v
       Fetch official Godot documentation
            |
            v
       Search documentation for relevant chunks
            |
            v
       Add successful documentation results
       as temporary system context
            |
            v
       Final LLM response
            |
            v
       Store response in conversation history
```

Tool selection and final answer generation are separate LLM calls when documentation is requested.

## Architecture

### `GodotAgent`

`agent/godot_agent.py` contains the main orchestration logic.

The agent:

1. Stores conversation history.
2. Sends the conversation to a dedicated tool-selection prompt.
3. Parses the model's structured tool request.
4. Executes requested Godot documentation searches.
5. Combines successful results from multiple Godot classes.
6. Injects retrieved documentation into the final answer context.
7. Calls the LLM again to produce the user-facing answer.
8. Stores the final response in conversation history.

The agent depends on the `LLMProvider` interface rather than Ollama directly.

### Provider Abstraction

`providers/base.py` defines the provider contract:

```python
class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[Message]) -> str:
        ...
```

`providers/ollama_provider.py` provides the current implementation using Ollama.

This boundary is intended to make it possible to add another provider later without coupling `GodotAgent` to a specific LLM service.

### Tool Selection

`agent/tool_router.py` defines a `ToolRequest` containing:

```python
@dataclass
class ToolRequest:
    tool: str
    class_names: list[str]
```

The tool-selection model can request multiple Godot classes in one request:

```json
{
  "tool": "godot_docs",
  "class_names": ["Area2D", "Timer"]
}
```

If no documentation is needed, the expected request is:

```json
{
  "tool": "none"
}
```

Malformed JSON, missing tools, or an invalid `class_names` type are treated as an unusable tool request rather than crashing the agent.

### Official Godot Documentation

`tools/godot_docs.py` contains `GodotDocsClient`.

It retrieves documentation from the stable Godot documentation site and converts the HTML documentation body into plain text.

Godot classes are resolved to class documentation pages using a normalized class name. For example:

```text
Timer
    -> timer
    -> classes/class_timer.html
```

The client attempts several selectors when locating the main documentation content:

- `div[itemprop="articleBody"]`
- `.document`
- `[role="main"]`

### `GodotDocsError`

Documentation failures are normalized through `GodotDocsError`.

The client raises this exception when:

- an HTTP request fails,
- a network request fails, or
- expected documentation content cannot be found in the returned page.

The agent catches `GodotDocsError` while processing individual classes. A failed class does not prevent other requested classes from being used.

For example, if the model requests:

```text
Area2D
PlayerController
Timer
```

and `PlayerController` cannot be retrieved, successful `Area2D` and `Timer` documentation can still be passed to the final LLM call.

If every documentation lookup fails, the agent continues without documentation context.

### Documentation Retrieval

`tools/godot_docs_tool.py` wraps the documentation client and the text retriever.

It currently supports:

```python
get_class_docs(class_name)
```

for retrieving and truncating raw class documentation, and:

```python
search_class_docs(class_name, query)
```

for retrieving only chunks relevant to the user's question.

### Lightweight Text Retrieval

`tools/text_retriever.py` implements a small local lexical retriever without a vector database or embedding model.

It:

1. Splits documentation into chunks.
2. Tokenizes the user's query and each chunk.
3. Removes common stop words.
4. Scores chunks by matching query terms.
5. Gives additional weight to matching underscore-containing API-style terms.
6. Returns the highest-scoring chunks.

The default documentation search returns up to five relevant chunks.

This keeps the current retrieval system local and easy to understand while avoiding premature vector-database complexity.

## Multi-Class Documentation

The active documentation tool supports multiple Godot classes in one request.

For a question such as:

```text
How do I start a Timer when the player enters an Area2D?
```

the tool selector can request:

```json
{
  "tool": "godot_docs",
  "class_names": ["Area2D", "Timer"]
}
```

`GodotAgent._execute_tool()` searches each class independently and combines successful results into one context block.

Each result is labeled with its class name and separated before being supplied to the final LLM call.

## Failure Handling

The current agent is designed to degrade gracefully when optional documentation retrieval fails.

### Invalid tool-selection response

If the LLM returns invalid JSON, tool parsing returns `None`. The agent then continues to the normal answer call without documentation.

### Documentation request failure

If a class lookup raises `GodotDocsError`, that class is skipped.

### Partial multi-class failure

If some requested classes succeed and others fail, the successful documentation is still used.

### Empty search results

If documentation retrieval succeeds but the lexical search returns no relevant text, no empty documentation context is injected.

### Complete documentation failure

If no requested class produces usable documentation, the agent still performs the final LLM call using its normal conversation context.

## Conversation Memory

`GodotAgent` maintains in-memory conversation history using a list of `Message` dictionaries:

```python
{
    "role": "user",
    "content": "How does a Timer work?"
}
```

The history includes:

- the main system prompt,
- user messages, and
- assistant responses.

The tool-selection step also receives previous conversation turns, allowing follow-up questions such as:

```text
How does a Timer work?
```

followed by:

```text
What signal does it emit?
```

to be interpreted using the existing conversation.

Retrieved documentation is temporary answer context and is not permanently appended to the conversation history.

## Godot Project Tool

`tools/godot_project_tool.py` contains the initial local-project inspection capability.

A `GodotProjectTool` is initialized with a project root and verifies that the directory contains `project.godot`.

It currently supports:

### List project files

```python
files = tool.list_files()
```

### Read a project file

```python
content = tool.read_file("scripts/player.gd")
```

File reads are restricted to paths inside the configured Godot project root.

### Search project files

```python
matches = tool.search_files("CharacterBody2D")
```

Search is case-insensitive and currently defaults to these file types:

```text
.gd
.tscn
.godot
```

The project tool is currently standalone. It has tests, but the agent does not yet select or execute it.

## Project Structure

```text
godot-agent/
├── .github/
│   └── workflows/
│       └── pytest.yml
├── agent/
│   ├── __init__.py
│   ├── godot_agent.py
│   └── tool_router.py
├── config/
│   └── settings.py
├── prompts/
│   ├── system_prompt.txt
│   └── tool_selection.txt
├── providers/
│   ├── __init__.py
│   ├── base.py
│   └── ollama_provider.py
├── tests/
│   ├── test_agent.py
│   ├── test_godot_agent_tools.py
│   ├── test_godot_docs.py
│   ├── test_godot_docs_tool.py
│   ├── test_godot_project_tool.py
│   ├── test_text_retriever.py
│   └── test_tool_router.py
├── tools/
│   ├── __init__.py
│   ├── godot_docs.py
│   ├── godot_docs_tool.py
│   ├── godot_project_tool.py
│   └── text_retriever.py
├── .gitignore
├── main.py
└── pyproject.toml
```

## Requirements

The project currently requires:

- Python 3.14 or newer
- Ollama
- A locally available Ollama model
- Internet access when official Godot documentation needs to be retrieved

Python dependencies declared in `pyproject.toml` are:

- `ollama`
- `httpx`
- `beautifulsoup4`

Development dependencies include:

- `pytest`

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd godot-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install the project

For development:

```bash
pip install -e ".[dev]"
```

### 4. Install and start Ollama

Install Ollama separately and make sure its local service is available.

The CLI currently uses:

```python
MODEL = "gemma4"
```

Make sure that model is available locally before running the agent.

## Running the Agent

From the project root:

```bash
python main.py
```

The CLI starts an interactive loop:

```text
Godot Agent (gemma4)
Type 'exit' or 'quit' to stop.

You > How do I know when a Timer finishes?
```

Enter either `exit` or `quit` to stop the program.

## Running Tests

Run the full test suite with:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

At the time of this README snapshot, the repository contains **25 passing tests**.

The tests cover areas including:

- basic agent responses,
- conversation history,
- tool-request parsing,
- single-class documentation use,
- multi-class documentation use,
- documentation HTTP and network failures,
- missing documentation content,
- partial documentation failures,
- invalid tool-selection responses,
- empty documentation searches,
- tool selection using conversation history,
- raw documentation retrieval,
- documentation truncation,
- lexical retrieval,
- Godot project file listing,
- Godot project file reading,
- project path traversal protection, and
- Godot project text searching.

## Continuous Integration

The repository includes a GitHub Actions workflow at:

```text
.github/workflows/pytest.yml
```

It runs the test suite for pull requests targeting `main` using a Python 3.14 development build.

