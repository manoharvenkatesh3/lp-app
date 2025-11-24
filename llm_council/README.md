# LLM Council

The **LLM Council** is a self-contained Streamlit experience dedicated to orchestrating
multi-model deliberations powered by OpenRouter. This scaffold provides the
configuration primitives (models, retry policies, environment helpers, and
session-state utilities) required to build a richer, multi-agent council UI
without relying on the existing root Streamlit app in this repository.

## Project structure

```
llm_council/
├── .streamlit/
│   └── config.toml        # Streamlit theme + dev server defaults
├── config.py              # Centralized constants & helper utilities
├── requirements.txt       # Python dependencies for the council app
├── streamlit_app.py       # Minimal Streamlit entrypoint wired to the config
└── README.md              # You are here
```

## Prerequisites

- Python 3.10+ (3.11 recommended)
- `pip` for dependency installation
- An [OpenRouter](https://openrouter.ai/) API key with chat completion access

## Environment configuration

Set your OpenRouter API key before running the app. Two approaches are supported:

1. **Environment variable (recommended for local dev):**

   ```bash
   export OPENROUTER_API_KEY="sk-your-key"
   ```

2. **Streamlit secrets (useful for sharing workspaces):**

   Create `llm_council/.streamlit/secrets.toml` containing:

   ```toml
   OPENROUTER_API_KEY = "sk-your-key"
   ```

> `config.py` automatically checks the environment variable first and falls back
> to Streamlit secrets, raising a helpful error if neither is present when the
> app attempts to contact OpenRouter.

## Installation

```bash
cd llm_council
python -m venv .venv          # optional but encouraged
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the app

From inside the `llm_council` directory, start Streamlit:

```bash
streamlit run streamlit_app.py
```

The starter UI lists the preconfigured council participants and chairman model
so you can verify configuration and session-state persistence. Extend
`streamlit_app.py` with agent orchestration, httpx calls to OpenRouter, and any
additional visualization or coordination logic needed for your use case.

## Customization tips

- Edit `config.py` to change participant definitions, retry policies, or the
  default chairman model.
- Update `.streamlit/config.toml` to tailor theming, fonts, or server behavior.
- Add new modules within this folder to keep the council experience isolated
  from the root Streamlit implementation.
