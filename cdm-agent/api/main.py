"""
Main entry point for the CDM Trade Insight API server

IMPORTANT: Run from cdm-agent directory:
    cd cdm-agent
    python api/main.py
"""
import sys
import os
from pathlib import Path

# Ensure we're running from the correct directory context
# Get the cdm-agent directory (parent of api/)
cdm_agent_dir = Path(__file__).parent.parent.resolve()

# Change to cdm-agent directory if not already there
os.chdir(cdm_agent_dir)

# Add cdm-agent directory to Python path
if str(cdm_agent_dir) not in sys.path:
    sys.path.insert(0, str(cdm_agent_dir))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(cdm_agent_dir)]  # Watch the cdm-agent directory
    )
