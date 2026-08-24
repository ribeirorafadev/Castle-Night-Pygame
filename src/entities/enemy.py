"""Enemy entity hierarchy including BasicEnemy and DragonBoss implementations."""

import random
from typing import Optional, Dict, List, Any
import pygame
from src.entities.entity import Entity
from src.utils.asset_loader import AssetLoader
from src.utils import settings


class Enemy(Entity):
    """Base class for all hostile entities."""

    def __init__(self, name: str, surf: pygame.Surface, x: float, y: float, speed: float = settings.ENEMY_SPEED) -> None:
        super().__init__(name, surf, x, y, speed)
        self.current_playing_sound: Optional[pygame.mixer.Sound] = None

    def take_damage(self, amount: int) -> None:
        """Inflicts damage, resets frame counter and updates state."""
        super().take_damage(amount)
        if self._hp <= 0:
            self._state = 'dead'
        else:
            self._state = 'hurt'

        if self.current_playing_sound:
            self.current_playing_sound.stop()
            self.current_playing_sound = None

        self._current_frame = 0.0

    @property
    def is_boss(self) -> bool:
        """Indicates whether this enemy is a boss."""
        return False


class BasicEnemy(Enemy):
    """Standard enemy entity with patrol AI, vision detection, and attack patterns."""

    def __init__(self, name: str, x: float, y: float, speed: float = settings.ENEMY_SPEED, config: Optional[Dict[str, Any]] = None) -> None:
        if config is None:
            config = {}

        self.idle_frames: List[pygame.Surface] = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/Idle.png', 128, 128)
        self.walk_frames: List[pygame.Surface] = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/Walk.png', 128, 128)
        self.hurt_frames: List[pygame.Surface] = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/Hurt.png', 128, 128)
        self.dead_frames: List[pygame.Surface] = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/Dead.png', 128, 128)

        if 'run' in config:
            self.run_frames: List[pygame.Surface] = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/{config["run"]}', 128, 128)
        else:
            self.run_frames = self.walk_frames

        if 'jump' in config:
            self.jump_frames: List[pygame.Surface] = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/{config["jump"]}', 128, 128)
        else:
            self.jump_frames = self.walk_frames

        if 'run_attack' in config:
            self.run_attack_frames: Optional[List[pygame.Surface]] = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/{config["run_attack"]}', 128, 128)
        else:
            self.run_attack_frames = None

        attack_files = config.get('attacks', ['Attack.png'])
        self.attack_animations: List[List[pygame.Surface]] = [
            AssetLoader.load_spritesheet(f'sprites/enemies/{name}/{f}', 128, 128) for f in attack_files
        ]

        attack_sound_files = config.get('attack_sounds', ['audio/Attack-Sword-Enemy.mp3'] * len(attack_files))
        self.attack_sounds = [AssetLoader.load_sound(f) for f in attack_sound_files]
        self.run_attack_sound = AssetLoader.load_sound(config['run_attack_sound']) if 'run_attack_sound' in config else None

        super().__init__(name, self.idle_frames[0], x, y, speed)
        self.max_hp: int = settings.ENEMY_MAX_HP
        self._hp: int = settings.ENEMY_MAX_HP
        self.attack_damage: int = settings.ENEMY_ATTACK_DAMAGE

        self._rect.midbottom = (round(x), round(y))
        self.hurtbox: pygame.Rect = pygame.Rect(0, 0, 40, 60)
        self.hurtbox.midbottom = self._rect.midbottom

        self._state: str = 'idle'
        self._current_frame: float = 0.0
        self._animation_speed: float = settings.ENEMY_ANIMATION_SPEED
        self._death_timer: float = 0.0
        self.facing_right: bool = False

        # AI properties
        self.vision_range: float = settings.ENEMY_VISION_RANGE
        self.attack_range: float = settings.ENEMY_ATTACK_RANGE
        self._attack_cooldown: float = 0.0
        self._patrol_timer: float = 0.0
        self._patrol_direction: int = 1
        self._attack_hit: bool = False
        self._current_attack_index: int = 0
        self._behavior_timer: float = 0.0

    def _get_active_frames(self) -> List[pygame.Surface]:
        """Returns the frame list for the current state."""
        if self._state in ['patrol', 'walk']:
            return self.walk_frames
        elif self._state == 'run':
            return self.run_frames
        elif self._state == 'jump':
            return self.jump_frames
        elif self._state == 'run_attack' and self.run_attack_frames:
            return self.run_attack_frames
        elif self._state == 'attack':
            idx = min(self._current_attack_index, len(self.attack_animations) - 1)
            return self.attack_animations[idx]
        elif self._state == 'hurt':
            return self.hurt_frames
        elif self._state == 'dead':
            return self.dead_frames
        return self.idle_frames

    def update(self, dt: float) -> None:
        """Updates AI behavior, physics, animation frames, and death timers."""
        self.hurtbox = pygame.Rect(0, 0, 40, 60)
        self.hurtbox.midbottom = self._rect.midbottom

        # Terminal Dead state lifecycle
        if self._state == 'dead':
            self._vel.x = 0.0
            self._current_frame += self._animation_speed * dt
            if self._current_frame >= len(self.dead_frames) - 1:
                self._current_frame = float(len(self.dead_frames) - 1)
                self._death_timer += dt
                if self._death_timer >= settings.ENEMY_DEATH_DELAY:
                    self._is_removable = True
            return

        # Interrupt Hurt state lifecycle
        if self._state == 'hurt':
            self._vel.x = 0.0
            self._current_frame += self._animation_speed * dt
            if self._current_frame >= len(self.hurt_frames) - 1:
                self._state = 'idle'
                self._current_frame = 0.0
            return

        # Attack animation lock and state lifecycle
        if self._state in ['attack', 'run_attack']:
            current_attack = self.attack_animations[self._current_attack_index] if self._state == 'attack' else self.run_attack_frames
            if current_attack and self._current_frame >= len(current_attack) - 1:
                self._state = 'idle'
                self._current_frame = 0.0
                self._attack_cooldown = settings.ENEMY_ATTACK_COOLDOWN
                self.current_playing_sound = None
            else:
                self._current_frame += self._animation_speed * dt
                self._vel.y += settings.GRAVITY * dt
                self._pos.x += self._vel.x * self._speed * dt
                self._pos.y += self._vel.y * dt

                if self._pos.y >= settings.FLOOR_HEIGHT:
                    self._pos.y = settings.FLOOR_HEIGHT
                    self._vel.y = 0.0

                self._rect.midbottom = (round(self._pos.x), round(self._pos.y))
                self.hurtbox.midbottom = self._rect.midbottom
                return

        if self._attack_cooldown > 0:
            self._attack_cooldown -= dt

        # Vector Vision & AI Movement
        if self._target and self._target.hp > 0:
            dist_x = self._target.rect.centerx - self._rect.centerx
            if abs(dist_x) <= self.attack_range:
                if self._attack_cooldown <= 0:
                    actions = ['attack']
                    if self.run_attack_frames:
                        actions.append('run_attack')

                    self._state = random.choice(actions)
                    self._current_frame = 0.0
                    self.facing_right = dist_x > 0
                    self._attack_hit = False

                    if self.current_playing_sound:
                        self.current_playing_sound.stop()

                    if self._state == 'attack':
                        self._current_attack_index = random.randint(0, len(self.attack_animations) - 1)
                        self._vel.x = 0.0
                        self.current_playing_sound = self.attack_sounds[self._current_attack_index]
                    else:
                        self._vel.x = 2.0 if dist_x > 0 else -2.0
                        self.current_playing_sound = self.run_attack_sound

                    if self.current_playing_sound:
                        self.current_playing_sound.play()
                else:
                    self._state = 'idle'
                    self._vel.x = 0.0
            elif abs(dist_x) <= self.vision_range:
                if self._state not in ['run', 'walk', 'jump'] or self._behavior_timer <= 0:
                    actions = ['walk', 'run']
                    if self.jump_frames != self.walk_frames:
                        actions.append('jump')
                    self._state = random.choice(actions)
                    self._behavior_timer = random.uniform(0.5, 1.5)
                else:
                    self._behavior_timer -= dt

                direction = 1.0 if dist_x > 0 else -1.0
                self.facing_right = dist_x > 0

                if self._state == 'walk':
                    self._vel.x = direction * 0.5
                elif self._state == 'run':
                    self._vel.x = direction * 1.5
                elif self._state == 'jump':
                    self._vel.x = direction * 2.0
                    if self._pos.y >= settings.FLOOR_HEIGHT:
                        self._vel.y = settings.ENEMY_JUMP_FORCE
            else:
                self._patrol_behavior(dt)
        else:
            self._patrol_behavior(dt)

        self._vel.y += settings.GRAVITY * dt
        self._pos.x += self._vel.x * self._speed * dt
        self._pos.y += self._vel.y * dt

        if self._pos.y >= settings.FLOOR_HEIGHT:
            self._pos.y = settings.FLOOR_HEIGHT
            self._vel.y = 0.0

        self._rect.midbottom = (round(self._pos.x), round(self._pos.y))

        # Screen boundary wall bounce
        if self._rect.left < 0 and self._vel.x < 0:
            self._rect.left = 0
            self._pos.x = self._rect.midbottom[0]
            self._patrol_direction *= -1
        elif self._rect.right > settings.SCREEN_WIDTH and self._vel.x > 0:
            self._rect.right = settings.SCREEN_WIDTH
            self._pos.x = self._rect.midbottom[0]
            self._patrol_direction *= -1

        self.hurtbox.midbottom = self._rect.midbottom

        # Looping animation frame advancement
        active_frames = self._get_active_frames()
        self._current_frame = (self._current_frame + self._animation_speed * dt) % len(active_frames)

    def _patrol_behavior(self, dt: float) -> None:
        """Patrol logic for passive roaming."""
        self._state = 'patrol'
        self._patrol_timer -= dt
        if self._patrol_timer <= 0:
            self._patrol_direction *= -1
            self._patrol_timer = 2.0
        self._vel.x = float(self._patrol_direction)
        self.facing_right = self._vel.x > 0

    def get_hitbox(self) -> Optional[pygame.Rect]:
        """Calculates offensive collision hitbox during active attack frames."""
        if (self._state == 'attack' or self._state == 'run_attack') and not self._attack_hit:
            current_attack = self.attack_animations[self._current_attack_index] if self._state == 'attack' else self.run_attack_frames
            if current_attack and self._current_frame >= len(current_attack) - 2:
                if self.facing_right:
                    return pygame.Rect(self.hurtbox.left, self.hurtbox.centery - 20, 80, 40)
                return pygame.Rect(self.hurtbox.right - 80, self.hurtbox.centery - 20, 80, 40)
        return None

    def register_hit(self) -> None:
        """Registers hit connection."""
        self._attack_hit = True

    def draw(self, window: pygame.Surface) -> None:
        """Pure rendering method without side effects."""
        current_list = self._get_active_frames()
        idx = int(self._current_frame)
        idx = max(0, min(idx, len(current_list) - 1))
        current_image = current_list[idx]

        if not self.facing_right:
            current_image = pygame.transform.flip(current_image, True, False)

        window.blit(current_image, self._rect)


