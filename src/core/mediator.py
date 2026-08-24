"""Behavioral Mediator pattern decoupling Hero and Enemy combat interactions and collisions."""

from typing import List, TYPE_CHECKING
from src.utils import settings

if TYPE_CHECKING:
    from src.entities.hero import Hero
    from src.entities.enemy import Enemy
    from src.entities.entity import Entity


class CombatMediator:
    """Mediator coordinating AABB collision checks, damage propagation, knockback, and blocking."""

    def __init__(self, hero: 'Hero') -> None:
        self._hero: 'Hero' = hero

    def update(self, enemies: List['Entity']) -> None:
        """Processes offensive hitboxes against target hurtboxes for all combatants."""
        # 1. Hero attacking Enemies
        hitbox = self._hero.get_hitbox()
        if hitbox:
            for enemy in enemies:
                if enemy.hp > 0 and hitbox.colliderect(enemy.hurtbox):
                    enemy.take_damage(self._hero.attack_damage)
                    direction = 1 if self._hero.rect.centerx < enemy.rect.centerx else -1
                    enemy.apply_knockback(direction, settings.KNOCKBACK_FORCE)
                    self._hero.register_hit()
                    break  # Single target hit per swing

        # 2. Enemies attacking Hero
        for enemy in enemies:
            if enemy.hp > 0 and self._hero.hp > 0:
                enemy_hitbox = enemy.get_hitbox()
                if enemy_hitbox and enemy_hitbox.colliderect(self._hero.hurtbox):
                    if self._hero.can_block(enemy.rect.centerx):
                        self._hero.block_hit()
                    else:
                        self._hero.take_damage(enemy.attack_damage)
                    enemy.register_hit()
