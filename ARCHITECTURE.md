# Architecture Research & Design

## 1. Layer Breakdown & Responsibilities

### Views / ViewSets (`views.py` / `viewsets.py`)
**Primary Responsibility:** HTTP presentation layer — request handling, security, and response formatting only.

Key responsibilities:
- Receiving and parsing incoming HTTP requests (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
- Enforcing authentication (`authentication_classes`) and authorization (`permission_classes`).
- Invoking serializers for validation and data representation.
- Delegating any non-trivial business logic to `components/` or `services/`.
- Returning standardized `Response` objects with correct HTTP status codes (`200`, `201`, `400`, `403`, `404`, etc.).

Views should stay thin. They orchestrate, they don't implement business rules.

### Serializers (`serializers.py`)
**Primary Responsibility:** Data validation, transformation, and standard persistence.

Key responsibilities:
- Validating incoming payloads (field-level and object-level validation).
- Converting complex data (querysets, model instances) into native Python types for JSON/XML rendering, and back (serialization/deserialization).
- Handling standard `.create()` / `.update()` ORM operations.
- `ModelSerializer` is used as a shortcut when working directly with model instances/querysets; `Serializer` is used for full manual control.

Serializers should not contain external API calls or complex multi-model business logic — that belongs in components/services.

### Components (`components/`)
**Primary Responsibility:** Internal reusable business logic shared across multiple parts of the app.

Key responsibilities:
- Encapsulating multi-step business logic that spans multiple models/modules.
- Reusable domain actions (e.g. calculating invoice totals, updating reputation scores, distributing rewards).
- Pure internal domain rules, independent of HTTP request/response structure — they should be callable from views, management commands, Celery tasks, etc. without modification.

### Services (`services/`)
**Primary Responsibility:** Boundary layer for external, 3rd-party integrations.

Key responsibilities:
- Managing communication with external APIs/vendors (AWS S3, Stripe, SendGrid, Twilio, etc.).
- Wrapping 3rd-party SDK clients, API keys/tokens, retries, and external error handling.
- Abstracting the external dependency behind a clean interface so it can be mocked/stubbed easily in unit tests.

**Summary — Request flow across layers:**

1. HTTP Request → **Views/ViewSets** (routing, auth, status codes)
2. **Serializers** (validation & persistence)
3. **Components** (internal business logic)
4. **Services** (external tooling — S3, email, payments, etc.)

---

## 2. Helpers vs. Utils

### Utils (`utils/`)
Pure, domain-agnostic, standalone functions that do **not** depend on Django's context, request objects, or database state. They could theoretically be lifted into any Python project without modification.

**Examples:**
- A string sanitizer / slug generator.
- A custom timestamp/date formatting function.
- Generic math or string manipulation helpers.

### Helpers (`helpers/`)
Context-aware functions tied specifically to Django or to this application's domain. They typically take a `request`, a model instance, or domain-specific parameters, and may depend on other parts of the app.

**Examples:**
- A function that extracts the client IP from `request.META`.
- A function that generates tenant-specific file upload paths.
- Form-validation helpers or data-formatting classes tightly coupled to a specific model/domain.

**Key distinction:** if it needs Django's request/DB context to make sense → `helpers/`. If it works the same in any Python program → `utils/`.