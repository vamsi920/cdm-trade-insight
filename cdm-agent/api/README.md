# Run instructions for CDM Trade Insight API

## Option 1: Run from cdm-agent directory (Recommended)
```bash
cd cdm-agent
python api/main.py
```

## Option 2: Run with uvicorn directly
```bash
cd cdm-agent
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

## Option 3: Run as module
```bash
cd cdm-agent
python -m api.main
```

**Note:** Always run from the `cdm-agent` directory, not from inside the `api` directory.

