# Refactoring playbook

1. Hardcoded secret → environment configuration.
2. Request SQL → explicit use cases with parameterized queries.
3. God module → Routes → Controllers → Services → Models/Repositories.
4. Fat controller → thin handler delegating to a service.
5. Global state → factory/lifecycle-managed dependency.
6. Partial writes → transaction with rollback.
7. N+1 → joins, `IN` queries or eager loading.
8. Repeated validation → shared schema/domain validator.
9. Broad errors → typed exceptions and centralized safe responses.
10. Deprecated API → documented modern equivalent after compatibility check.
11. Duplicate serialization → dedicated serializer without secrets.
12. Magic values/dead imports → named constants and lint cleanup.

Preserve HTTP methods, paths, payloads and status codes whenever possible. Validate syntax, boot and representative endpoints after each migration.
