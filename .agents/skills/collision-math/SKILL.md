---
name: collision-math
description: Use quando for implementar cinemática vetorial, normalização de velocidade diagonal, arredondamento float para int ou resolução de combate hitbox/hurtbox AABB em entidades ou no CombatMediator.
---

# Matemática de Colisão & Cinemática Vetorial

## Visão Geral
Diretrizes e fórmulas matemáticas para transformações espaciais 2D de alta precisão e resolução de intersecção AABB (Axis-Aligned Bounding Box) no Pygame.

## 1. Cinemática Vetorial & Rastreamento de Posição
Sempre utilize `pygame.math.Vector2` com rastreamento em ponto flutuante (float) para evitar erros de arredondamento de sub-pixels.

```python
# 1. Atualiza vetor de velocidade
self._vel.y += GRAVITY * dt
self._pos += self._vel * dt

# 2. Sincroniza o Rect de renderização do Pygame
self._rect.midbottom = (round(self._pos.x), round(self._pos.y))
```

## 2. Normalização de Velocidade Diagonal
Ao se mover em dois eixos simultaneamente (ex.: movimento diagonal WASD), sempre normalize vetores não-nulos para prevenir anomalias de velocidade ($\sqrt{2} \approx 1,414$ de multiplicador):

```python
if direction.length_squared() > 0:
    direction = direction.normalize()
velocity = direction * speed
```

## 3. Resolução de Combate AABB (`CombatMediator`)
- **Hurtbox:** Caixa de colisão vulnerável (persiste com a entidade).
- **Hitbox:** Janela ofensiva transitória (ativa apenas em quadros específicos de animação de ataque).
- **Encapsulamento:** Nunca altere `_pos.x` diretamente dentro do Mediator. Invoque `defender.apply_knockback(direction, force)` em seu lugar.

```python
if attacker_hitbox and attacker_hitbox.colliderect(defender.hurtbox):
    defender.take_damage(attacker.attack_damage)
    direction = 1 if attacker.rect.centerx < defender.rect.centerx else -1
    defender.apply_knockback(direction, force=20.0)
```
