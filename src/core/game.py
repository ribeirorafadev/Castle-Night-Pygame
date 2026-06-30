import pygame
from src.core.states import IState, MenuState


class Game:
    def __init__(self, width: int = 800, height: int = 600) -> None:
        pygame.init()
        pygame.mixer.set_num_channels(64)
        self.window: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Castle Night - Demo")
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._running: bool = True
        
        self._current_state: IState = MenuState(self)

    @property
    def fps(self) -> float:
        return self._clock.get_fps()

    def change_state(self, new_state: IState) -> None:
        # Delega ao novo estado, o estado antigo perde a referência e é coletado (GC)
        self._current_state = new_state

    def quit(self) -> None:
        self._running = False

    def run(self) -> None:
        while self._running:
            # Controla a taxa de quadros e obtém o delta time
            dt: float = self._clock.tick(60) / 1000.0
            
            # Delegação absoluta: cada estado controla seu próprio ciclo de renderização e eventos
            self._current_state.run(dt)
            
            pygame.display.update()
            
        pygame.quit()
