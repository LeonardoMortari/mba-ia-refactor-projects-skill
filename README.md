# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

## Ferramenta escolhida: OpenAI Codex

Embora o enunciado use Claude Code como referência, este projeto será executado com o Codex. Para manter compatibilidade com o formato original e, ao mesmo tempo, permitir a execução no Codex, a Skill é mantida nos dois caminhos:

```text
.claude/skills/refactor-arch/  # convenção original do desafio
.codex/skills/refactor-arch/   # cópia usada na execução com Codex
```

O conteúdo das duas cópias é idêntico: `SKILL.md` e os cinco arquivos de referência em Markdown. No Codex, a Skill será invocada por uma instrução explícita apontando para `.codex/skills/refactor-arch/SKILL.md`, preservando as três fases e a confirmação obrigatória entre auditoria e refatoração.

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

## Análise Manual

A análise foi realizada antes da criação e execução da Skill. As linhas indicadas referem-se ao estado original dos projetos.

### Projeto 1 — `code-smells-project`

Stack: Python + Flask + SQLite. Domínio: e-commerce com produtos, usuários, pedidos e relatórios. Arquitetura: monolítica.

- **[CRITICAL] SQL Injection/backdoor administrativo:** `app.py:59-78` executa SQL recebido da requisição; há SQL por concatenação em `models.py:28`, `92`, `110`, `127`, `140`, `155`, `174`, `188-192`, `220-224` e `289-299`. Permite consultar, modificar ou apagar dados.
- **[CRITICAL] Segredos e senhas expostos:** `app.py:7`, `database.py:31`, `database.py:76` e `controllers.py:289` fixam a chave secreta e armazenam/retornam senhas sem hash. O endpoint `/health` também retorna a chave.
- **[HIGH] Dados sensíveis nas respostas:** `models.py:83-84` e `98-99` serializam o campo `senha`.
- **[HIGH] God Module/God Controller:** `controllers.py:1-292` e `models.py` misturam HTTP, validação, regras, SQL, serialização, notificações e erros.
- **[HIGH] Conexão global mutável:** `database.py:4-10` usa `global db_connection` e `check_same_thread=False`, dificultando concorrência e testes.
- **[HIGH] Pedido sem transação clara:** `models.py:133-168` executa pedido, itens e estoque sem unidade atômica/rollback garantido.
- **[MEDIUM] Queries N+1:** `models.py:174-224` consulta itens por pedido e produtos por item; usar joins ou agrupamento.
- **[MEDIUM] Validação duplicada:** `controllers.py:24-55` e `64-92` repetem regras de produto.
- **[MEDIUM] Exceções genéricas/erro interno exposto:** `controllers.py:10-12`, `60-62` e `app.py:77-78` retornam `str(e)`.
- **[MEDIUM] Debug e diagnóstico excessivo:** `app.py:8`, `app.py:88` e `controllers.py:285-289` deixam debug ativo e expõem infraestrutura.
- **[LOW] Magic values:** categorias, status e versões espalhados em `controllers.py:52`, `242` e `app.py:35-44`.
- **[LOW] Logging inadequado:** `controllers.py:8`, `57`, `106` e `208-210` usam `print` em vez de logging estruturado.
- **[LOW] Serialização duplicada:** `models.py:1-350` monta respostas diretamente em várias funções.

### Projeto 2 — `ecommerce-api-legacy`

Stack: Node.js + Express + SQLite. Domínio: LMS com usuários, cursos, matrículas, pagamentos e relatório financeiro. Arquitetura: `AppManager` concentra praticamente toda a aplicação.

- **[CRITICAL] Segredos hardcoded:** `src/utils.js:1-6` contém credenciais de banco, senha, gateway de pagamento e SMTP.
- **[CRITICAL] Dados de cartão em logs:** `src/AppManager.js:45` registra cartão e chave do gateway.
- **[HIGH] Criptografia inadequada:** `src/utils.js:17-23` usa Base64 repetido como se fosse hash; deve usar bcrypt, scrypt ou Argon2.
- **[HIGH] God Class:** `src/AppManager.js:4-141` cria banco, seed, rotas, validação, checkout, pagamentos, relatórios e exclusões.
- **[HIGH] Checkout sem transação:** `src/AppManager.js:50-63` grava matrícula, pagamento e auditoria separadamente, sem rollback.
- **[MEDIUM] N+1 no relatório:** `src/AppManager.js:80-127` busca cursos, matrículas, usuários e pagamentos em cascata.
- **[MEDIUM] Erros de banco inconsistentes:** `src/AppManager.js:37-42`, `50-61` e `131-136` tratam parcialmente ou ignoram falhas.
- **[MEDIUM] Exclusão deixa dados órfãos:** `src/AppManager.js:131-136` remove usuário sem tratar matrículas e pagamentos.
- **[LOW] Estado global mutável:** `src/utils.js:9-10` mantém cache e receita globalmente.
- **[LOW] Seed com senha fraca:** `src/AppManager.js:18-21` cria usuário com senha `'123'`.
- **[LOW] Payload pouco expressivo:** `src/AppManager.js:28-35` usa `usr`, `eml`, `pwd` e `c_id`.
- **[LOW] Callback nesting:** `src/AppManager.js:37-127` aninha callbacks de todo o fluxo.

