import os
import sys

# Adiciona o diretório raiz ao sys.path para garantir importações a partir de 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.game import Game
from src.utils import settings


def main() -> None:
    game = Game(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    game.run()


if __name__ == "__main__":
    main()
