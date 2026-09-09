# Architecture Audit Report

## Project

- **Project:** `ecommerce-api-legacy`
- **Stack:** Node.js + Express 4.18.2 + SQLite3 5.1.6
- **Domain:** LMS with users, courses, enrollments, payments and financial reporting
- **Architecture before:** Monolithic `AppManager` responsible for database setup, routes, validation, checkout, payment, reporting and deletion.
- **Files analyzed:** 3 JavaScript source files, 180 lines total (`app.js` 14, `AppManager.js` 141, `utils.js` 25)
- **Database:** SQLite in-memory; tables `users`, `courses`, `enrollments`, `payments` and `audit_logs`

## Phase 1 — Project Analysis

- Language and framework detected correctly: JavaScript/Node.js + Express.
- Application entry point: `src/app.js`.
- Routes discovered: checkout, financial report and user deletion.
- Current architecture: monolithic class with nested callbacks and utility-level global state.

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 2 |
| HIGH | 3 |
| MEDIUM | 3 |
| LOW | 4 |
| **Total** | **12** |

## Findings

### [CRITICAL] Hardcoded production secrets — A01

- **File:** `ecommerce-api-legacy/src/utils.js:1-6`
- **Evidence:** database credentials, payment gateway key and SMTP user are literal values in source.
- **Impact:** credentials can be exposed through source control and reused outside the application.
- **Recommendation:** load configuration from environment variables and fail safely when required production secrets are absent.

### [CRITICAL] Sensitive payment data written to logs — A01

- **File:** `ecommerce-api-legacy/src/AppManager.js:45`
- **Evidence:** checkout logs the card value and payment gateway key.
- **Impact:** payment data may be retained by logs and observability systems.
- **Recommendation:** never log card data or secret keys; use masked transaction identifiers only.

### [HIGH] Weak password hashing — A08

- **File:** `ecommerce-api-legacy/src/utils.js:17-23`
- **Evidence:** `badCrypto` repeats Base64 encoding and truncates the result as a password hash.
- **Impact:** Base64 is not password hashing and provides no meaningful protection.
- **Recommendation:** use a dedicated password hashing algorithm such as Argon2, scrypt or bcrypt.

### [HIGH] God Class and mixed responsibilities — A03/A04

- **File:** `ecommerce-api-legacy/src/AppManager.js:4-141`
- **Evidence:** one class creates schema and seed data, registers routes, validates input, executes checkout, records payments, generates reports and deletes users.
- **Impact:** high coupling, difficult testing and risky changes.
- **Recommendation:** separate routes, controllers, checkout service, payment service, repositories and configuration.

### [HIGH] Checkout lacks transaction boundary — A06

- **File:** `ecommerce-api-legacy/src/AppManager.js:50-63`
- **Evidence:** enrollment, payment and audit inserts are independent nested operations without SQLite transaction or rollback.
- **Impact:** partial checkout state can remain after a failure.
- **Recommendation:** execute the use case inside one transaction and rollback every related write on failure.

### [MEDIUM] N+1 queries in financial report — A07

- **File:** `ecommerce-api-legacy/src/AppManager.js:80-127`
- **Evidence:** courses, enrollments, users and payments are loaded through nested queries and loops.
- **Impact:** query count and response time grow with the number of courses and enrollments.
- **Recommendation:** use a parameterized aggregate query with joins and grouping.

### [MEDIUM] Inconsistent database error handling — A09

- **Files:** `ecommerce-api-legacy/src/AppManager.js:37-42`, `50-61`, `131-136`
- **Evidence:** callbacks check errors inconsistently; the delete route ignores the error before returning success.
- **Impact:** clients may receive success for failed operations and operators lack reliable diagnostics.
- **Recommendation:** centralize error mapping and reject every failed database operation.

### [MEDIUM] User deletion leaves orphaned business data — A08

- **File:** `ecommerce-api-legacy/src/AppManager.js:131-136`
- **Evidence:** only the user row is deleted while enrollments and payments remain.
- **Impact:** reports can contain orphaned references and inconsistent financial history.
- **Recommendation:** define a retention policy using soft delete, foreign keys/cascade or an explicit deletion block.

### [LOW] Global mutable cache and unused revenue state — A05

- **File:** `ecommerce-api-legacy/src/utils.js:9-10`
- **Evidence:** `globalCache` and `totalRevenue` are module-level mutable state; the exported primitive cannot be updated by consumers as intended.
- **Impact:** behavior is difficult to test and reason about across requests.
- **Recommendation:** encapsulate cache/metrics behind an injected component or remove unused state.

### [LOW] Weak seeded credential — A12

- **File:** `ecommerce-api-legacy/src/AppManager.js:18-21`
- **Evidence:** initial user is created with password `'123'`.
- **Impact:** unsafe if the seed data survives outside local development.
- **Recommendation:** use environment-provided development credentials and never reuse them in production.

### [LOW] Abbreviated request contract — A08

- **File:** `ecommerce-api-legacy/src/AppManager.js:28-35`
- **Evidence:** checkout expects `usr`, `eml`, `pwd` and `c_id`.
- **Impact:** reduces readability, discoverability and validation quality.
- **Recommendation:** use explicit names and a request schema while preserving backward compatibility during migration.

### [LOW] Callback nesting — A12

- **File:** `ecommerce-api-legacy/src/AppManager.js:37-127`
- **Evidence:** course lookup, user lookup, user creation, enrollment, payment and audit are nested callbacks.
- **Impact:** control flow, error paths and tests are difficult to follow.
- **Recommendation:** encapsulate database calls as promises and compose the use case with `async`/`await`.

## Manual analysis coverage

The audit identifies at least five manually documented findings, including hardcoded secrets, weak cryptography, a God Class, missing transaction boundaries, N+1 queries and orphaned data.

## Confirmation gate

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

## Phase 3 — Refactoring Result

- Confirmation received: `y`.
- MVC structure created under `src/` with `config`, `database`, `models`, `services`, `controllers`, `routes` and `middlewares`.
- `AppManager.js` and `utils.js` were removed; `src/app.js` is now the composition root.
- Configuration is read from environment variables.
- Checkout now uses parameterized queries and an explicit SQLite transaction with rollback.
- Payment card data and gateway keys are no longer logged.
- Financial report uses one aggregate query instead of nested N+1 queries.
- User deletion removes dependent payments and enrollments before deleting the user.

### Validation

- Dependencies installed with `npm ci`: **passed**.
- Application boot: **passed**; server started on port 3000.
- `POST /api/checkout`: **200 OK**.
- `GET /api/admin/financial-report`: **200 OK**.
- `DELETE /api/users/2`: **200 OK**.
- `npm audit` reported vulnerabilities in the legacy dependency tree; these are documented for a subsequent dependency-upgrade pass and are not introduced by the MVC restructuring.
