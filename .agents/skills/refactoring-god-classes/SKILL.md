---
name: refactoring-god-classes
description: Use quando for refatorar classes monolíticas (como LevelState ou subclasses de Entity que excedam 200 linhas de código) em componentes desacoplados de Responsabilidade Única sem quebrar os contratos do game loop.
---

# Refatoração de God Classes

## Visão Geral
Diretrizes para identificar e refatorar classes monolíticas ("God Classes") que acumulam múltiplas responsabilidades, violando o SRP (Princípio da Responsabilidade Única).

## Sintomas de uma God Class
- A classe excede 200–300 linhas de código.
- Gerencia transições de estado, carregamento de assets, leitura de inputs, física E renderização de UI simultaneamente.
- Contém funções auxiliares aninhadas dentro de seus métodos de loop (ex.: funções definidas dentro de `run()`).

## Receita de Refatoração
1. **Extrair UI/HUD:** Mova todo o `blit` de texto, barras de vida, overlays e contadores de FPS para o `HUDManager`.
2. **Extrair Progresso/Spawns:** Mova a contagem de ondas, posições de spawn e gatilhos de boss para o `LevelProgressProxy`.
3. **Extrair Componentes:** Mova gravidade/cinemática para o `PhysicsComponent` e loops de quadros para o `AnimationComponent`.
4. **Método de Loop Limpo:** Garanta que o método principal `run(dt)` contenha apenas chamadas de orquestração de alto nível:
   ```python
   def run(self, dt: float) -> None:
       self._handle_events()
       self.hero.update(dt)
       self.wave_manager.update(dt)
       self.mediator.update(self.enemies)
       self.hud.draw(self._window, self.hero, self.wave_manager)
   ```
