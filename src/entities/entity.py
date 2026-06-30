from abc import ABC, abstractmethod
import pygame
from pygame.math import Vector2

class Entity(ABC):
    """Classe Base Abstrata (ABC) que define a superclasse do domínio. Aplica encapsulamento e injeção de dependência espacial."""
    
    def __init__(self, name: str, surf: pygame.Surface, x: float, y: float, speed: float = 0.0) -> None:
        self._name: str = name
        self._surf: pygame.Surface = surf
        # get_rect recebe coordenadas inteiras devido ao arredondamento subjacente do Pygame
        self._rect: pygame.Rect = self._surf.get_rect(topleft=(round(x), round(y)))
        self.hurtbox: pygame.Rect = pygame.Rect(0, 0, 30, 50)
        
        # Controle Vetorial Contínuo para impedir a falha de precisão de int vs float
        self._pos = pygame.math.Vector2(x, y)
        self._vel = pygame.math.Vector2(0, 0)
        
        self.max_hp: int = 100
        self.attack_damage: int = 5
        self._hp: int = self.max_hp
        self._is_dead: bool = False
        self._speed: float = speed
        self._target = None

    def set_target(self, target: 'Entity') -> None:
        self._target = target

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = value

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    @property
    def rect(self) -> pygame.Rect:
        """Acesso Read-Only da Bounding Box para detecções AABB no CombatMediator."""
        return self._rect

    @abstractmethod
    def update(self, dt: float) -> None:
        """Delega a lógica de movimentação vetorial e estados à classe filha."""
        pass

    @abstractmethod
    def draw(self, window: pygame.Surface) -> None:
        """Delega a lógica de desenho (`blit`) para a classe filha."""
        pass

    @abstractmethod
    def get_hitbox(self) -> pygame.Rect | None:
        """Contrato para retorno da matriz de colisão ofensiva."""
        pass

    @abstractmethod
    def register_hit(self) -> None:
        """Contrato de callback disparado pelo Mediator ao confirmar acerto."""
        pass
