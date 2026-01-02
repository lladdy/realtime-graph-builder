# graph-builder

A small FastAPI example + graph builder utilities.

## Quickstart — run the app with uvicorn

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install runtime deps

```bash
uv sync
```

3. Run the app

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

4. Open http://127.0.0.1:8000/ or http://127.0.0.1:8000/docs for the interactive API docs.

## Development & tests

Set up a development environment (recommended):

```bash
# use uv to setup a virtual environment and install dev dependencies
uv -e .venv python
source .venv/bin/activate
uv synci
```

Install runtime + test/dev dependencies:

```bash
pip install -e .[test]
```

Run the tests with pytest:

```bash
pytest -q
```
