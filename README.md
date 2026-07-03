<div align="center">

# AI Form Builder API

**Build forms through natural language — powered by Groq + FastAPI**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=fff)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=fff)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=fff)](https://postgresql.org)
[![Groq](https://img.shields.io/badge/Groq-000?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptMCAxOGMtNC40MSAwLTgtMy41OS04LThzMy41OS04IDgtOCA4IDMuNTkgOCA4LTMuNTkgOC04IDh6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

A REST API that lets users build dynamic forms through natural language conversations. Describe the form you want, and the API uses Groq's LLM to generate structured questions with proper validation rules. Iterate via follow-up prompts, publish, and collect responses — all through clean REST endpoints.

**Frontend Repository:** [github.com/bruce-pain/ai-form-builder-fe](https://github.com/bruce-pain/ai-form-builder-fe)

---

## Architecture

### LLM + Instruction Engine

The LLM doesn't output final form JSON directly. Instead, it emits a list of deterministic editing operations (`set_title`, `add_question`, `update_question`, `remove_question`, `reorder_questions`) that a local instruction engine applies. This keeps the LLM's role narrow and verifiable — the engine enforces constraints like unique question IDs, valid reorderings, and type-appropriate validation rules.

### Conversational Refinement

Users can iteratively refine a form across multiple turns. Prior prompts are persisted and replayed alongside the current form state, enabling natural interactions like _"add a question about age"_ followed by _"make the email field required"_.

### Layered Architecture

Clean separation of concerns:

```
Routes (HTTP) → Service (Business Logic) → Repository (Data Access) → Database
```

Each layer is independently testable. Pydantic schemas handle request/response validation, and SQLAlchemy ORM manages persistence with Alembic for migrations.

---

## Tech Stack

| Category             | Choice                                    |
| -------------------- | ----------------------------------------- |
| Framework            | [FastAPI](https://fastapi.tiangolo.com)   |
| Database             | [PostgreSQL](https://postgresql.org)      |
| Migrations           | [Alembic](https://alembic.sqlalchemy.org) |
| LLM Provider         | [Groq API](https://groq.com)              |
| Auth                 | JWT (access + refresh tokens)             |
| Package Manager      | [uv](https://github.com/astral-sh/uv)     |
| Linting / Formatting | [Ruff](https://docs.astral.sh/ruff)       |
| Testing              | [pytest](https://pytest.org)              |

---

## Features

- **JWT Authentication** — Register, login, and token refresh with access/refresh token pairs
- **Form CRUD** — Full create, read, update, delete for forms with structured question schemas
- **AI Question Generation** — Describe a form in plain English; the LLM generates a complete set of questions with appropriate types (text / select / multi-select) and validation rules
- **Public Response Collection** — Submit responses to published forms without authentication (ideal for embedding in external sites)
- **Response Dashboard** — Authenticated users can view all responses collected for their forms
- **Structured Logging** — Application and error logs persisted to file with rotation

---

## API Endpoints

### Authentication

| Method | Path                         | Description                           |
| ------ | ---------------------------- | ------------------------------------- |
| POST   | `/api/v1/auth/register`      | Create a new user account             |
| POST   | `/api/v1/auth/login`         | Login with email and password         |
| POST   | `/api/v1/auth/token/refresh` | Refresh access and refresh tokens     |
| GET    | `/api/v1/auth/user`          | Get details of the authenticated user |

### Forms

| Method | Path                        | Description                               |
| ------ | --------------------------- | ----------------------------------------- |
| POST   | `/api/v1/forms`             | Create a new form                         |
| GET    | `/api/v1/forms`             | List all forms for the authenticated user |
| GET    | `/api/v1/forms/{id}`        | Get a single form                         |
| PATCH  | `/api/v1/forms/{id}`        | Update a form                             |
| DELETE | `/api/v1/forms/{id}`        | Delete a form                             |
| GET    | `/api/v1/forms/public/{id}` | Get a published form (no auth required)   |

### AI Question Generation

| Method | Path          | Description                                                       |
| ------ | ------------- | ----------------------------------------------------------------- |
| POST   | `/api/v1/llm` | Generate or modify form questions using a natural language prompt |

### Responses

| Method | Path                                 | Description                                              |
| ------ | ------------------------------------ | -------------------------------------------------------- |
| POST   | `/api/v1/forms/{id}/responses`       | Submit a response to a published form (no auth required) |
| GET    | `/api/v1/forms/{id}/responses`       | List all responses for a form (auth required)            |
| GET    | `/api/v1/forms/{id}/responses/{rid}` | Get a single response (auth required)                    |

---

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL
- [uv](https://github.com/astral-sh/uv) (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A [Groq API key](https://console.groq.com/keys)

### Setup

```sh
# Clone the repository
git clone https://github.com/yourusername/AI-form-builder-be.git
cd AI-form-builder-be

# Create environment file
cp .env.sample .env

# Fill in your environment variables (see table below)
# Install dependencies
make install

# Run database migrations
make upgrade

# Start the development server
make run
```

The server starts at `http://localhost:8000`.

### Environment Variables

| Variable               | Description                           |
| ---------------------- | ------------------------------------- |
| `ENVIRONMENT`          | Runtime environment (`dev` or `prod`) |
| `DATABASE_TYPE`        | Database type (`postgresql`)          |
| `DATABASE_NAME`        | Database name                         |
| `DATABASE_USER`        | Database username                     |
| `DATABASE_PASSWORD`    | Database password                     |
| `DATABASE_HOST`        | Database host                         |
| `DATABASE_PORT`        | Database port                         |
| `GROQ_API_KEY`         | API key for Groq LLM access           |
| `SECRET_KEY`           | Secret key for JWT signing            |
| `ALGORITHM`            | JWT signing algorithm (`HS256`)       |
| `ACCESS_TOKEN_EXPIRY`  | Access token lifetime in hours        |
| `REFRESH_TOKEN_EXPIRY` | Refresh token lifetime in hours       |

### Database Setup

```sh
# Create the database
createdb your_database_name

# Generate a new migration (after model changes)
make migrate message="description of changes"

# Apply pending migrations
make upgrade
```

> [!IMPORTANT]
> After adding new models, import them in `alembic/env.py` so Alembic can detect them.

---

## Development Commands

| Command          | Description                              |
| ---------------- | ---------------------------------------- |
| `make run`       | Start development server with hot reload |
| `make install`   | Install project dependencies             |
| `make migrate`   | Generate a new migration                 |
| `make upgrade`   | Apply all pending migrations             |
| `make downgrade` | Revert the last migration                |
| `make test`      | Run the test suite                       |
| `make lint`      | Check code for linting errors            |
| `make format`    | Format the codebase                      |
| `make clean`     | Remove cache and generated files         |

Run `make help` to see all available commands.

---

## Project Structure

```
├── app/
│   ├── core/
│   │   ├── base/                  # Base classes (model, schema, repository)
│   │   ├── dependencies/          # Dependency injection (auth, db session)
│   │   ├── config.py              # Application settings
│   │   ├── database.py            # Database connection setup
│   │   ├── groq.py                # Groq client initialization
│   │   ├── logger.py             # Logging configuration
│   │   └── response_messages.py   # Standard API response helpers
│   ├── features/
│   │   ├── auth/                  # Authentication (register, login, JWT)
│   │   ├── form/                  # Form CRUD operations
│   │   ├── llm/                   # AI question generation via Groq
│   │   ├── response/              # Form response collection
│   │   └── router.py              # Central route aggregation
│   └── main.py                    # Application entry point
├── alembic/                       # Database migrations
├── tests/                         # Test suite
├── Makefile                       # Development command shortcuts
├── pyproject.toml                 # Project configuration & dependencies
└── .env.sample                    # Environment variable template
```

---

## API Documentation

Once the server is running:

- **Swagger UI** — [http://localhost:8000/v1/docs](http://localhost:8000/v1/docs)
- **ReDoc** — [http://localhost:8000/v1/redoc](http://localhost:8000/v1/redoc)

---

## License

[MIT](LICENSE)
