demo_agent
==========

Hands-on playground for building an autonomous chat agent that talks to local LLMs via the `lmstudio` Python SDK. The agent stitches together prompting, tool use, retrieval-augmented memory, and long-term recollection to mimic a production-quality workflow while remaining hackable.

Features
--------
- Interactive CLI loop driven by `demo_agent.agent.runtime.Runner`, streaming responses from an LM Studio-served model (default: `openai/gpt-oss-20b`).
- Policy layer (`demo_agent.agent.policy.DefaultPolicy`) that formats Harmony-style prompts, decides when to surface tools, and persists conversation history.
- Vector-based memory (`demo_agent.agent.memory.Memory`) backed by FAISS with auto-summarisation and durable storage under `data/pernanent_memory/`.
- Tool registry (`demo_agent.tools.utils.Tools`) with JSON argument validation; ships with a sandboxed `math_tool` and a stub for future browsing integrations.
- Retrieval helpers in `demo_agent.retriever.*` combining MarkItDown loaders, configurable text chunking, and embedding generation (`text-embedding-embeddinggemma-300m-qat`).

Getting Started
---------------
1. **Prerequisites**
   - Python 3.10 or newer.
   - [LM Studio](https://lmstudio.ai/) desktop app with the desired model downloaded.
   - Python packages: `lmstudio`, `markitdown`, `faiss-cpu`, `numpy`. Install them alongside standard tooling (`pytest`, etc.).

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the project in editable mode**
   ```bash
   pip install -e .
   ```

Running the Agent
-----------------
Start LM Studio and ensure the target model is available, then launch the conversational loop:

```bash
python -m demo_agent.agent.runtime
```

Type messages at the `>>` prompt. The agent will:
- build a Harmony-formatted prompt (system instructions, optional tool manifest, retrieved memories, and recent chats);
- stream the model’s reply;
- persist chat snippets to short-term history and (when enabled) long-term memory files such as `data/pernanent_memory/default.memory.json`.

Tools & Extensions
------------------
- **Math tool** (`math_tool`): evaluates Python expressions via `demo_agent.tools.math.math_func`.
- **Browse tool stub** (`browse_tool`): placeholder sharing the same signature; replace `func` with a real implementation to enable web search.
- Add new tools by extending the dictionary in `demo_agent.tools.utils.Tools` and documenting the `description` and JSON-compatible `arguments`.
- Adjust prompting, retry behaviour, or memory settings inside `demo_agent.agent.policy.DefaultPolicy`.

Retrieval & Memory
------------------
- Documents can be ingested with `demo_agent.retriever.loader.Loader` (MarkItDown) and chunked by `demo_agent.retriever.textsplit.Cutter`.
- Embeddings are produced through LM Studio (`demo_agent.retriever.embedder.Embedder`) and stored in a FAISS index (`demo_agent.retriever.vectorstore.VectorStore`).
- Long-term memories are generated automatically when chat history exceeds the configured window, using `MemorizePolicy` to request JSON summaries from the model.

Testing
-------
Install `pytest` and run the suite from the repository root:

```bash
pytest
```

Project Resources
-----------------
- `src/demo_agent/AGENTS.md` documents the intended module layout, dev workflow, and coding guidelines.
- `configs/`, `data/`, `notebooks/`, and `scripts/` contain sample assets you can adapt while experimenting with new agents or evaluation tasks.
