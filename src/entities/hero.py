import pygame
from src.entities.entity import Entity
from src.utils.asset_loader import AssetLoader
from src.utils import settings

class Hero(Entity):
    def __init__(self, name: str, x: float, y: float, speed: float = 0.0) -> None:
        self.idle_frames = AssetLoader.load_spritesheet('sprites/hero/Idle.png', 128, 128)
        self.walk_frames = AssetLoader.load_spritesheet('sprites/hero/Walk.png', 128, 128)
        self.attack1_frames = AssetLoader.load_spritesheet('sprites/hero/Attack 1.png', 128, 128)
        self.attack2_frames = AssetLoader.load_spritesheet('sprites/hero/Attack 2.png', 128, 128)
        self.defend_frames = AssetLoader.load_spritesheet('sprites/hero/Defend.png', 128, 128)
        self.hurt_frames = AssetLoader.load_spritesheet('sprites/hero/Hurt.png', 128, 128)
        self.dead_frames = AssetLoader.load_spritesheet('sprites/hero/Dead.png', 128, 128)
        self.jump_frames = AssetLoader.load_spritesheet('sprites/hero/Jump.png', 128, 128)
        self.run_frames = AssetLoader.load_spritesheet('sprites/hero/Run.png', 128, 128)
        self.run_attack_frames = AssetLoader.load_spritesheet('sprites/hero/Run+Attack.png', 128, 128)
        
        self.sfx_attack = AssetLoader.load_sound('audio/Attack-Sword-Hero.mp3')
        self.sfx_death = AssetLoader.load_sound('audio/Death-hero.mp3')
        self.sfx_defend = AssetLoader.load_sound('audio/Defend-Hero.mp3')
        
        self._state: str = 'idle'
        self._attack_type: int = 1
        
        super().__init__(name, self.idle_frames[0], x, y, speed)
        self._rect.midbottom = (round(x), round(y))
        self.hurtbox = pygame.Rect(0, 0, 30, 50)
        self._attack_hit: bool = False
        
        self.is_defending: bool = False
        self.is_attacking: bool = False
        self.is_running: bool = False
        self.facing_right: bool = True
        
        self._current_frame: float = 0.0
        self._animation_speed: float = 10.0
        self._gravity: float = 800.0
        self._jump_force: float = -400.0
        self._dt: float = 0.0
        
    def take_damage(self, amount: int) -> None:
        super().take_damage(amount)
        if self._hp > 0:
            self._state = 'hurt'
            self._current_frame = 0.0
            self.is_attacking = False
            self.is_defending = False

    def update(self, dt: float) -> None:
        self._dt = dt
        keys = pygame.key.get_pressed()
        
        mouse = pygame.mouse.get_pressed()
        
        if self._hp <= 0:
            self._vel.x = 0
            self.is_attacking = False
            self.is_defending = False
            self.is_running = False
        else:
            is_locked = self._state in ['attack1', 'attack2', 'run_attack', 'hurt']
            if not is_locked:
                self.is_attacking = mouse[0] or mouse[2]
                if mouse[0]:
                    self._attack_type = 1
                elif mouse[2]:
                    self._attack_type = 2
            self.is_defending = keys[pygame.K_c]
            self.is_running = keys[pygame.K_LSHIFT]
            
            if self._state == 'hurt':
                self._vel.x = 0
            else:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self._vel.x = -1.5 if self.is_running else -1
                    self.facing_right = False
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self._vel.x = 1.5 if self.is_running else 1
                    self.facing_right = True
                else:
                    self._vel.x = 0
            
        self._vel.y += self._gravity * dt
        
        if self._hp > 0 and keys[pygame.K_SPACE] and self._pos.y >= settings.FLOOR_HEIGHT:
            self._vel.y = self._jump_force
            
        self._pos.x += self._vel.x * self._speed * dt
        self._pos.y += self._vel.y * dt
        
        # Aplicação do piso provisório
        if self._pos.y >= settings.FLOOR_HEIGHT:
            self._pos.y = settings.FLOOR_HEIGHT
            self._vel.y = 0
            
        self._rect.midbottom = (round(self._pos.x), round(self._pos.y))
        self.hurtbox.midbottom = self._rect.midbottom
        
        if self._rect.left < -30:
            self._rect.left = -30
            self._pos.x = self._rect.midbottom[0]
        elif self._rect.right > settings.SCREEN_WIDTH + 30:
            self._rect.right = settings.SCREEN_WIDTH + 30
            self._pos.x = self._rect.midbottom[0]

    def draw(self, window: pygame.Surface) -> None:
        # Máquina de Estados Finita (FSM) com prioridade hierárquica e Animation Lock.
        new_state = 'idle'
        if self._hp <= 0:
            new_state = 'dead'
        elif self.is_defending:
            new_state = 'defend'
        elif self.is_attacking and self._vel.x != 0:
            new_state = 'run_attack'
        elif self.is_attacking and self._attack_type == 1:
            new_state = 'attack1'
        elif self.is_attacking and self._attack_type == 2:
            new_state = 'attack2'
        elif self._pos.y < settings.FLOOR_HEIGHT:
            new_state = 'jump'
        elif self._vel.x != 0:
            new_state = 'run' if self.is_running else 'walk'
            
        state_map = {
            'idle': self.idle_frames,
            'run': self.run_frames,
            'walk': self.walk_frames,
            'jump': self.jump_frames,
            'attack1': self.attack1_frames,
            'attack2': self.attack2_frames,
            'run_attack': self.run_attack_frames,
            'defend': self.defend_frames,
            'dead': self.dead_frames,
            'hurt': self.hurt_frames
        }
            
        is_locked = self._state in ['attack1', 'attack2', 'run_attack', 'hurt']
        current_list = state_map[self._state]
        animation_finished = self._current_frame >= len(current_list) - 1
        
        if is_locked and not animation_finished:
            new_state = self._state # Força a manutenção do estado
        elif is_locked and animation_finished:
            self.is_attacking = False # Libera a trava quando terminar
            
        if new_state != self._state:
            # Se estava atacando e vai mudar de estado, corta o som imediatamente
            if self._state in ['attack1', 'attack2', 'run_attack']:
                self.sfx_attack.stop()

            self._current_frame = 0.0
            self._state = new_state
            self._attack_hit = False
            
            # Se o novo estado for um ataque, inicia o som
            if new_state in ['attack1', 'attack2', 'run_attack']:
                self.sfx_attack.play()
            elif new_state == 'dead':
                self.sfx_death.play()
        
        current_list = state_map[self._state]
        
        
        self._current_frame += self._animation_speed * self._dt
        if self._state == 'dead':
            if self._current_frame >= len(current_list) - 1:
                self._current_frame = len(current_list) - 1.0 # Trava o corpo no chão
        else:
            self._current_frame %= len(current_list) # Executa loop para as demais
        
        current_image = current_list[int(self._current_frame)]
        
        # Lógica de inversão de sprites
        if not self.facing_right:
            current_image = pygame.transform.flip(current_image, True, False)
            
        window.blit(current_image, self._rect)

    def get_hitbox(self) -> pygame.Rect | None:
        if self._state in ['attack1', 'attack2', 'run_attack'] and not self._attack_hit:
            current_list = self.attack1_frames
            # Gera a hitbox apenas nos quadros finais da animação (o corte da espada)
            if self._current_frame >= len(current_list) - 2:
                if self.facing_right:
                    return pygame.Rect(self.hurtbox.right, self.hurtbox.centery - 20, 40, 40)
                else:
                    return pygame.Rect(self.hurtbox.left - 40, self.hurtbox.centery - 20, 40, 40)
        return None

    def register_hit(self) -> None:
        self._attack_hit = True
        
    def block_hit(self) -> None:
        self.sfx_defend.play()
