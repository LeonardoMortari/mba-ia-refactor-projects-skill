# Project analysis heuristics

- Confirm Python/Flask from manifests and imports; confirm Node/Express from `package.json` and imports.
- Identify entry point, dependencies, database technology, tables/models, domain vocabulary and route map.
- Follow each route to controller, service, model/repository and infrastructure.
- Classify architecture as monolithic, partially layered or MVC.
- Record exact current file and line numbers for every finding.
