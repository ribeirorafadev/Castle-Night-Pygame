"""Application entry point for Castle Night.

Initializes the runtime environment, configures the system path, and starts
the primary Game lifecycle loop with window parameters from settings.
"""

import os
import sys

# Ensure project root directory is on sys.path for absolute package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.game import Game
from src.utils import settings


def main() -> None:
    """Bootstrap and run the Castle Night game instance."""
    game = Game(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    game.run()


if __name__ == "__main__":
    main()
