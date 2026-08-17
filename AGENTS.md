# 🤖 AGENTS.md - Manifesto & Harness Agêntico do Projeto

> **Missão do Projeto:** Demo 2D Metroidvania em Pygame — Padrões de Engenharia de Software Acadêmicos e de Produção.

Bem-vindo ao **Castle Night**. Este arquivo define o manifesto operacional, os guardrails arquiteturais, os papéis dos subagentes e o índice de contexto para assistentes de IA agênticos que trabalham neste repositório.

---

## 🛠️ 1. Contexto do Projeto e Ambiente
- **Linguagem:** Python 3.12+ (PEP 8 estritamente aplicado).
- **Biblioteca Core:** Pygame 2.6+.
- **Domínio Acadêmico:** Bacharelado em Engenharia de Software (Uninter) — Clean Code, Princípios SOLID, Padrões de Projeto (Design Patterns).
- **Ponto de Entrada:** `run_game.py` (Script de entrada na raiz para execução do código-fonte e empacotamento PyInstaller).

---

## 🛡️ 2. Invariantes Arquiteturais (Guardrails Zero-Trust)

Todos os assistentes de IA agênticos que trabalham neste repositório DEVEM seguir estritamente estas regras:

1. **Princípio da Responsabilidade Única (SRP):**
   - Proibido "God Classes". `states.py`, `hero.py` e `enemy.py` devem permanecer focados.
   - Separe transições de estado, física, tomada de decisão de IA e lógica de renderização.
2. **Funções de Renderização Puras (`draw()`):**
   - O método `draw()` em qualquer entidade ou estado DEVE ser livre de efeitos colaterais.
   - NÃO toque áudio, NÃO atualize quadros de animação e NÃO altere o estado do jogo dentro de `draw()`.
3. **Encapsulamento & PEP 8:**
   - Membros privados/protegidos usam `_` ou `__`. Use `@property` para getters públicos.
   - Nunca altere campos privados de outra instância diretamente (ex.: use `enemy.apply_knockback()` em vez de `enemy._pos.x += 20`).
4. **Zero Números Mágicos (Magic Numbers):**
   - Todas as dimensões espaciais, constantes de gravidade, tamanhos de hurtbox e limites de timers DEVEM residir como constantes nomeadas em `src/utils/settings.py`.
5. **Resolução de Caminhos:**
   - Todos os arquivos estáticos (imagens, sons) DEVEM ser carregados via caminhos relativos usando `AssetLoader` para garantir compatibilidade com o PyInstaller.

---

## 👥 3. Matriz e Papéis de Subagentes

Ao trabalhar em tarefas complexas, delegue o trabalho para os subagentes especializados definidos em `.agents/subagents/`:

| Papel do Subagente | Arquivo de Perfil | Subsistema / Arquivos Alvo |
| :--- | :--- | :--- |
| **Game Architect** | `.agents/subagents/game-architect.md` | `src/core/game.py`, `src/core/states.py` |
| **Entity Engineer** | `.agents/subagents/entity-engineer.md` | `src/entities/*`, `src/core/mediator.py` |
| **HUD & UI Engineer** | `.agents/subagents/hud-ui-engineer.md` | `src/ui/*`, `src/core/states.py` (Overlays de UI) |
| **Build Specialist** | `.agents/subagents/build-specialist.md` | `run_game.py`, `requirements.txt`, `.agents/skills/build-pipeline/` |

---

## 📚 4. Índice do Harness (Navegação de Regras e Skills)

### Regras e Guardrails
- 📐 **[Regras de Estrutura do Projeto](.agents/rules/project-structure.md):** Regras de topologia estrita para a pasta `src/`.
- 🏛️ **[Regras SOLID do Pygame](.agents/rules/pygame-solid.md):** Diretrizes de encapsulamento, tipagem e SOLID.
- 🔄 **[Regras da Máquina de Estados](.agents/rules/state-machine.md):** Contrato `IState` e gerenciamento de ciclo de vida de memória.

### Skills Especializadas de Agentes (Padrão agentskills.io)
- ⚙️ **[Refatoração de God Classes](.agents/skills/refactoring-god-classes/SKILL.md):** Receitas para fatiar classes monolíticas (>200 LOC).
- 🛡️ **[Proxy de Progresso de Nível](.agents/skills/level-progress-proxy/SKILL.md):** Implementação do padrão Proxy para ondas e gatilho do Boss.
- 🎨 **[Desacoplamento de HUD](.agents/skills/hud-decoupling/SKILL.md):** Extração do `HUDManager` e isolamento da renderização a 60 FPS.
- 🏃 **[Componentes de Animação e Física](.agents/skills/animation-physics-components/SKILL.md):** Composição para cinemática e loops de animação.
- 📐 **[Matemática de Colisão](.agents/skills/collision-math/SKILL.md):** Cinemática vetorial, normalização e lógica AABB no Mediator.
- 📦 **[Pipeline de Build](.agents/skills/build-pipeline/SKILL.md):** Guia de empacotamento PyInstaller e implantação de executáveis.
