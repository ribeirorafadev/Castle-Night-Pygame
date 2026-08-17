---
name: level-progress-proxy
description: Use quando for implementar ou modificar a progressão de spawn de inimigos, rastreamento de ondas, gatilhos de aparição do boss e condições de vitória/derrota através do padrão Proxy (src/core/proxy.py).
---

# Padrão Proxy de Progresso de Nível

## Visão Geral
Guia do padrão para desacoplar mecânicas de ondas, rastreamento de baixas, distribuição de spawns e progressão para o boss da classe `LevelState`.

## Responsabilidades do `LevelProgressProxy`
- **Rastreamento de Baixas:** Incrementa a contagem de baixas quando inimigos são marcados como `is_removable`.
- **Spawn de Ondas:** Calcula lados de surgimento (esquerda/direita) e seleciona tipos de inimigos da `EntityFactory`.
- **Gatilho de Boss:** Dispara a aparição do `DragonBoss` assim que 20 inimigos comuns forem eliminados.
- **Condição de Vitória:** Avalia se o HP do `DragonBoss` chega a 0.

## Contrato de Implementação
```python
class LevelProgressProxy:
    def __init__(self, factory: EntityFactory) -> None:
        self._enemies_killed: int = 0
        self._max_regular_enemies: int = 20
        self._boss_spawned: bool = False
        self._boss_defeated: bool = False

    def register_kill(self, entity_name: str) -> None:
        if entity_name != 'DragonBoss':
            self._enemies_killed += 1

    @property
    def should_spawn_boss(self) -> bool:
        return self._enemies_killed >= self._max_regular_enemies and not self._boss_spawned

    @property
    def is_victory(self) -> bool:
        return self._boss_defeated
```
