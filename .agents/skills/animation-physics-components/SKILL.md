---
name: animation-physics-components
description: Use quando for implementar cinemática de movimento, cálculo de gravidade, avanço de frames de animação e atualização de hitbox/hurtbox via composição em vez de poluir subclasses de Entity.
---

# Componentes de Animação & Física (Composição sobre Herança)

## Visão Geral
Diretrizes para extração de componentes reutilizáveis para física de movimento, integração de gravidade e avanço de animação de sprites para fora das subclasses `Hero` e `Enemy`.

## 1. `PhysicsComponent`
Encapsula cinemática vetorial 2D, aceleração por gravidade e limites de piso/parede.

```python
class PhysicsComponent:
    def __init__(self, pos: Vector2, speed: float, gravity: float = 800.0) -> None:
        self.pos = pos
        self.vel = Vector2(0, 0)
        self.speed = speed
        self.gravity = gravity

    def update(self, dt: float, floor_y: float) -> None:
        self.vel.y += self.gravity * dt
        self.pos.x += self.vel.x * self.speed * dt
        self.pos.y += self.vel.y * dt
        
        if self.pos.y >= floor_y:
            self.pos.y = floor_y
            self.vel.y = 0.0
```

## 2. `AnimationComponent`
Encapsula incremento de quadros, módulo de ciclo, alternância de dicionário de animações e espelhamento horizontal.

```python
class AnimationComponent:
    def __init__(self, animations: dict[str, list[pygame.Surface]], speed: float = 10.0) -> None:
        self._animations = animations
        self._current_frame: float = 0.0
        self._speed = speed

    def get_current_sprite(self, state: str, dt: float, facing_right: bool) -> pygame.Surface:
        frames = self._animations[state]
        self._current_frame += self._speed * dt
        img = frames[int(self._current_frame) % len(frames)]
        if not facing_right:
            img = pygame.transform.flip(img, True, False)
        return img
```