class DragonBoss(Enemy):
    """Dragon Boss entity featuring dual attack phases, fire breath VFX, and super-armor immunity."""

    def __init__(self, x: float, y: float, speed: float = settings.BOSS_SPEED) -> None:
        self.idle_frames: List[pygame.Surface] = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Idle{i}.png') for i in range(1, 4)]
        self.hurt_frames: List[pygame.Surface] = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Hurt{i}.png') for i in range(1, 3)]
        self.dead_frames: List[pygame.Surface] = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Death{i}.png') for i in range(1, 6)]
        self.walk_frames: List[pygame.Surface] = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Walk{i}.png') for i in range(1, 6)]
        self.base_attack_frames: List[pygame.Surface] = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Attack{i}.png') for i in range(1, 5)]
        self.fire_frames: List[pygame.Surface] = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Fire_Attack{i}.png') for i in [1, 2, 3, 5]]
        self.attack_frames: List[pygame.Surface] = self.base_attack_frames + self.fire_frames

        self.sfx_attack = AssetLoader.load_sound('audio/Attack-Boss.mp3')
        self.sfx_death = AssetLoader.load_sound('audio/Death-boss.mp3')

        super().__init__("DragonBoss", self.idle_frames[0], x, y, speed)

        self.max_hp: int = settings.BOSS_MAX_HP
        self._hp: int = settings.BOSS_MAX_HP
        self.attack_damage: int = settings.BOSS_ATTACK_DAMAGE
        self.vision_range: float = settings.BOSS_VISION_RANGE
        self.attack_range: float = settings.BOSS_ATTACK_RANGE
        self._attack_cooldown: float = 0.0
        self._attack_hit: bool = False
        self.facing_right: bool = False

        self._rect.midbottom = (round(x), round(y) + 65)
        self.hurtbox: pygame.Rect = pygame.Rect(0, 0, 150, 150)
        self.hurtbox.midbottom = self._rect.midbottom

        self._state: str = 'idle'
        self._current_frame: float = 0.0
        self._animation_speed: float = settings.BOSS_ANIMATION_SPEED
        self._death_timer: float = 0.0

    @property
    def is_boss(self) -> bool:
        """DragonBoss is classified as a boss entity."""
        return True

    def take_damage(self, amount: int) -> None:
        """Inflicts damage with Super-Armor: hp is reduced, but state/attacks/cooldowns are never interrupted unless dead."""
        self.hp -= amount
        if self._hp <= 0:
            self._state = 'dead'
            self._current_frame = 0.0
            if self.current_playing_sound:
                self.current_playing_sound.stop()
                self.current_playing_sound = None
            if self.sfx_death:
                self.sfx_death.play()

    def apply_knockback(self, direction: float | int, force: float = settings.KNOCKBACK_FORCE) -> None:
        """Knockback immunity: Boss has infinite poise and cannot be displaced by knockback."""
        pass

    def update(self, dt: float) -> None:
        """Updates boss AI, attack sequences, and death state timers."""
        if self._state == 'dead':
            self._vel.x = 0.0
            self._current_frame += self._animation_speed * dt
            if self._current_frame >= len(self.dead_frames) - 1:
                self._current_frame = float(len(self.dead_frames) - 1)
                self._death_timer += dt
                if self._death_timer >= settings.BOSS_DEATH_DELAY:
                    self._is_removable = True
            return

        if self._state == 'hurt':
            self._vel.x = 0.0
            self._current_frame += self._animation_speed * dt
            if self._current_frame >= len(self.hurt_frames) - 1:
                self._state = 'idle'
                self._current_frame = 0.0
            return

        if self._state == 'attack':
            self._current_frame += self._animation_speed * dt
            if self._current_frame >= len(self.attack_frames) - 1:
                self._state = 'idle'
                self._current_frame = 0.0
                self._attack_cooldown = settings.BOSS_ATTACK_COOLDOWN
        else:
            if self._attack_cooldown > 0:
                self._attack_cooldown -= dt

            if self._target:
                dist_x = self._target.rect.centerx - self._rect.centerx
                if abs(dist_x) <= self.attack_range:
                    if self._attack_cooldown <= 0:
                        self._state = 'attack'
                        self._current_frame = 0.0
                        self._attack_cooldown = settings.BOSS_ATTACK_COOLDOWN
                        self._attack_hit = False
                        self._vel.x = 0.0
                        self.facing_right = dist_x > 0
                        self.sfx_attack.play()
                    elif self._state != 'attack':
                        self._state = 'idle'
                        self._vel.x = 0.0
                else:
                    if self._state != 'attack':
                        self._state = 'run'
                        direction = 1.0 if dist_x > 0 else -1.0
                        self._vel.x = direction * 1.5
                        self.facing_right = direction > 0

            # Advance looping animation frames
            current_list = self.walk_frames if self._state == 'run' else self.idle_frames
            self._current_frame = (self._current_frame + self._animation_speed * dt) % len(current_list)

        self._vel.y += settings.GRAVITY * dt
        self._pos.x += self._vel.x * self._speed * dt
        self._pos.y += self._vel.y * dt

        if self._pos.y >= settings.FLOOR_HEIGHT:
            self._pos.y = settings.FLOOR_HEIGHT
            self._vel.y = 0.0

        self._rect.midbottom = (round(self._pos.x), round(self._pos.y) + 65)
        self.hurtbox = pygame.Rect(0, 0, 150, 150)
        self.hurtbox.midbottom = self._rect.midbottom

    def get_hitbox(self) -> Optional[pygame.Rect]:
        """Returns offensive boss hitbox during fire breath phase."""
        if self._state == 'attack' and not self._attack_hit:
            if self._current_frame >= len(self.attack_frames) - 4:
                if self.facing_right:
                    return pygame.Rect(self.hurtbox.right, self.hurtbox.centery - 50, 150, 100)
                return pygame.Rect(self.hurtbox.left - 150, self.hurtbox.centery - 50, 150, 100)
        return None

    def register_hit(self) -> None:
        """Registers hit on player."""
        self._attack_hit = True

    def draw(self, window: pygame.Surface) -> None:
        """Pure rendering method for boss body and decoupled fire breath VFX."""
        frame_idx = int(self._current_frame)

        if self._state == 'attack' and frame_idx >= len(self.base_attack_frames):
            base_img = self.base_attack_frames[-1]
            if not self.facing_right:
                base_img = pygame.transform.flip(base_img, True, False)
            window.blit(base_img, self._rect)

            fire_idx = min(frame_idx - len(self.base_attack_frames), len(self.fire_frames) - 1)
            fire_img = self.fire_frames[fire_idx]

            if self.facing_right:
                offset_x = 155
                offset_y = 85
            else:
                offset_x = -27
                offset_y = 85
                fire_img = pygame.transform.flip(fire_img, True, False)

            fire_pos = (self._rect.x + offset_x, self._rect.y + offset_y)
            window.blit(fire_img, fire_pos)
        else:
            current_list = self.idle_frames
            if self._state == 'run':
                current_list = self.walk_frames
            elif self._state == 'attack':
                current_list = self.attack_frames
            elif self._state == 'hurt':
                current_list = self.hurt_frames
            elif self._state == 'dead':
                current_list = self.dead_frames

            idx = max(0, min(frame_idx, len(current_list) - 1))
            current_image = current_list[idx]
            if not self.facing_right:
                current_image = pygame.transform.flip(current_image, True, False)
            window.blit(current_image, self._rect)
