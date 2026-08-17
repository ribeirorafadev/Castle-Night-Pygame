# Rules: Topologia e Estrutura de Diretórios (project-structure.md)

## 1. Diretriz de Organização (Restrição Absoluta)
Você (Agente de IA) deve operar estritamente dentro da topologia de diretórios definida abaixo. É terminantemente proibido criar arquivos de código-fonte (`.py`) na raiz do projeto ou inventar novos diretórios fora do escopo de `src/` sem autorização explícita do usuário.

## 2. Mapa da Árvore do Projeto
Abaixo está a árvore oficial do repositório, incluindo o harness agêntico e a estrutura de módulos.

```text
Castle-Night-Pygame/
├── AGENTS.md                         # Manifesto Mestre do Harness (Raiz do Projeto)
├── .agents/                          # Diretório de Suporte Agêntico
│   ├── persona/
│   │   └── game-engineer.md          # Persona do agente e diretrizes master
│   ├── subagents/                    # Perfis de subagentes especialistas
│   │   ├── game-architect.md
│   │   ├── entity-engineer.md
│   │   ├── hud-ui-engineer.md
│   │   └── build-specialist.md
│   ├── rules/                        # Regras e guardrails inegociáveis
│   │   ├── project-structure.md
│   │   ├── pygame-solid.md
│   │   └── state-machine.md
│   └── skills/                       # Skills canônicas (agentskills.io)
│       ├── animation-physics-components/SKILL.md
│       ├── build-pipeline/SKILL.md
│       ├── collision-math/SKILL.md
│       ├── hud-decoupling/SKILL.md
│       ├── level-progress-proxy/SKILL.md
│       └── refactoring-god-classes/SKILL.md
├── src/                              # Código-fonte Python
│   ├── core/                         # Game engine, estados, mediator e proxy
│   ├── entities/                     # Entidades, fábrica e hierarquias
│   ├── ui/                           # HUDManager e overlays de UI
│   ├── utils/                        # Configurações e AssetLoader
│   └── main.py                       # Ponto único de entrada
├── assets/                           # Imagens e Sons
├── docs/                             # Documentação e guias
├── run_game.py                       # Ponto de ancoragem para PyInstaller
├── requirements.txt                  # Dependências do projeto
└── .gitignore                        # Arquivos ignorados pelo Git
```

## 3. Regras de Alocação de Código (`src/`)

| Diretório | Arquivos Permitidos | Responsabilidade Arquitetural |
| :--- | :--- | :--- |
| **`src/core/`** | `game.py`, `states.py`, `mediator.py`, `proxy.py` | Lógicas de controle central, Máquina de Estados, `CombatMediator` e `LevelProgressProxy`. |
| **`src/entities/`** | `entity.py`, `hero.py`, `enemy.py`, `factory.py` | Domínio do jogo: classes abstratas/concretas de entidades e a `EntityFactory`. |
| **`src/ui/`** | `hud.py` | Gerenciador de interface de usuário (`HUDManager`), overlays e texto. |
| **`src/utils/`** | `settings.py`, `asset_loader.py` | Constantes, valores de configuração e carregamento seguro de mídias. |
| **`src/` (Raiz)** | `main.py` | Instanciação e execução do objeto `Game`. |
