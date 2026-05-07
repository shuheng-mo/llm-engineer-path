# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal learning repo for 莫抒衡's 大模型开发训练营 (LLM engineering bootcamp, started 2026-05-06). Source spec is `莫抒衡 - 大模型开发训练营.docx` in the repo root. The training plan has three stages; the directory layout below mirrors them 1:1.

## Layout

```text
stage1-foundations/   # 夯实基础 — Python / FastAPI / MySQL / LLM 概念 / Prompt eng
  01-python/  02-fastapi/  03-mysql/  04-llm-basics/  05-prompt-engineering/
stage2-advanced/      # 系统进阶 — LangChain → RAG → LangGraph → Capstone → Finetune → Algo
  01-langchain/  02-redis/  03-rag/  04-langgraph/  05-mcp-a2a/
  06-travel-assistant/  07-finetune/  08-algo/
stage3-interview/     # 面试冲刺
  01-qa-bank/  02-resume/  03-mock-interviews/
```

Treat each numbered topic as an independent sandbox — they don't share code. The capstone `stage2-advanced/06-travel-assistant/` (知行旅游助手) is the integration project that pulls together LangChain + RAG + LangGraph.

## Python / dependency management

**Single-rooted uv project.** One `pyproject.toml`, one `.venv/` at the repo root, one `uv.lock`. Topics are split via PEP 735 `[dependency-groups]` — don't create per-subdir venvs.

Required Python: `>=3.11,<3.13` (pinned to 3.12 via `.python-version`). The ML ecosystem is unstable on 3.13/3.14 — do not bump without checking torch/transformers wheel availability.

Index: pyproject.toml configures the Tsinghua PyPI mirror as default (CN network reliability). To use the canonical PyPI for one run: `UV_INDEX_URL=https://pypi.org/simple uv sync`.

Common commands:

```bash
uv sync                        # install default groups (everything except finetune)
uv sync --group finetune       # add the heavy ML stack when you reach stage2-advanced/07-finetune
uv sync --all-groups           # install everything including finetune
uv run python <script>         # run inside the venv without activating
uv run pytest                  # tests
uv run ruff check .            # lint
uv add <pkg> --group rag       # add a dep to a specific topic group
```

Group → topic mapping lives in `pyproject.toml`. `default-groups` under `[tool.uv]` controls what plain `uv sync` installs — `finetune` is intentionally excluded because torch + transformers + accelerate is multi-GB and irrelevant until the finetune module.

### Llama-Factory note

Llama-Factory is the framework called out in the bootcamp doc for stage 2 finetune. It pins specific versions of transformers/peft that often clash with newer releases. **Do not** add it to `[dependency-groups.finetune]` in `pyproject.toml` — install it ad-hoc with `uv pip install llamafactory` (or clone its repo) inside the synced venv at the time you start that module, after a fresh `uv sync --group finetune`.

### Hardware reality

The user is on Apple Silicon (Darwin arm64). torch will install with MPS support. `bitsandbytes`, `flash-attn`, `deepspeed` and other CUDA-only libs are deliberately not in any group — if a tutorial requires them, run on a Linux/CUDA box rather than fighting macOS.

## Working in a topic

When starting real work in a topic directory:

1. Update that directory's `README.md` with what you're building and how to run it.
2. If the topic has its own runnable entrypoint, document the `uv run ...` command in that README.
3. Update this file only if the command/conventions affect the whole repo.

## Things not to do

- Don't create per-topic `pyproject.toml` files — this is a single-root project on purpose.
- Don't pin to Python 3.13+ until torch ships stable wheels for it.
- Don't commit `.venv/`, `data/`, `models/`, or `.env` — already in `.gitignore`.
- Don't run `pip install` directly; always go through `uv add` / `uv sync` so the lockfile stays authoritative.
