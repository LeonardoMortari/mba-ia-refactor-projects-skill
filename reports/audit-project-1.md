# Architecture Audit Report

## Project

- **Project:** `code-smells-project`
- **Stack:** Python 3 + Flask 3.1.1 + flask-cors 5.0.1 + SQLite
- **Domain:** E-commerce API: produtos, usuários, pedidos e relatórios de vendas
- **Architecture before:** Monolítica; `app.py` registra rotas, `controllers.py` concentra HTTP/validação, `models.py` mistura SQL e domínio e `database.py` gerencia SQLite globalmente.
- **Files analyzed:** 4 Python source files, 780 lines total (`app.py` 88, `controllers.py` 292, `database.py` 86, `models.py` 314)
- **Database:** SQLite; tabelas `produtos`, `usuarios`, `pedidos` e `itens_pedido`

## Phase 1 — Project Analysis

- Language and framework detected correctly: Python + Flask.
- Application entry point: `app.py`.
- Routes discovered: product, user, login, order, sales report, health and two administrative routes.
- Current architecture: monolithic with limited separation of concerns.

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 3 |
| HIGH | 4 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **12** |

## Findings

### [CRITICAL] SQL injection and unrestricted SQL administration — A02

- **File:** `code-smells-project/app.py:59-78`
- **Evidence:** `/admin/query` reads `dados.get("sql", "")` and executes `cursor.execute(query)`.
- **Impact:** an unauthenticated caller can read, alter or delete arbitrary database data.
- **Recommendation:** remove the generic SQL endpoint and expose only authorized use cases with parameterized queries.

### [CRITICAL] Hardcoded secret and plaintext credentials — A01

- **Files:** `code-smells-project/app.py:7`, `database.py:31`, `database.py:76`
- **Evidence:** literal `SECRET_KEY` and user passwords stored directly in the database seed and schema flow.
- **Impact:** application signing material and user credentials can be compromised.
- **Recommendation:** use environment configuration and a password hashing algorithm such as Argon2, bcrypt or Werkzeug hashing.

### [CRITICAL] Sensitive secret exposed by health endpoint — A01

- **File:** `code-smells-project/controllers.py:285-289`
- **Evidence:** health response includes `db_path`, `debug` and `secret_key`.
- **Impact:** exposes internal configuration and the application secret to any caller of `/health`.
- **Recommendation:** return only non-sensitive liveness information.

### [HIGH] God module and controller responsibilities — A03/A04

- **Files:** `code-smells-project/controllers.py:1-292`, `models.py:1-314`
- **Evidence:** HTTP handling, validation, business rules, SQL, serialization, notifications and error conversion are distributed without meaningful layer boundaries.
- **Impact:** high coupling, difficult isolated testing and risky changes.
- **Recommendation:** introduce routes/views, controllers, services and domain-specific models/repositories.

### [HIGH] Global mutable database connection — A05

- **File:** `code-smells-project/database.py:4-10`
- **Evidence:** module-level `db_connection`, `global db_connection` and `check_same_thread=False`.
- **Impact:** unsafe lifecycle and concurrency behavior; difficult dependency isolation in tests.
- **Recommendation:** use an application factory and controlled connection lifecycle, preferably one connection per request/context.

### [HIGH] Order workflow lacks explicit atomic transaction — A06

- **File:** `code-smells-project/models.py:133-168`
- **Evidence:** order, item and stock operations are performed sequentially without a clear transaction boundary and rollback strategy.
- **Impact:** partial failures can leave order, inventory and item records inconsistent.
- **Recommendation:** wrap the use case in one transaction and rollback on any failure.

### [HIGH] SQL built with string concatenation — A02

- **Files:** `code-smells-project/models.py:28`, `92`, `110`, `127`, `140`, `155`, `174`, `188-192`, `220-224`, `289-299`
- **Evidence:** identifiers and user input are interpolated into SQL strings instead of consistently using parameters.
- **Impact:** injection risk in product, user, login, order and search operations.
- **Recommendation:** use parameterized statements or a repository/ORM layer for every dynamic value.

### [MEDIUM] N+1 queries in order and report paths — A07

- **Files:** `code-smells-project/models.py:174-224`
- **Evidence:** each order loads its items, then each item loads its product with another query.
- **Impact:** query count grows with the number of orders and items.
- **Recommendation:** replace loops of dependent queries with joins, `IN` queries or preloaded mappings.

### [MEDIUM] Duplicated validation rules — A08

- **Files:** `code-smells-project/controllers.py:24-55`, `64-92`
- **Evidence:** create and update product handlers repeat required fields, numeric limits and category validation.
- **Impact:** rules can diverge and changes must be applied in multiple handlers.
- **Recommendation:** centralize request/domain validation in reusable schemas or services.

### [MEDIUM] Generic exception handling and error leakage — A09

- **Files:** `code-smells-project/controllers.py:10-12`, `60-62`, `95-96`, `app.py:77-78`
- **Evidence:** broad `except Exception` blocks return `str(e)` to clients.
- **Impact:** internal database/application details can leak and debugging becomes inconsistent.
- **Recommendation:** centralize error handling, log internal details and return safe public messages.

### [LOW] Magic values and duplicated serialization — A11/A12

- **Files:** `code-smells-project/controllers.py:52`, `242`, `app.py:35-44`, `models.py:1-314`
- **Evidence:** categories, statuses, versions and response dictionaries are hardcoded across handlers and model functions.
- **Impact:** maintenance friction and inconsistent response contracts.
- **Recommendation:** use named constants/enums and dedicated serializers.

### [LOW] Print-based operational logging — A12

- **Files:** `code-smells-project/controllers.py:8`, `57`, `106`, `208-210`
- **Evidence:** errors, notifications and operational events are written with `print`.
- **Impact:** no log levels, structured context, correlation or environment control.
- **Recommendation:** use the standard logging framework with secrets redacted.

## Manual analysis coverage

The audit confirms at least five findings from the manual analysis, including critical security issues, architectural violations, performance problems and maintainability issues.

## Confirmation gate

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

## Phase 3 — Refactoring Result

- Confirmation received: `y`.
- MVC structure created under `code-smells-project/src/` with `config`, `database`, `models`, `controllers`, `views` and `middlewares`.
- Root `app.py` now acts as a compatibility entry point importing `src.app`.
- Dynamic SQL was replaced by parameterized queries in the new data layer.
- The unrestricted `/admin/query` and destructive admin reset route are no longer registered.
- User response serializers omit password fields.
- Order creation now uses a transaction with rollback on failure.
- Health endpoint no longer exposes secrets or filesystem details.

### Validation

- Python syntax compilation: **passed** with the workspace bundled Python runtime.
- Route registration and runtime smoke test: **passed** after installing `requirements.txt` in the local Python environment.
- `GET /health`: **200 OK**.
- `GET /produtos`: **200 OK**.
