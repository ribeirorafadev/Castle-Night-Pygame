"""Reusable entity components for physics and animation in Castle Night."""

import pygame
from pygame.math import Vector2
from src.utils import settings


class PhysicsComponent:
    """Component handling spatial kinematics, gravity, floor collision, and knockback."""

    def __init__(
        self,
        x: float,
        y: float,
        speed: float = 0.0,
        gravity: float = settings.GRAVITY,
        floor_y: float = settings.FLOOR_HEIGHT,
    ) -> None:
        self.pos: Vector2 = Vector2(x, y)
        self.vel: Vector2 = Vector2(0.0, 0.0)
        self.speed: float = speed
        self.gravity: float = gravity
        self.floor_y: float = floor_y

    @property
    def is_on_ground(self) -> bool:
        """Check if entity is at or below the floor plane."""
        return self.pos.y >= self.floor_y

    def update(self, dt: float) -> None:
        """Apply gravity and integrate continuous velocity into position."""
        self.vel.y += self.gravity * dt
        self.pos.x += self.vel.x * self.speed * dt
        self.pos.y += self.vel.y * dt

        if self.pos.y >= self.floor_y:
            self.pos.y = self.floor_y
            self.vel.y = 0.0

    def jump(self, force: float) -> None:
        """Apply an upward vertical impulse if currently on the ground."""
        if self.is_on_ground:
            self.vel.y = force

    def apply_knockback(self, direction: float | int, force: float = settings.KNOCKBACK_FORCE) -> None:
        """Apply horizontal displacement knockback."""
        self.pos.x += direction * force


class AnimationComponent:
    """Component managing sprite frame sequencing, playback speed, and animation state."""

    def __init__(
        self,
        animations: dict[str, list[pygame.Surface]],
        default_state: str = "idle",
        speed: float = 10.0,
    ) -> None:
        self.animations: dict[str, list[pygame.Surface]] = animations
        self._state: str = default_state
        self._current_frame: float = 0.0
        self.speed: float = speed
        self._is_finished: bool = False

    @property
    def state(self) -> str:
        """Current animation state key."""
        return self._state

    @property
    def current_frame(self) -> float:
        """Current sub-frame float index."""
        return self._current_frame

    @property
    def is_finished(self) -> bool:
        """Whether a non-looping animation has reached its final frame."""
        return self._is_finished

    def set_state(self, state: str, force_reset: bool = False) -> None:
        """Switch current animation state and reset the frame counter."""
        if state != self._state or force_reset:
            self._state = state
            self._current_frame = 0.0
            self._is_finished = False

    def update(self, dt: float, loop: bool = True) -> None:
        """Advance animation frames based on delta time."""
        frames = self.animations.get(self._state, [])
        if not frames:
            return

        self._current_frame += self.speed * dt
        if loop:
            self._current_frame %= len(frames)
            self._is_finished = False
        else:
            if self._current_frame >= len(frames) - 1:
                self._current_frame = float(len(frames) - 1)
                self._is_finished = True

    def get_current_image(self) -> pygame.Surface:
        """Retrieve the surface corresponding to the active frame."""
        frames = self.animations.get(self._state, [])
        if not frames:
            return pygame.Surface((0, 0))
        idx = int(self._current_frame)
        if 0 <= idx < len(frames):
            return frames[idx]
        return frames[0]
