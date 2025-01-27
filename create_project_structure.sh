#!/bin/bash

# Create base directory structure
mkdir -p src/{common,supabase}
mkdir -p tests/{common,supabase}

# Create supabase module
mkdir -p src/supabase
touch src/supabase/{__init__.py,api.py,auth.py,client.py,dependencies.py,schemas.py}

# Create common module (for shared utilities)
mkdir -p src/common
touch src/common/{__init__.py,exceptions.py,pagination.py}

# Create root level files
touch src/{__init__.py,main.py,config.py}
touch {.env,.gitignore,README.md} 