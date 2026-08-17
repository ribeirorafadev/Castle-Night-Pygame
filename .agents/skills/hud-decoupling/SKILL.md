---
name: hud-decoupling
description: Use quando for projetar, renderizar ou atualizar elementos de interface visual (barras de vida, medidores do boss, contadores de ondas/FPS, overlays de controles) isolados da lógica de estado.
---

# Desacoplameto de HUD & UI

## Visão Geral
Diretrizes para isolar a renderização da interface de usuário (UI), barras de vida, sombras de texto (drop shadows) e overlays em glassmorphism da lógica de estado do jogo.

## Princípios
1. **Zero Overhead na Coleta de Lixo (GC):** NÃO defina funções auxiliares dentro do método `run()` a 60 FPS. Instancie fontes ou métodos auxiliares UMA VEZ dentro da classe `HUDManager`.
2. **Funções de Renderização Puras:** O método `HUDManager.draw(window, hero, boss, proxy)` recebe dados e desenha na superfície da janela sem alterar o estado do jogo.
3. **Glassmorphism e Sombras:** Desenhe sombras projetadas renderizando superfícies de texto pretas com offset `(x+2, y+2)` antes de renderizar o texto colorido principal.

## Contrato de Componente
```python
class HUDManager:
    def __init__(self) -> None:
        self._font_main = pygame.font.Font(None, 28)
        self._font_title = pygame.font.Font(None, 72)

    def draw_player_hp(self, surface: pygame.Surface, hp: int, max_hp: int) -> None:
        # Renderiza barra de cor dinâmica (Verde -> Laranja -> Vermelho Piscante)
        ...

    def draw_boss_bar(self, surface: pygame.Surface, boss: Entity) -> None:
        # Renderiza barra de vida centralizada do chefe
        ...

    def draw_game_over(self, surface: pygame.Surface, alpha: float) -> None:
        # Renderiza overlay YOU DIED com fade de transparência alpha
        ...
```
