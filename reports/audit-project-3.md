# Architecture Audit Report

## Project

- **Project:** `task-manager-api`
- **Stack:** Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 + SQLite
- **Domain:** Task Manager with users, tasks, categories, priorities, statuses and reports
- **Architecture before:** Partially layered with `models`, `routes`, `services` and `utils`, but route handlers still contain validation, persistence, domain rules and serialization.
- **Files analyzed:** 14 Python source files, 1,216 lines total
- **Routes discovered:** task CRUD/search/stats, user CRUD/login, reports and category CRUD, plus health/root endpoints

## Phase 1 — Project Analysis

- Language and framework detected correctly: Python + Flask + Flask-SQLAlchemy.
- Application entry point: `app.py`.
- Existing layers: models, routes, services and utils.
- Main architectural risk: the existing directory layout suggests separation, but business logic remains concentrated in route modules.

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 3 |
| HIGH | 2 |
| MEDIUM | 6 |
| LOW | 4 |
| **Total** | **15** |

## Findings

### [CRITICAL] Insecure MD5 password hashing — A01

- **File:** `task-manager-api/models/user.py:27-32`
- **Evidence:** `set_password` and `check_password` use `hashlib.md5`.
- **Impact:** MD5 is unsuitable for password storage and is vulnerable to fast dictionary and rainbow-table attacks.
- **Recommendation:** use Werkzeug, bcrypt, scrypt or Argon2 password hashing.

### [CRITICAL] Password hash included in user serialization — A01

- **File:** `task-manager-api/models/user.py:16-21`
- **Evidence:** `to_dict()` includes the `password` field.
- **Impact:** user hashes can be exposed by any endpoint returning the model representation.
- **Recommendation:** remove password from all public serializers and use explicit response schemas.

### [CRITICAL] Hardcoded SMTP credential — A01

- **File:** `task-manager-api/services/notification_service.py:7-10`
- **Evidence:** SMTP host, user and password are assigned as string literals.
- **Impact:** source exposure compromises the email account and prevents safe environment separation.
- **Recommendation:** load notification configuration from environment variables or a secret manager.

### [HIGH] Predictable fake authentication token — A01

- **File:** `task-manager-api/routes/user_routes.py:207-210`
- **Evidence:** login returns `fake-jwt-token-` concatenated with the user ID.
- **Impact:** a caller can predict or forge tokens for other users.
- **Recommendation:** use a signed, expiring JWT or a server-side session with secure validation.

### [HIGH] Fat route modules — A04

- **Files:** `task-manager-api/routes/task_routes.py`, `user_routes.py`, `report_routes.py`
- **Evidence:** handlers perform validation, database queries, domain calculations, relationship checks, serialization and transaction handling.
- **Impact:** HTTP concerns are coupled to business logic, reducing testability and reuse.
- **Recommendation:** move use cases to services/controllers and keep routes focused on transport concerns.

### [MEDIUM] Deprecated SQLAlchemy query API — A10

- **Files:** `routes/user_routes.py:29`, `94`, `136`; `routes/task_routes.py:42`, `67`, `117`, `158`; `routes/report_routes.py:105`
- **Evidence:** repeated use of `Model.query.get(...)`.
- **Impact:** warnings and future compatibility problems with modern SQLAlchemy usage.
- **Recommendation:** migrate to `db.session.get(Model, id)` after confirming the installed SQLAlchemy version.

### [MEDIUM] N+1 queries for task relationships — A07

- **File:** `task-manager-api/routes/task_routes.py:14-51`
- **Evidence:** tasks are loaded, then each task separately loads its user and category.
- **Impact:** query count grows with result size.
- **Recommendation:** use eager loading or a joined query.

### [MEDIUM] N+1 queries in user reports — A07

- **File:** `task-manager-api/routes/report_routes.py:53-60`
- **Evidence:** users are loaded and tasks are queried separately for each user.
- **Impact:** report latency and database load grow with the number of users.
- **Recommendation:** aggregate tasks in SQL and group results in the service layer.

### [MEDIUM] Full-table load for task statistics — A07

