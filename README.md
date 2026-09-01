# DRF Skeleton

A reusable, production-ready starter skeleton for Django REST Framework projects, with clean separation between **views**, **serializers**, **components** (internal business logic), and **services** (external integrations).

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full breakdown of layer responsibilities.

## Branches

- **`main`** — clean base skeleton (project layout, settings, custom user model, logging, exception handling). No domain-specific feature code.
- **`example`** — branched from `main`, implements a working `users` app (registration, email verification, login, profile) as a reference for how to use the architecture.

## Tech Stack

- Python 3.14
- Django 6.1 + Django REST Framework
- PostgreSQL (via `DATABASE_URL`)
- `djangorestframework-simplejwt` for JWT authentication
- `drf-spectacular` for OpenAPI 3.0 schema + Swagger UI
- `django-environ` for environment-based settings
- Package management via [`uv`](https://docs.astral.sh/uv/)

## Getting Started (using this project as-is)

### 1. Clone the repository

```bash
git clone <repo-url> my-project
cd my-project
```

### 2. Set up the environment

Install dependencies with `uv` (this also creates the virtual environment automatically based on `.python-version`):

```bash
uv sync
```

Copy the environment template and fill in your own values:

```bash
cp .env.example .env
```

Required variables in `.env`:

| Variable | Description |
|---|---|
| `DJANGO_SETTINGS_MODULE` | Settings module to use, e.g. `core.settings.development` |
| `DEBUG` | `True` / `False` |
| `SECRET_KEY` | Django secret key |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `DATABASE_URL` | PostgreSQL connection string |
| `EMAIL_HOST_USER` | SMTP username (for email verification) |
| `EMAIL_HOST_PASSWORD` | SMTP app password |

### 3. Run migrations and start the server

```bash
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

## Project Structure

```
core/
├── settings/
│   ├── base.py          # shared settings
│   ├── development.py
│   ├── staging.py
│   └── production.py
├── exceptions.py         # standardized exception handler
├── urls.py
users/                     # example app (on `example` branch)
├── models.py
├── serializers.py
├── views.py
├── Component.py           # internal business logic (e.g. register_user)
├── services.py            # external integrations (e.g. email sending)
├── urls.py
manage.py
pyproject.toml
.env.example
```

## Logging

Logs are written to both stdout (console) and `logs/errors.log` (see `LOGGING` in `core/settings/base.py`). The `logs/` directory is created automatically at startup.

## Exception Handling

All unhandled API exceptions are intercepted by a custom handler (`core.exceptions.custom_exception_handler`), configured via `REST_FRAMEWORK["EXCEPTION_HANDLER"]`, to return consistent structured JSON error responses across all endpoints.