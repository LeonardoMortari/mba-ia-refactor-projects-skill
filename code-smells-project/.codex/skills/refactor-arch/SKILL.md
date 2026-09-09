---
name: refactor-arch
description: Audita e refatora backends legados para MVC, com suporte a Python/Flask e Node.js/Express.
---

# Refactor Arch

Execute as fases abaixo em ordem. Nunca altere arquivos antes da confirmação explícita do usuário ao final da Fase 2.

## Fase 1 — Análise do projeto

1. Inspecione somente arquivos-fonte, manifests, configurações e testes; ignore dependências e artefatos gerados.
2. Detecte linguagem, framework, versão quando disponível, banco, domínio, entry point e dependências.
3. Mapeie a arquitetura atual: rotas, controllers, serviços, modelos, acesso a dados, configuração e middleware.
4. Conte arquivos analisados e registre caminhos e linhas relevantes.
5. Imprima um resumo com stack, domínio, arquitetura atual, riscos e plano de investigação.

Consulte `references/project-analysis.md`.

## Fase 2 — Auditoria

1. Cruze o código com `references/anti-pattern-catalog.md`.
2. Para cada finding, informe severidade, categoria, arquivo e linha exatos, evidência, impacto e recomendação.
3. Não invente achados: quando uma hipótese não puder ser comprovada no código, marque-a como não confirmada.
4. Ordene findings por CRITICAL, HIGH, MEDIUM e LOW.
5. Use o formato de `references/audit-template.md` e inclua contagens por severidade.
6. Salve ou apresente o relatório antes de qualquer mudança.
7. Pergunte exatamente se o usuário deseja prosseguir para a Fase 3. Aguarde confirmação.

## Fase 3 — Refatoração e validação

Após confirmação:

1. Preserve contratos públicos: métodos HTTP, caminhos, payloads e status sempre que possível.
2. Aplique apenas transformações justificadas pelos findings, adaptando-se ao nível de organização existente.
3. Siga `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
4. Extraia configuração e segredos para ambiente/configuração segura.
5. Separe Models, Views/Routes, Controllers, serviços e infraestrutura; centralize erros.
6. Rode formatadores, linters, testes disponíveis e verificações de sintaxe.
7. Inicialize a aplicação em processo controlado e exercite health check e todos os endpoints documentados, usando dados de teste seguros.
8. Registre estrutura final, comandos executados, resultados e limitações. Se algum endpoint não puder ser testado, explique por quê.

## Regras de segurança

- Nunca exponha segredos encontrados no relatório; mas registre caminho e linha.
- Não execute comandos destrutivos, migrações irreversíveis ou exclusões sem autorização.
- Não considere a ausência de testes como prova de funcionamento.
