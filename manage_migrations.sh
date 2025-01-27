#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Function to show usage
show_usage() {
    echo "Usage: ./manage_migrations.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  create <name>  - Create a new migration"
    echo "  apply         - Apply pending migrations"
    echo "  seed          - Apply seed data"
    echo ""
    echo "Examples:"
    echo "  ./manage_migrations.sh create add_users_table"
    echo "  ./manage_migrations.sh apply"
    echo "  ./manage_migrations.sh seed"
}

# Check if command is provided
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

# Execute the migration command
python -c "import asyncio; from src.scripts.manage_migrations import create_migration, apply_migrations, apply_seeds; \
    command = '$1'; \
    if command == 'create' and len('$*'.split()) > 1: \
        asyncio.run(create_migration('$2')); \
    elif command == 'apply': \
        asyncio.run(apply_migrations()); \
    elif command == 'seed': \
        asyncio.run(apply_seeds()); \
    else: \
        print('Invalid command or missing arguments')"

# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
