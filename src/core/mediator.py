from typing import List, TYPE_CHECKING
from src.entities.hero import Hero

if TYPE_CHECKING:
    from src.entities.enemy import Enemy

class CombatMediator:
    """Implementação do Padrão de Projeto Comportamental 'Mediator'. Desacopla as classes Hero e Enemy, centralizando a lógica matemática de colisão AABB (Axis-Aligned Bounding Box) em um juiz neutro (Single Responsibility Principle)."""
    def __init__(self, hero: Hero) -> None:
        self._hero = hero

    def update(self, enemies: List['Enemy']) -> None:
        hitbox = self._hero.get_hitbox()
        if hitbox:
            for enemy in enemies:
                if enemy.hp > 0 and hitbox.colliderect(enemy.hurtbox):
                    enemy.take_damage(25)
                    # Knockback (Stagger push)
                    direction = 1 if self._hero.rect.centerx < enemy.rect.centerx else -1
                    enemy._pos.x += direction * 20
                    self._hero.register_hit()
                    break  # Atinge apenas um inimigo por swing de espada

        for enemy in enemies:
            if enemy.hp > 0 and self._hero.hp > 0:
                enemy_hitbox = enemy.get_hitbox()
                if enemy_hitbox and enemy_hitbox.colliderect(self._hero.hurtbox):
                    # Verifica se o herói está defendendo e virado para o atacante
                    is_facing_enemy = (self._hero.rect.centerx < enemy.rect.centerx and self._hero.facing_right) or \
                                      (self._hero.rect.centerx > enemy.rect.centerx and not self._hero.facing_right)
                    
                    if self._hero.is_defending and is_facing_enemy:
                        self._hero.block_hit()
                    else:
                        self._hero.take_damage(enemy.attack_damage)
                        
                    enemy.register_hit()
