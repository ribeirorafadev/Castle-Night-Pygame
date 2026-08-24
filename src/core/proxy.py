"""Level progress proxy module for Castle Night.

Implements the Proxy design pattern to encapsulate wave progression,
spawn calculations, enemy kill tracking, and boss transition logic.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from src.utils import settings
from src.entities.factory import EntityFactory

if TYPE_CHECKING:
    from src.entities.entity import Entity
    from src.entities.hero import Hero


class LevelProgressProxy:
    """Proxy responsible for tracking level progression, wave spawning, and boss lifecycle."""

    def __init__(
        self,
        factory: type[EntityFactory] | EntityFactory = EntityFactory,
        total_wave_enemies: int | None = None,
    ) -> None:
        self._factory = factory
        self._total_enemies: int = (
            total_wave_enemies
            if total_wave_enemies is not None
            else getattr(settings, "MAX_REGULAR_ENEMIES", 20)
        )
        self._enemies_killed: int = 0
        self._boss_spawned: bool = False
        self._boss_defeated: bool = False

    @property
    def total_enemies(self) -> int:
        """Total regular enemies required to trigger the boss fight."""
        return self._total_enemies

    @property
    def enemies_remaining(self) -> int:
        """Number of regular enemies remaining before the boss spawns."""
        return max(0, self._total_enemies - self._enemies_killed)

    @property
    def defeated_count(self) -> int:
        """Total number of regular enemies defeated so far."""
        return self._enemies_killed

    @property
    def boss_spawned(self) -> bool:
        """Whether the DragonBoss has been spawned."""
        return self._boss_spawned

    @boss_spawned.setter
    def boss_spawned(self, value: bool) -> None:
        self._boss_spawned = value

    @property
    def boss_defeated(self) -> bool:
        """Whether the DragonBoss has been defeated."""
        return self._boss_defeated

    @boss_defeated.setter
    def boss_defeated(self, value: bool) -> None:
        self._boss_defeated = value

    @property
    def should_spawn_boss(self) -> bool:
        """Check if all regular enemies are defeated and the boss is not yet spawned."""
        return self._enemies_killed >= self._total_enemies and not self._boss_spawned

    @property
    def is_victory(self) -> bool:
        """Check if the victory condition is met (boss is defeated)."""
        return self._boss_defeated

    def register_kill(self, entity_or_name: Any) -> None:
        """Register an enemy kill, advancing the horde progress or triggering victory."""
        if isinstance(entity_or_name, str):
            if entity_or_name in ("DragonBoss", "boss-dragon"):
                self._boss_defeated = True
            else:
                self._enemies_killed += 1
        else:
            is_boss = getattr(entity_or_name, "is_boss", False)
            name = getattr(entity_or_name, "name", "") or getattr(entity_or_name, "_name", "")
            if is_boss or name in ("DragonBoss", "boss-dragon"):
                self._boss_defeated = True
            else:
                self._enemies_killed += 1

    def request_spawn(
        self,
        hero: Hero | Entity,
        active_enemies: list[Entity] | None = None,
    ) -> list[Entity]:
        """Request the next wave of enemies or the boss based on current progression."""
        if self.should_spawn_boss:
            floor_y = getattr(settings, "FLOOR_HEIGHT", 450.0)
            screen_w = getattr(settings, "SCREEN_WIDTH", 800)
            boss = self._factory.create_enemy(
                "boss-dragon",
                float(screen_w + 50.0),
                float(floor_y),
            )
            boss.set_target(hero)
            self._boss_spawned = True
            return [boss]

        if self._boss_spawned or self.enemies_remaining <= 0:
            return []

        defeated = self.defeated_count
        if defeated < 6:
            num_right = 1
            num_left = 1
        elif defeated < 15:
            num_right = 2
            num_left = 1
        else:
            num_right = 2
            num_left = 3

        total_to_spawn = min(num_right + num_left, self.enemies_remaining)
        spawn_sides = (["right"] * num_right + ["left"] * num_left)[:total_to_spawn]

        enemy_types = ["minotaur", "wizard", "skeleton", "werewolf", "yokai"]
        floor_y = getattr(settings, "FLOOR_HEIGHT", 450.0)
        screen_w = getattr(settings, "SCREEN_WIDTH", 800)

        spawned: list[Entity] = []
        for side in spawn_sides:
            enemy_type = random.choice(enemy_types)
            if side == "right":
                spawn_x = screen_w + 50.0 + random.uniform(0, 80)
            else:
                spawn_x = -50.0 - random.uniform(0, 80)

            enemy = self._factory.create_enemy(enemy_type, spawn_x, float(floor_y))
            enemy.set_target(hero)
            spawned.append(enemy)

        return spawned
