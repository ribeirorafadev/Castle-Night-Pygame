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
    """Proxy responsible for tracking level progression, wave spawning, and boss lifecycle.

    Encapsulates game difficulty scaling, enemy quota tracking, off-screen spawn positioning,
    and boss transition triggers without exposing internal state complexity to LevelState.
    """

    def __init__(
        self,
        factory: type[EntityFactory] | EntityFactory = EntityFactory,
        total_wave_enemies: int | None = None,
    ) -> None:
        """Initialize level progress proxy with entity factory and wave quota.

        Args:
            factory: Factory instance or class for instantiating characters.
            total_wave_enemies: Total regular enemy quota before boss trigger.
        """
        self._factory = factory
        self._total_enemies: int = (
            total_wave_enemies
            if total_wave_enemies is not None
            else settings.MAX_REGULAR_ENEMIES
        )
        self._enemies_killed: int = 0
        self._boss_spawned: bool = False
        self._boss_defeated: bool = False

    @property
    def total_enemies(self) -> int:
        """Total regular enemies required to trigger the boss fight.

        Returns:
            int: Required regular enemy count.
        """
        return self._total_enemies

    @property
    def enemies_remaining(self) -> int:
        """Number of regular enemies remaining before the boss spawns.

        Returns:
            int: Remaining enemy count clamped at 0.
        """
        return max(0, self._total_enemies - self._enemies_killed)

    @property
    def defeated_count(self) -> int:
        """Total number of regular enemies defeated so far.

        Returns:
            int: Number of defeated regular enemies.
        """
        return self._enemies_killed

    @property
    def boss_spawned(self) -> bool:
        """Whether the DragonBoss has been spawned.

        Returns:
            bool: True if boss has entered the arena, False otherwise.
        """
        return self._boss_spawned

    @boss_spawned.setter
    def boss_spawned(self, value: bool) -> None:
        """Set boss spawned state flag.

        Args:
            value: Boolean value for boss spawned status.
        """
        self._boss_spawned = value

    @property
    def boss_defeated(self) -> bool:
        """Whether the DragonBoss has been defeated.

        Returns:
            bool: True if boss HP is zero and registered, False otherwise.
        """
        return self._boss_defeated

    @boss_defeated.setter
    def boss_defeated(self, value: bool) -> None:
        """Set boss defeated state flag.

        Args:
            value: Boolean value for boss defeated status.
        """
        self._boss_defeated = value

    @property
    def should_spawn_boss(self) -> bool:
        """Check if all regular enemies are defeated and the boss is not yet spawned.

        Returns:
            bool: True if boss spawn condition is fulfilled, False otherwise.
        """
        return self._enemies_killed >= self._total_enemies and not self._boss_spawned

    @property
    def is_victory(self) -> bool:
        """Check if the victory condition is met (boss is defeated).

        Returns:
            bool: True if victory is achieved, False otherwise.
        """
        return self._boss_defeated

    def register_kill(self, entity_or_name: Any) -> None:
        """Register an enemy kill, advancing the horde progress or triggering victory.

        Args:
            entity_or_name: Entity instance or string identifier of defeated character.
        """
        if isinstance(entity_or_name, str):
            if entity_or_name in ("DragonBoss", "boss-dragon"):
                self._boss_defeated = True
            else:
                self._enemies_killed += 1
        else:
            is_boss = getattr(entity_or_name, "is_boss", False)
            name = getattr(entity_or_name, "name", "") or getattr(
                entity_or_name, "_name", ""
            )
            if is_boss or name in ("DragonBoss", "boss-dragon"):
                self._boss_defeated = True
            else:
                self._enemies_killed += 1

    def request_spawn(
        self,
        hero: Hero | Entity,
        active_enemies: list[Entity] | None = None,
    ) -> list[Entity]:
        """Request the next wave of enemies or the boss based on current progression.

        Args:
            hero: Player character entity to target.
            active_enemies: Optional list of currently alive enemies.

        Returns:
            list[Entity]: Newly instantiated and positioned enemy entities.
        """
        # Boss phase transition check
        if self.should_spawn_boss:
            floor_y = settings.FLOOR_HEIGHT
            screen_w = settings.SCREEN_WIDTH
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

        # Dynamic difficulty scaling based on defeated horde count
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
        floor_y = settings.FLOOR_HEIGHT
        screen_w = settings.SCREEN_WIDTH

        # Off-screen spawn generation
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