- **File:** `task-manager-api/routes/task_routes.py:273-296`
- **Evidence:** all tasks are loaded with `Task.query.all()` to calculate overdue totals in Python.
- **Impact:** unnecessary memory and CPU usage as the task table grows.
- **Recommendation:** use database-side `COUNT` and filtered aggregates.

### [MEDIUM] Generic exception handling — A09

- **Files:** `routes/task_routes.py:62`, `137`, `204`, `236`; `routes/report_routes.py:186`
- **Evidence:** bare `except:` blocks catch every exception without logging or classification.
- **Impact:** programming errors are hidden and diagnosis is difficult.
- **Recommendation:** catch expected exceptions, rollback explicitly and centralize error responses.

### [MEDIUM] Weak password policy — A08

- **Files:** `routes/user_routes.py:64-65`, `114-116`
- **Evidence:** passwords with only four characters are accepted.
- **Impact:** accounts are vulnerable to brute-force and dictionary attacks.
- **Recommendation:** centralize a stronger password policy and rate-limit authentication attempts.

### [MEDIUM] Duplicated business and serialization logic — A11

- **Files:** `routes/user_routes.py:33-38`, `160-181`; `routes/task_routes.py:14-51`, `267-271`
- **Evidence:** tasks are represented and enriched differently in multiple handlers.
- **Impact:** response contracts can diverge and fixes must be repeated.
- **Recommendation:** introduce serializers and reusable task/user query services.

### [LOW] Dead and unnecessary imports — A12

- **Files:** `app.py:7`, `routes/user_routes.py:6`, `routes/task_routes.py:7`, `utils/helpers.py:2-7`
- **Evidence:** modules import unused `sys`, `json`, `os`, `time`, `math` or `hashlib` symbols.
- **Impact:** reduces clarity and indicates missing lint enforcement.
- **Recommendation:** remove unused imports and add a linter to the validation workflow.

### [LOW] Naive UTC datetime usage — A12

- **Files:** `models/task.py:15-16`, `routes/task_routes.py:31`, `215`, `services/notification_service.py:35`
- **Evidence:** repeated use of `datetime.utcnow()` without an explicit timezone policy.
- **Impact:** comparisons and presentation can become inconsistent across environments.
- **Recommendation:** use timezone-aware datetimes and a single persistence/display policy.

### [LOW] In-memory notification state — A05

- **File:** `task-manager-api/services/notification_service.py:5-6`, `43-48`
- **Evidence:** notifications are stored in an instance list and filtered in memory.
- **Impact:** data disappears on restart and behavior differs across processes.
- **Recommendation:** persist notifications or use a dedicated queue/store if the feature is required.

### [LOW] Repeated magic values — A12

- **Files:** `routes/task_routes.py:177`, `182-183`; `routes/user_routes.py:71-72`, `120-121`
- **Evidence:** statuses, roles and numeric limits are repeated directly in route code.
- **Impact:** changes can become inconsistent across endpoints.
- **Recommendation:** centralize enums and validation constants in the domain layer.

## Manual analysis coverage

The audit identifies more than five manually documented findings, including three critical security issues, architectural coupling, deprecated APIs, N+1 queries, inefficient aggregation and weak error handling.

## Confirmation gate

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

## Phase 3 — Refactoring Result

- Confirmation received: `y`.
- Existing layered structure was preserved and strengthened with `config/settings.py` and `controllers/task_controller.py`.
- Application configuration and secret key now come from environment variables.
- Passwords now use Werkzeug password hashing instead of MD5.
- Passwords are removed from user serialization.
- SMTP credentials now come from environment variables.
- Authentication token generation no longer uses a predictable user ID string.
- Deprecated `Model.query.get(...)` calls were migrated to `db.session.get(...)`.
- Application error handling is centralized in the Flask application factory.
- Python syntax compilation: **passed** with the workspace bundled Python runtime.

### Runtime validation

Runtime smoke test executed successfully after installing `requirements.txt`:

- `GET /health`: **200 OK**
- `GET /`: **200 OK**
- `GET /tasks`: **200 OK**
- `GET /users`: **200 OK**
- `GET /reports/summary`: **200 OK**
- `GET /categories`: **200 OK**

The API booted without errors and all checked endpoints continued responding after the refactoring. The empty collections are expected for the fresh local database because the seed script was not executed during the smoke test.