### Projeto 3 — `task-manager-api`

Stack: Python + Flask + Flask-SQLAlchemy. Domínio: tarefas, usuários, categorias, prioridades, status e relatórios. Arquitetura: parcialmente organizada, mas com regras de negócio dentro das rotas.

- **[CRITICAL] Hashing inseguro com MD5:** `models/user.py:27-32` usa `hashlib.md5` para senhas.
- **[CRITICAL] Hash de senha na resposta:** `models/user.py:16-21` inclui `password` em `to_dict()`.
- **[CRITICAL] Credencial SMTP hardcoded:** `services/notification_service.py:7-10` fixa usuário e senha de e-mail.
- **[HIGH] Token falso e previsível:** `routes/user_routes.py:207-210` gera `fake-jwt-token-<id>`.
- **[HIGH] Routes/controllers gordos:** `routes/task_routes.py`, `user_routes.py` e `report_routes.py` misturam HTTP, validação, persistência, regras e serialização.
- **[MEDIUM] API deprecated:** `user_routes.py:29`, `94`, `136`; `task_routes.py:42`, `67`, `117`, `158`; `report_routes.py:105` usam `Model.query.get(...)`; recomendar `db.session.get(...)` após validar a versão.
- **[MEDIUM] N+1 em tarefas:** `routes/task_routes.py:14-51` consulta usuário e categoria dentro de loop.
- **[MEDIUM] N+1 em relatórios:** `routes/report_routes.py:53-60` consulta tarefas separadamente para cada usuário.
- **[MEDIUM] Estatísticas carregam tudo:** `routes/task_routes.py:273-296` usa `Task.query.all()` para calcular atrasos em Python.
- **[MEDIUM] Exceções genéricas:** `task_routes.py:62`, `137`, `204`, `236` e `report_routes.py:186` usam `except:` sem tipo.
- **[MEDIUM] Política de senha fraca:** `user_routes.py:64-65` e `114-116` aceitam quatro caracteres.
- **[LOW] Serialização duplicada:** `user_routes.py:33-38` e `160-181` representam tarefas de formas diferentes.
- **[LOW] Imports mortos:** `app.py:7`, `user_routes.py:6`, `task_routes.py:7` e `utils/helpers.py:2-7` possuem imports desnecessários.
- **[LOW] Datas sem timezone explícito:** `models/task.py:15-16`, `task_routes.py:31`, `215` e `notification_service.py:35` usam `datetime.utcnow()` sem política timezone-aware.

### Resumo dos achados

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---:|---:|---:|---:|---:|
| `code-smells-project` | 2 | 4 | 4 | 3 | 13 |
| `ecommerce-api-legacy` | 2 | 3 | 3 | 4 | 12 |
| `task-manager-api` | 3 | 2 | 6 | 4 | 15 |

Os três projetos fornecem contextos complementares: o primeiro é um monólito, o segundo concentra responsabilidades em uma classe JavaScript e o terceiro já possui diretórios de camadas, mas ainda apresenta falhas de segurança, performance, APIs deprecated e regras de negócio dentro das rotas.

## Resultados

### Relatórios de auditoria

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Validação runtime |
|---|---|---:|---:|---:|---:|---|
| `code-smells-project` | Python + Flask + SQLite | 3 | 4 | 3 | 2 | Passou |
| `ecommerce-api-legacy` | Node.js + Express + SQLite | 2 | 3 | 3 | 4 | Passou |
| `task-manager-api` | Python + Flask + SQLAlchemy | 3 | 2 | 6 | 4 | Passou |

Relatórios completos:

