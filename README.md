# FastAPI Supabase Template

A production-ready template for building modern web applications with FastAPI and Supabase, following SOLID principles and best practices.

## Features

- 🚀 FastAPI for high-performance API development
- 🔐 Supabase for authentication and database management
- 📦 Modern dependency management with UV
- 🏗️ SOLID architecture with clean separation of concerns
- 🔒 Row Level Security (RLS) policies out of the box
- 📝 Type hints and Pydantic v2 models
- 🧪 Testing setup with pytest
- 🔄 Automatic OpenAPI/Swagger documentation

## Prerequisites

- Python 3.12+
- [Supabase Account](https://supabase.com)
- UV Package Manager

## Quick Start

1. Clone the template:
```bash
git clone git@github.com:Wirasm/fastapi-supabase.git
cd fastapi-supabase
```

2. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. Install dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

4. Set up the database:
- Go to your Supabase Dashboard
- Open SQL Editor
- Run the SQL files in `src/supabase/sql` in numerical order

5. Run the application:
```bash
uvicorn src.main:app --reload
```

Visit `http://localhost:8000/docs` for the Swagger UI documentation.

## Project Structure

```
fastapi-project/
├── src/
│   ├── core/           # Core application components
│   │   ├── config.py   # Configuration management
│   │   ├── lifespan.py # Application lifespan events
│   │   └── utils.py    # Utility functions
│   ├── shared/         # Shared components
│   │   ├── base_schemas.py  # Base Pydantic models
│   │   └── crud_base.py    # Generic CRUD operations
│   ├── supabase/       # Supabase integration
│   │   ├── sql/        # SQL files for database setup
│   │   ├── client.py   # Supabase client configuration
│   │   └── deps.py     # Dependencies and utilities
│   └── item/           # Example feature module
│       ├── api_v1/     # API endpoints
│       ├── schemas.py  # Data models
│       └── crud.py     # Database operations
├── tests/              # Test suite
├── .env               # Environment variables
└── requirements.txt   # Project dependencies
```

## Database Management

Database changes are managed through SQL files in `src/supabase/sql/`:
1. Files are numbered for execution order (e.g., `01_initial_setup.sql`)
2. Each file contains complete SQL for its changes
3. RLS policies are included with table creation
4. See `src/supabase/sql/README.md` for detailed instructions

## Authentication

Authentication is handled by Supabase:
1. JWT tokens for session management
2. Built-in user management
3. Row Level Security (RLS) policies
4. Secure password handling

## Development Guidelines

1. **Code Style**
   - Use type hints
   - Follow PEP 8
   - Document all public functions and classes

2. **Architecture**
   - Follow SOLID principles
   - Use dependency injection
   - Keep modules independent
   - Implement proper error handling

3. **Security**
   - Never commit sensitive data
   - Always use environment variables
   - Implement proper validation
   - Follow security best practices

## Testing

Run tests with pytest:
```bash
pytest
```

## Deployment

1. Set up your production environment
2. Configure environment variables
3. Run database setup SQL
4. Deploy using your preferred method (Docker, serverless, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## TODO Before Publishing

1. **Documentation**
   - [ ] Add API documentation examples
   - [ ] Include deployment guides for different platforms
   - [ ] Add troubleshooting guide

2. **Testing**
   - [ ] Add comprehensive test suite
   - [ ] Include integration tests
   - [ ] Add load testing examples

3. **Features**
   - [ ] Add example background tasks
   - [ ] Include WebSocket example
   - [ ] Add file upload example
   - [ ] Include caching example

4. **Security**
   - [ ] Add rate limiting
   - [ ] Implement CORS configuration
   - [ ] Add security headers
   - [ ] Include input validation examples

5. **Development**
   - [ ] Add pre-commit hooks
   - [ ] Include CI/CD pipeline
   - [ ] Add Docker configuration
   - [ ] Include development container setup

6. **Examples**
   - [ ] Add more complex CRUD examples
   - [ ] Include pagination example
   - [ ] Add search functionality
   - [ ] Include file handling example

7. **Utilities**
   - [ ] Add logging configuration
   - [ ] Include error tracking setup
   - [ ] Add monitoring examples
   - [ ] Include backup scripts

8. **Performance**
   - [ ] Add caching layer
   - [ ] Include database optimization examples
   - [ ] Add performance testing tools

9. **Dependencies**
   - [ ] Review and update dependencies
   - [ ] Add dependency audit
   - [ ] Include dependency management guide