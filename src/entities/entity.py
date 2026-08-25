"""Domain entity base class defining spatial, physical, and combat contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
import pygame
from pygame.math import Vector2
from src.utils import settings


class Entity(ABC):
    """Abstract Base Class (ABC) defining domain entity contracts, encapsulation, and spatial kinematics."""

    def __init__(self, name: str, surf: pygame.Surface, x: float, y: float, speed: float = 0.0) -> None:
        self._name: str = name
        self._surf: pygame.Surface = surf
        self._rect: pygame.Rect = self._surf.get_rect(midbottom=(round(x), round(y)))
        self.hurtbox: pygame.Rect = pygame.Rect(0, 0, 30, 50)
        self.hurtbox.midbottom = self._rect.midbottom

        self._pos: Vector2 = Vector2(x, y)
        self._vel: Vector2 = Vector2(0.0, 0.0)

        self.max_hp: int = settings.ENEMY_MAX_HP
        self.attack_damage: int = settings.ENEMY_ATTACK_DAMAGE
        self._hp: int = self.max_hp
        self._is_removable: bool = False
        self._speed: float = speed
        self._target: Optional[Entity] = None

    @property
    def name(self) -> str:
        """Read-only access to entity name."""
        return self._name

    @property
    def pos(self) -> Vector2:
        """Spatial position vector."""
        return self._pos

    @property
    def vel(self) -> Vector2:
        """Spatial velocity vector."""
        return self._vel

    @staticmethod
    def safe_normalize(vec: Vector2) -> Vector2:
        """Safely normalizes a 2D vector, preventing ZeroDivisionError when magnitude is 0."""
        if vec.length_squared() > 0.0:
            return vec.normalize()
        return Vector2(0.0, 0.0)

    @property
    def is_boss(self) -> bool:
        """Indicates whether this entity is classified as a boss."""
        return False

    @property
    def is_removable(self) -> bool:
        """Indicates whether entity is dead and ready for memory cleanup."""
        return self._is_removable

    @is_removable.setter
    def is_removable(self, value: bool) -> None:
        """Sets whether entity is ready for memory cleanup."""
        self._is_removable = value

    @property
    def hp(self) -> int:
        """Current hit points."""
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        """Setter for hit points, clamped at lower bound 0."""
        self._hp = max(0, value)

    def take_damage(self, amount: int) -> None:
        """Inflicts damage on the entity."""
        self.hp -= amount

    @property
    def rect(self) -> pygame.Rect:
        """Read-only access to the bounding box for AABB collision detection."""
        return self._rect

    def set_target(self, target: Entity) -> None:
        """Assigns combat target entity."""
        self._target = target

    def can_block(self, attacker_x: float) -> bool:
        """Determines whether incoming attack from attacker_x is blocked. Default is False."""
        return False

    def apply_knockback(self, direction: float | int, force: float = settings.KNOCKBACK_FORCE) -> None:
        """Applies horizontal displacement knockback and syncs bounding boxes."""
        self._pos.x += direction * force
        self._rect.midbottom = (round(self._pos.x), round(self._pos.y))
        self.hurtbox.midbottom = self._rect.midbottom

    @abstractmethod
    def update(self, dt: float) -> None:
        """Updates internal kinematics, timers, and state machine."""
        pass

    @abstractmethod
    def draw(self, window: pygame.Surface) -> None:
        """Pure render routine. Must not mutate state, advance timers, or play audio."""
        pass

    @abstractmethod
    def get_hitbox(self) -> Optional[pygame.Rect]:
        """Returns offensive collision rectangle if actively attacking, or None."""
        pass

    @abstractmethod
    def register_hit(self) -> None:
        """Callback invoked by CombatMediator when an attack connects."""
        pass