- [Auditoria do Projeto 1](reports/audit-project-1.md)
- [Auditoria do Projeto 2](reports/audit-project-2.md)
- [Auditoria do Projeto 3](reports/audit-project-3.md)

### Comparação antes/depois

| Projeto | Antes | Depois |
|---|---|---|
| `code-smells-project` | Monólito com rotas, SQL, validação e regras misturados em quatro arquivos | `src/` com `config`, `database`, `models`, `controllers`, `views` e `middlewares`; queries parametrizadas e transação no pedido |
| `ecommerce-api-legacy` | `AppManager` concentrava banco, rotas, checkout, pagamentos e relatórios | `src/` separado em `config`, `database`, `models`, `services`, `controllers`, `routes` e `middlewares`; checkout transacional |
| `task-manager-api` | Camadas existentes, mas rotas concentravam regras e usavam APIs deprecated | Configuração e controllers adicionados; hashing seguro, respostas sem senha, token aleatório e `db.session.get` |

### Checklist de validação

#### Projeto 1 — `code-smells-project`

- [x] Python/Flask detectado corretamente
- [x] Domínio de e-commerce identificado
- [x] Arquivos e tabelas mapeados
- [x] Auditoria com mais de 5 findings e severidades ordenadas
- [x] Confirmação solicitada antes da Fase 3
- [x] Estrutura MVC criada
- [x] Configuração extraída
- [x] Queries parametrizadas
- [x] Error handling centralizado
- [x] `GET /health` retornou `200 OK`
- [x] `GET /produtos` retornou `200 OK`

#### Projeto 2 — `ecommerce-api-legacy`

- [x] Node.js/Express detectado corretamente
- [x] Domínio de LMS/checkout identificado
- [x] Auditoria com mais de 5 findings e severidades ordenadas
- [x] Confirmação solicitada antes da Fase 3
- [x] Estrutura MVC criada
- [x] Checkout separado em service
- [x] Transação e rollback implementados
- [x] `POST /api/checkout` retornou `200 OK`
- [x] `GET /api/admin/financial-report` retornou `200 OK`
- [x] `DELETE /api/users/2` retornou `200 OK`

#### Projeto 3 — `task-manager-api`

- [x] Python/Flask/SQLAlchemy detectado corretamente
- [x] Domínio de Task Manager identificado
- [x] Auditoria encontrou problemas mesmo com camadas existentes
- [x] Confirmação solicitada antes da Fase 3
- [x] Configuração extraída e controller criado
- [x] MD5 substituído por hashing seguro
- [x] Senhas removidas das respostas
- [x] APIs deprecated migradas
- [x] `GET /health` retornou `200 OK`
- [x] `GET /` retornou `200 OK`
- [x] `GET /tasks` retornou `200 OK`
- [x] `GET /users` retornou `200 OK`
- [x] `GET /reports/summary` retornou `200 OK`
- [x] `GET /categories` retornou `200 OK`

### Observações sobre a Skill

A Skill funcionou nas duas stacks porque as regras de análise foram baseadas em sinais semânticos e responsabilidades, não em nomes fixos de arquivos. No Flask, ela tratou tanto o monólito quanto o projeto parcialmente organizado. No Express, identificou a concentração de responsabilidades em uma classe e adaptou o alvo MVC para uma API JSON.

Durante a execução, a Skill preservou os contratos públicos sempre que possível e exigiu confirmação entre auditoria e refatoração. A validação final combinou compilação/sintaxe, boot da aplicação e chamadas reais aos endpoints.

### Logs de execução

Exemplos dos resultados obtidos:

```text
code-smells-project:
GET /health     -> 200 OK
GET /produtos   -> 200 OK

ecommerce-api-legacy:
POST /api/checkout              -> 200 OK
GET /api/admin/financial-report -> 200 OK
DELETE /api/users/2             -> 200 OK

task-manager-api:
GET /health           -> 200 OK
GET /                 -> 200 OK
GET /tasks            -> 200 OK
GET /users            -> 200 OK
GET /reports/summary  -> 200 OK
GET /categories       -> 200 OK
```

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

No Codex, em cada projeto, utilizar a instrução:

```text
Leia e execute a Skill em .codex/skills/refactor-arch/SKILL.md neste projeto.
Siga obrigatoriamente as três fases, pare para confirmação ao final da Fase 2
e só prossiga para a Fase 3 depois da minha confirmação.
```

Ordem de execução:

```text
1. code-smells-project
2. ecommerce-api-legacy
3. task-manager-api
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.
