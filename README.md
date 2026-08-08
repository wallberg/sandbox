# Fun with Programming

My playground for programming with Python 3.

## Python Environment

Set up the local Python environment:

```bash
# Get the project
git clone git@github.com:wallberg/sandbox.git
cd sandbox

# Install uv (one-time, if not already installed)
# macOS:
brew install uv
# Linux / CI / non-Homebrew:
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up virtual environment and install dependencies
# (uv auto-installs Python 3.11 if not already present)
uv sync

# Activate (optional — scripts in ./run and ./runtests use uv run automatically)
source .venv/bin/activate
```

Common uv commands:

| Task | Command |
|------|---------|
| Install/update all deps | `uv sync` |
| Add a new package | `uv add <pkg>` |
| Run a script | `uv run python script.py` |

## Extras

Project Euler code is tracked in a separate private repo. It depends on this project as a local
`uv` path dependency, so clone it as a sibling directory next to this one:

```bash
cd ..
git clone git@github.com:wallberg/project-euler.git euler
cd euler
uv sync
```
