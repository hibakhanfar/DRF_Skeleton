# DRF Skeleton

A reusable, production-ready starter skeleton for Django REST Framework projects, with clean separation between **views**, **serializers**, **components** (internal business logic), and **services** (external integrations).

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full breakdown of layer responsibilities.

### Branches

* **`main`** — Clean base skeleton (project layout, settings, custom user model, logging, exception handling). No domain-specific feature code.
* **`example`** — Branched from `main`, implements a working users app (registration, email verification, login, profile) as a reference for how to use the architecture.
* **`file`** — Branched from `example`, adds secure file upload capabilities with custom MIME-type validation using `python-magic` for robust header/magic-bytes checking.
* **`S3`** — Branched from `file`, replaces local disk storage (`MEDIA_ROOT`) with S3-compatible object storage via `django-storages` + `boto3`. Configured against Backblaze B2 by default, but works with any S3-compatible provider.
## Tech Stack

- Python 3.14
- Django 6.1 + Django REST Framework
- PostgreSQL (via `DATABASE_URL`)
- `djangorestframework-simplejwt` for JWT authentication
- `drf-spectacular` for OpenAPI 3.0 schema + Swagger UI
- `django-environ` for environment-based settings
- `python-magic` for magic-bytes file type validation on uploads (needs system `libmagic`)
- `django-storages` + `boto3` for S3-compatible object storage (`S3` branch)
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

Additional variables required on the **`S3`** branch (see [Cloud Storage](#cloud-storage-s3-compatible--backblaze-b2) below):

| Variable | Description |
|---|---|
| `USE_S3` | `True` to store uploads on S3-compatible storage instead of local disk |
| `AWS_ACCESS_KEY_ID` | Access key ID for the storage provider |
| `AWS_SECRET_ACCESS_KEY` | Secret access key |
| `AWS_STORAGE_BUCKET_NAME` | Bucket name (case-sensitive, must match exactly) |
| `AWS_S3_ENDPOINT_URL` | S3-compatible endpoint, e.g. `https://s3.us-east-005.backblazeb2.com` |
| `AWS_S3_REGION_NAME` | Region name, e.g. `us-east-005` |

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

## API Endpoints (`example` branch — `users` app)

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| `POST` | `/api/register/` | No | Register a new user, sends an email verification link |
| `GET` | `/api/email-verify/?token=...` | No | Verify a user's email using the JWT token from the email link |
| `POST` | `/api/login/` | No | Obtain JWT access/refresh tokens (blocks unverified users) |
| `POST` | `/api/token/refresh/` | No | Refresh an expired access token |
| `GET` | `/api/me/` | Yes | Get the authenticated user's profile (requires verified email) |
| `POST` | `/api/upload-file/` | Yes | Upload a document for the authenticated user (requires verified email) |

Interactive docs: `/api/docs/` (Swagger UI) · Raw schema: `/api/schema/`

## File Uploads

The `upload-file` endpoint (`users/views.py::FileUploadView`) lets an authenticated, verified user attach a document to their account via `multipart/form-data`.

**Where files are stored**, configured in `core/settings/base.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

The `User.file` field itself decides the sub-folder:

```python
# users/models.py
file = models.FileField(upload_to='docs/', null=True, blank=True)
```

So an uploaded file ends up at `media/docs/<filename>` and is served at `/media/docs/<filename>` — this path is what the API returns in the response, not the raw file bytes.

The `media/` directory is git-ignored on purpose (uploaded files are runtime user data, not source code) and is created automatically by Django the first time a file is uploaded — no manual setup needed after cloning.

**Validation:** `users/serializers.py::FileSerializer.validate_file` checks the file's actual content (magic bytes), not just its extension, restricting uploads to `image/png`, `image/jpeg`, and `application/pdf`.

This relies on `libmagic`, a system-level C library — not a pure Python package — so the setup differs slightly per OS. `pyproject.toml` handles this automatically with OS-conditional dependencies:

```toml
"python-magic>=0.4.27; sys_platform != 'win32'",
"python-magic-bin>=0.4.14; sys_platform == 'win32'",
```

| OS | What gets installed | Extra setup needed |
|---|---|---|
| **Windows** | `python-magic-bin` | None — it bundles the required `libmagic` DLLs |
| **macOS** | `python-magic` | `brew install libmagic` (one-time) |

`uv sync` reads `sys_platform` and picks the right package automatically — no manual choice needed. Just run `uv sync`, then (on macOS/Linux only) install the system `libmagic` library once.

> Note: `python-magic-bin` hasn't been updated since 2017 and only ships Intel builds for macOS — it doesn't support Apple Silicon (M-series) Macs. That's why macOS always uses plain `python-magic` + Homebrew's `libmagic` instead, regardless of chip.

To verify `libmagic` is set up correctly after `uv sync`:

```bash
uv run python -c "import magic; print('OK')"
```

**Swagger/OpenAPI note:** the request body for this endpoint must render as a binary file picker (`string($binary)`), not a plain text field (`string($uri)`). This requires `COMPONENT_SPLIT_REQUEST: True` in `SPECTACULAR_SETTINGS` (`core/settings/base.py`) — without it, drf-spectacular reuses the same schema for the request and the response, and since the response returns the file as a URL string, the request field incorrectly inherits that `uri` format too.

## Cloud Storage (S3-Compatible / Backblaze B2)

On the **`S3`** branch, set `USE_S3=True` in `.env` to route all `FileField`/`ImageField` uploads through S3-compatible object storage instead of local disk. When `USE_S3` is unset or `False`, the project falls back transparently to `MEDIA_ROOT` .

Configuration lives in `core/settings/base.py`:

```python
if env.bool('USE_S3', default=False):

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": env("AWS_ACCESS_KEY_ID"),
                "secret_key": env("AWS_SECRET_ACCESS_KEY"),
                "bucket_name": env("AWS_STORAGE_BUCKET_NAME"),
                "endpoint_url": env("AWS_S3_ENDPOINT_URL"),
                "region_name": env("AWS_S3_REGION_NAME", default="us-east-005"),
                "querystring_auth": False,
        
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
```

- `querystring_auth: False` — bucket is private, but this keeps generated URLs clean (no signed query params baked into the stored URL).

### Setting up a Backblaze B2 bucket

1. Create a bucket at [backblaze.com](https://www.backblaze.com/) (Private is fine — the app never needs public URLs).
2. Note the bucket's **Endpoint** (e.g. `s3.us-east-005.backblazeb2.com`) and region (e.g. `us-east-005`).
3. **Create an Application Key — not the Master Application Key.** B2's S3-compatible API does not accept the Master Application Key at all; auth attempts with it fail, and depending on the operation this can surface as either a clean `InvalidAccessKeyId` error or, confusingly, as a dropped/aborted connection (`ConnectionClosedError` / `BadStatusLine`) during upload. Go to **Application Keys → Add a New Application Key**, scope it to the bucket, and use *that* `keyID` / `applicationKey` pair.
4. Fill in the `.env` variables listed in [Getting Started](#2-set-up-the-environment) above.

## Logging

Logs are written to both stdout (console) and `logs/errors.log` (see `LOGGING` in `core/settings/base.py`). The `logs/` directory is created automatically at startup.

## Exception Handling

All unhandled API exceptions are intercepted by a custom handler (`core.exceptions.custom_exception_handler`), configured via `REST_FRAMEWORK["EXCEPTION_HANDLER"]`, to return consistent structured JSON error responses across all endpoints.