"""Hero entity representing player character with physics, combat mechanics, and animations."""

from typing import Optional, Dict, List
import pygame
from src.entities.entity import Entity
from src.utils.asset_loader import AssetLoader
from src.utils import settings


class Hero(Entity):
    """Player-controlled hero entity with combat actions, state management, and pure rendering."""

    def __init__(self, name: str, x: float, y: float, speed: float = settings.HERO_SPEED) -> None:
        self.idle_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Idle.png', 128, 128)
        self.walk_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Walk.png', 128, 128)
        self.attack1_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Attack 1.png', 128, 128)
        self.attack2_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Attack 2.png', 128, 128)
        self.defend_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Defend.png', 128, 128)
        self.hurt_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Hurt.png', 128, 128)
        self.dead_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Dead.png', 128, 128)
        self.jump_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Jump.png', 128, 128)
        self.run_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Run.png', 128, 128)
        self.run_attack_frames: List[pygame.Surface] = AssetLoader.load_spritesheet('sprites/hero/Run+Attack.png', 128, 128)

        self.sfx_attack = AssetLoader.load_sound('audio/Attack-Sword-Hero.mp3')
        self.sfx_death = AssetLoader.load_sound('audio/Death-hero.mp3')
        self.sfx_defend = AssetLoader.load_sound('audio/Defend-Hero.mp3')

        super().__init__(name, self.idle_frames[0], x, y, speed)
        self.max_hp: int = settings.HERO_MAX_HP
        self._hp: int = settings.HERO_MAX_HP
        self.attack_damage: int = settings.HERO_ATTACK_DAMAGE

        self._rect.midbottom = (round(x), round(y))
        self.hurtbox: pygame.Rect = pygame.Rect(0, 0, 30, 50)
        self.hurtbox.midbottom = self._rect.midbottom

        self._state: str = 'idle'
        self._attack_type: int = 1
        self._attack_hit: bool = False

        self.is_defending: bool = False
        self.is_attacking: bool = False
        self.is_running: bool = False
        self.facing_right: bool = True

        self._current_frame: float = 0.0
        self._animation_speed: float = settings.HERO_ANIMATION_SPEED
        self._gravity: float = settings.GRAVITY
        self._jump_force: float = settings.HERO_JUMP_FORCE

    def _get_state_map(self) -> Dict[str, List[pygame.Surface]]:
        """Mapping from state names to animation frame lists."""
        return {
            'idle': self.idle_frames,
            'run': self.run_frames,
            'walk': self.walk_frames,
            'jump': self.jump_frames,
            'attack1': self.attack1_frames,
            'attack2': self.attack2_frames,
            'run_attack': self.run_attack_frames,
            'defend': self.defend_frames,
            'dead': self.dead_frames,
            'hurt': self.hurt_frames,
        }

    def can_block(self, attacker_x: float) -> bool:
        """Checks if incoming attack is blocked based on defense state and orientation."""
        if not self.is_defending:
            return False
        if self.facing_right:
            return attacker_x >= self.rect.centerx
        return attacker_x <= self.rect.centerx

    def block_hit(self) -> None:
        """Plays shield defense sound effect."""
        self.sfx_defend.play()

    def take_damage(self, amount: int) -> None:
        """Inflicts damage and transitions hero into hurt or dead state."""
        super().take_damage(amount)
        if self._hp > 0:
            self._state = 'hurt'
            self._current_frame = 0.0
            self.is_attacking = False
            self.is_defending = False
        else:
            if self._state != 'dead':
                self._state = 'dead'
                self._current_frame = 0.0
                self.sfx_death.play()

    def update(self, dt: float) -> None:
        """Updates hero physics, input evaluation, FSM state changes, and audio triggers."""
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        state_map = self._get_state_map()

        if self._hp <= 0:
            self._vel.x = 0.0
            self.is_attacking = False
            self.is_defending = False
            self.is_running = False
            new_state = 'dead'
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

                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self._vel.x = -1.5 if self.is_running else -1.0
                    self.facing_right = False
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self._vel.x = 1.5 if self.is_running else 1.0
                    self.facing_right = True
                else:
                    self._vel.x = 0.0
            else:
                if self._state in ['hurt', 'attack1', 'attack2']:
                    self._vel.x = 0.0
                elif self._state == 'run_attack':
                    self._vel.x = 1.5 if self.facing_right else -1.5

            # Determine desired new state & velocity adjustments
            if self.is_defending:
                new_state = 'defend'
            elif self.is_attacking:
                if self.is_running and self._vel.x != 0:
                    new_state = 'run_attack'
                else:
                    self._vel.x = 0.0
                    new_state = 'attack1' if self._attack_type == 1 else 'attack2'
            elif self._pos.y < settings.FLOOR_HEIGHT:
                new_state = 'jump'
            elif self._vel.x != 0:
                new_state = 'run' if self.is_running else 'walk'
            else:
                new_state = 'idle'

            # Animation lock resolution
            current_list = state_map.get(self._state, self.idle_frames)
            total_frames = len(current_list)
            animation_finished = total_frames == 0 or self._current_frame >= total_frames - 1
            if is_locked and not animation_finished:
                new_state = self._state
            elif is_locked and animation_finished:
                self.is_attacking = False
                if self._state == 'hurt':
                    new_state = 'idle'

        # FSM state transition & Audio trigger handling
        if new_state != self._state:
            if self._state in ['attack1', 'attack2', 'run_attack']:
                self.sfx_attack.stop()

            self._current_frame = 0.0
            self._state = new_state
            self._attack_hit = False

            if new_state in ['attack1', 'attack2', 'run_attack']:
                self.sfx_attack.play()
            elif new_state == 'dead':
                self.sfx_death.play()

        # Advance animation frame safely
        current_list = state_map.get(self._state, self.idle_frames)
        total_frames = len(current_list)
        if total_frames > 0:
            self._current_frame += self._animation_speed * dt
            if self._state == 'dead':
                if self._current_frame >= total_frames - 1:
                    self._current_frame = float(total_frames - 1)
            else:
                self._current_frame %= total_frames

        # Physics simulation
        self._vel.y += self._gravity * dt
        if self._hp > 0 and keys[pygame.K_SPACE] and self._pos.y >= settings.FLOOR_HEIGHT:
            self._vel.y = self._jump_force

        self._pos.x += self._vel.x * self._speed * dt
        self._pos.y += self._vel.y * dt

        if self._pos.y >= settings.FLOOR_HEIGHT:
            self._pos.y = settings.FLOOR_HEIGHT
            self._vel.y = 0.0

        self._rect.midbottom = (round(self._pos.x), round(self._pos.y))

        # Horizontal screen boundary constraint
        if self._rect.left < -30:
            self._rect.left = -30
            self._pos.x = self._rect.midbottom[0]
        elif self._rect.right > settings.SCREEN_WIDTH + 30:
            self._rect.right = settings.SCREEN_WIDTH + 30
            self._pos.x = self._rect.midbottom[0]

        self.hurtbox.midbottom = self._rect.midbottom

    def draw(self, window: pygame.Surface) -> None:
        """Pure rendering method. Renders current active frame without side-effects."""
        state_map = self._get_state_map()
        current_list = state_map.get(self._state, self.idle_frames)
        if not current_list:
            return

        idx = int(self._current_frame)
        idx = max(0, min(idx, len(current_list) - 1))
        current_image = current_list[idx]

        if not self.facing_right:
            current_image = pygame.transform.flip(current_image, True, False)

        window.blit(current_image, self._rect)

    def get_hitbox(self) -> Optional[pygame.Rect]:
        """Returns offensive weapon hitbox during the active strike window."""
        if self._state in ['attack1', 'attack2', 'run_attack'] and not self._attack_hit:
            current_list = self.attack1_frames
            if current_list and self._current_frame >= len(current_list) - 2:
                if self.facing_right:
                    return pygame.Rect(self.hurtbox.right, self.hurtbox.centery - 20, 40, 40)
                return pygame.Rect(self.hurtbox.left - 40, self.hurtbox.centery - 20, 40, 40)
        return None

    def register_hit(self) -> None:
        """Registers that current swing connected with a target to prevent multi-hits."""
        self._attack_hit = True
