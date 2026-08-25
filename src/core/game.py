"""Main Game orchestration class managing state transitions, windowing, and the primary loop."""

from __future__ import annotations

import pygame

from src.core.states import IState, MenuState
from src.utils import settings


class Game:
    """Core Game engine class managing pygame lifecycle, display surfaces, and state delegation.

    Attributes:
        window (pygame.Surface): The primary screen display surface.
    """

    def __init__(
        self,
        width: int = settings.SCREEN_WIDTH,
        height: int = settings.SCREEN_HEIGHT,
    ) -> None:
        """Initialize Pygame subsystems, audio mixer, display window, and initial state.

        Args:
            width: Horizontal resolution of the game window in pixels.
            height: Vertical resolution of the game window in pixels.
        """
        pygame.init()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            # Allocate 64 concurrent channels for multi-track combat SFX & ambiance
            pygame.mixer.set_num_channels(64)
        except Exception:
            # Mixer initialization failure in headless/soundless environment handled gracefully
            pass

        self.window: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(settings.TITLE)
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._running: bool = True

        self._current_state: IState = MenuState(self)

    @property
    def fps(self) -> float:
        """Current rendering frames per second.

        Returns:
            float: Running average FPS measured by the internal clock.
        """
        return self._clock.get_fps()

    def change_state(self, new_state: IState) -> None:
        """Transition to a new active state, freeing the previous state reference for garbage collection.

        Args:
            new_state: New IState concrete implementation to activate.
        """
        self._current_state = new_state

    def quit(self) -> None:
        """Signal the primary game loop to terminate gracefully."""
        self._running = False

    def run(self) -> None:
        """Execute the primary game loop at configured FPS with continuous delta time integration."""
        while self._running:
            # Fixed 60 FPS clock step: delta time measured in fractional seconds
            dt: float = self._clock.tick(settings.FPS) / 1000.0

            # Absolute delegation: active state orchestrates its own event polling, physics, and rendering
            self._current_state.run(dt)

            pygame.display.update()

        pygame.quit()

