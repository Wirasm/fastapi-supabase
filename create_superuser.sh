#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the superuser creation script
python -c "import asyncio; from src.scripts.create_superuser import create_superuser; asyncio.run(create_superuser())"

# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
