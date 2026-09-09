# MVC guidelines

- Models/repositories own entities and persistence and do not know HTTP.
- Routes/views register endpoints, parse transport input and serialize responses.
- Controllers orchestrate use cases and do not build SQL.
- Services contain reusable business rules and external integrations.
- Configuration reads ports, URLs and secrets from environment variables.
- Middleware centralizes errors, logging and cross-cutting concerns.
- The composition root creates dependencies, registers routes and starts the server.
- For JSON APIs, route handlers are the Views/Routes layer; preserve public contracts.
