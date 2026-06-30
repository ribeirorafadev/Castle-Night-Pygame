import pygame
import random
from src.entities.entity import Entity
from src.utils.asset_loader import AssetLoader
from src.utils import settings

class Enemy(Entity):
    def take_damage(self, amount: int) -> None:
        super().take_damage(amount)
        if self._hp <= 0:
            self._state = 'dead'
        else:
            self._state = 'hurt'
            
        if hasattr(self, 'current_playing_sound') and self.current_playing_sound:
            self.current_playing_sound.stop()
            self.current_playing_sound = None
            
        self._current_frame = 0.0

class BasicEnemy(Enemy):
    def __init__(self, name: str, x: float, y: float, speed: float, config: dict = None) -> None:
        if config is None: config = {}
        self.idle_frames = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/Idle.png', 128, 128)
        self.walk_frames = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/Walk.png', 128, 128)
        self.hurt_frames = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/Hurt.png', 128, 128)
        self.dead_frames = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/Dead.png', 128, 128)
        
        if 'run' in config:
            self.run_frames = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/{config["run"]}', 128, 128)
        else:
            self.run_frames = self.walk_frames
            
        if 'jump' in config:
            self.jump_frames = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/{config["jump"]}', 128, 128)
        else:
            self.jump_frames = self.walk_frames
            
        if 'run_attack' in config:
            self.run_attack_frames = AssetLoader.load_spritesheet(f'sprites/enemies/{name}/{config["run_attack"]}', 128, 128)
        else:
            self.run_attack_frames = None
            
        attack_files = config.get('attacks', ['Attack.png'])
        self.attack_animations = [AssetLoader.load_spritesheet(f'sprites/enemies/{name}/{f}', 128, 128) for f in attack_files]
        
        attack_sound_files = config.get('attack_sounds', ['audio/Attack-Sword-Enemy.mp3'] * len(attack_files))
        self.attack_sounds = [AssetLoader.load_sound(f) for f in attack_sound_files]
        self.run_attack_sound = AssetLoader.load_sound(config['run_attack_sound']) if 'run_attack_sound' in config else None
        self.current_playing_sound = None
        
        super().__init__(name, self.idle_frames[0], x, y, speed)
        self._rect.midbottom = (round(x), round(y))
        self._state: str = 'idle'
        self._current_frame: float = 0.0
        self._animation_speed: float = 8.0
        self._game_dt: float = 0.0
        self.is_removable: bool = False
        self._death_timer: float = 0.0
        self.facing_right: bool = False
        
        # Variáveis da IA
        self.vision_range: float = 300.0
        self.attack_range: float = 60.0
        self._attack_cooldown: float = 0.0
        self._patrol_timer: float = 0.0
        self._patrol_direction: int = 1
        self._attack_hit: bool = False
        self._current_attack_index: int = 0
        self._behavior_timer: float = 0.0

    def update(self, dt: float) -> None:
        self._game_dt = dt
        self.hurtbox = pygame.Rect(0, 0, 40, 60)
        self.hurtbox.midbottom = self._rect.midbottom
        
        if self._attack_cooldown > 0:
            self._attack_cooldown -= dt
        
        # Trava de Estado (Lock): estados terminais e de interrupção
        if self._state in ['hurt', 'dead']:
            return
        
        # Lock de ataque: verificar se a animação terminou
        if self._state == 'attack' or self._state == 'run_attack':
            current_attack = self.attack_animations[self._current_attack_index] if self._state == 'attack' else self.run_attack_frames
            if self._current_frame >= len(current_attack) - 1:
                self._state = 'idle'
                self._current_frame = 0.0
                self._attack_cooldown = 1.5
                self.current_playing_sound = None
            else:
                self._vel.y += 800.0 * dt
                self._pos.x += self._vel.x * self._speed * dt
                self._pos.y += self._vel.y * dt
                
                if self._pos.y >= settings.FLOOR_HEIGHT:
                    self._pos.y = settings.FLOOR_HEIGHT
                    self._vel.y = 0.0

                self._rect.midbottom = (round(self._pos.x), round(self._pos.y))
                self.hurtbox.midbottom = self._rect.midbottom
                return
        
        # Visão Vetorial
        # Só persegue se o alvo existir e estiver vivo
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
                        self._vel.x = 0
                        self.current_playing_sound = self.attack_sounds[self._current_attack_index]
                    else:
                        self._vel.x = 2 if dist_x > 0 else -2
                        self.current_playing_sound = self.run_attack_sound
                        
                    if self.current_playing_sound:
                        self.current_playing_sound.play()
                else:
                    # Stop Distance: Impede o Z-Fighting e sobreposição enquanto recarrega
                    self._state = 'idle'
                    self._vel.x = 0
            elif abs(dist_x) <= self.vision_range:
                if self._state not in ['run', 'walk', 'jump'] or self._behavior_timer <= 0:
                    actions = ['walk', 'run']
                    if self.jump_frames != self.walk_frames:
                        actions.append('jump')
                    self._state = random.choice(actions)
                    self._behavior_timer = random.uniform(0.5, 1.5)
                else:
                    self._behavior_timer -= dt

                direction = 1 if dist_x > 0 else -1
                self.facing_right = dist_x > 0
                
                if self._state == 'walk':
                    self._vel.x = direction * 0.5
                elif self._state == 'run':
                    self._vel.x = direction * 1.5
                elif self._state == 'jump':
                    self._vel.x = direction * 2.0
                    if self._pos.y >= settings.FLOOR_HEIGHT:
                        self._vel.y = -400.0
            else:
                self._patrol_behavior(dt) # Delega a patrulha para simplificar o código
        else:
            self._patrol_behavior(dt)
        
        self._vel.y += 800.0 * dt
        self._pos.x += self._vel.x * self._speed * dt
        self._pos.y += self._vel.y * dt

        if self._pos.y >= settings.FLOOR_HEIGHT:
            self._pos.y = settings.FLOOR_HEIGHT
            self._vel.y = 0.0

        self._rect.midbottom = (round(self._pos.x), round(self._pos.y))
        
        if self._rect.left < 0 and self._vel.x < 0:
            self._rect.left = 0
            self._pos.x = self._rect.midbottom[0]
            self._patrol_direction *= -1 # Vira ao bater na parede
        elif self._rect.right > settings.SCREEN_WIDTH and self._vel.x > 0:
            self._rect.right = settings.SCREEN_WIDTH
            self._pos.x = self._rect.midbottom[0]
            self._patrol_direction *= -1

        self.hurtbox.midbottom = self._rect.midbottom

    def _patrol_behavior(self, dt: float) -> None:
        self._state = 'patrol'
        self._patrol_timer -= dt
        if self._patrol_timer <= 0:
            self._patrol_direction *= -1
            self._patrol_timer = 2.0
        self._vel.x = self._patrol_direction
        self.facing_right = self._vel.x > 0

    def get_hitbox(self) -> pygame.Rect | None:
        if (self._state == 'attack' or self._state == 'run_attack') and not self._attack_hit:
            current_attack = self.attack_animations[self._current_attack_index] if self._state == 'attack' else self.run_attack_frames
            if self._current_frame >= len(current_attack) - 2:
                if self.facing_right:
                    return pygame.Rect(self.hurtbox.left, self.hurtbox.centery - 20, 80, 40)
                else:
                    return pygame.Rect(self.hurtbox.right - 80, self.hurtbox.centery - 20, 80, 40)
        return None

    def register_hit(self) -> None:
        self._attack_hit = True

    def draw(self, window: pygame.Surface) -> None:
        current_list = self.idle_frames
        if self._state == 'patrol' or self._state == 'walk':
            current_list = self.walk_frames
        elif self._state == 'run':
            current_list = self.run_frames
        elif self._state == 'jump':
            current_list = self.jump_frames
        elif self._state == 'run_attack':
            current_list = self.run_attack_frames
        elif self._state == 'attack':
            current_list = self.attack_animations[self._current_attack_index]
        elif self._state == 'hurt':
            current_list = self.hurt_frames
            if self._current_frame >= len(current_list) - 1:
                self._state = 'idle'
                self._current_frame = 0.0
                current_list = self.idle_frames
        elif self._state == 'dead':
            current_list = self.dead_frames
            if self._current_frame >= len(current_list) - 1:
                self._current_frame = len(current_list) - 1.0
                self._death_timer += self._game_dt
                if self._death_timer >= 2.0:
                    self.is_removable = True

        self._current_frame += self._animation_speed * self._game_dt

        if self._state != 'dead' and self._state != 'hurt':
            self._current_frame %= len(current_list)

        current_image = current_list[int(self._current_frame)]
        
        if not self.facing_right:
            current_image = pygame.transform.flip(current_image, True, False)
            
        window.blit(current_image, self._rect)
        
        if 0 < self._hp < 100:
            bar_w, bar_h = 40, 6
            x = self._rect.centerx - (bar_w // 2)
            y = self._rect.top - 15
            # Borda (Sombra)
            pygame.draw.rect(window, (0, 0, 0), (x - 1, y - 1, bar_w + 2, bar_h + 2))
            # Fundo Cinza
            pygame.draw.rect(window, (50, 50, 50), (x, y, bar_w, bar_h))
            # Barra Vermelha
            pygame.draw.rect(window, (220, 20, 20), (x, y, int(bar_w * (self._hp / 100.0)), bar_h))

class DragonBoss(Enemy):
    def __init__(self, x: float, y: float, speed: float) -> None:
        self.idle_frames = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Idle{i}.png') for i in range(1, 4)]
        self.hurt_frames = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Hurt{i}.png') for i in range(1, 3)]
        self.dead_frames = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Death{i}.png') for i in range(1, 6)]
        self.walk_frames = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Walk{i}.png') for i in range(1, 6)]
        self.base_attack_frames = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Attack{i}.png') for i in range(1, 5)]
        self.fire_frames = [AssetLoader.load_image(f'sprites/enemies/boss-dragon/Fire_Attack{i}.png') for i in [1, 2, 3, 5]]
        self.attack_frames = self.base_attack_frames + self.fire_frames
        
        self.sfx_attack = AssetLoader.load_sound('audio/Attack-Boss.mp3')
        self.sfx_death = AssetLoader.load_sound('audio/Death-boss.mp3')
        
        super().__init__("DragonBoss", self.idle_frames[0], x, y, speed)
        
        self.max_hp = 500
        self._hp = 500
        self.attack_damage = 25
        self.vision_range = 600.0
        self.attack_range = 120.0
        self._attack_cooldown = 0.0
        self._attack_hit = False
        self.facing_right = False
        
        self._rect.midbottom = (round(x), round(y) + 65)
        self._state: str = 'idle'
        self._current_frame: float = 0.0
        self._animation_speed: float = 8.0
        self._game_dt: float = 0.0
        self.is_removable: bool = False
        self._death_timer: float = 0.0

    def take_damage(self, amount: int) -> None:
        Entity.take_damage(self, amount)
        if self._hp <= 0 and self._state != 'dead':
            self._state = 'dead'
            self._current_frame = 0.0
            self.sfx_death.play()

    def update(self, dt: float) -> None:
        self._game_dt = dt
        
        if self._state == 'dead' or self._state == 'hurt':
            self._vel.x = 0.0
        else:
            if self._attack_cooldown > 0:
                self._attack_cooldown -= dt
                
            dist_x = self._target._pos.x - self._pos.x
            
            if abs(dist_x) <= self.attack_range:
                if self._attack_cooldown <= 0:
                    self._state = 'attack'
                    self._current_frame = 0.0
                    self._attack_cooldown = 2.0
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
                
        self._vel.y += 800.0 * dt
        self._pos.x += self._vel.x * self._speed * dt
        self._pos.y += self._vel.y * dt
        
        if self._pos.y >= settings.FLOOR_HEIGHT:
            self._pos.y = settings.FLOOR_HEIGHT
            self._vel.y = 0.0
            
        self._rect.midbottom = (round(self._pos.x), round(self._pos.y) + 65)
        
        self.hurtbox = pygame.Rect(0, 0, 150, 150)
        self.hurtbox.midbottom = self._rect.midbottom

    def get_hitbox(self) -> pygame.Rect | None:
        if self._state == 'attack' and not self._attack_hit:
            if self._current_frame >= len(self.attack_frames) - 4:
                if self.facing_right:
                    return pygame.Rect(self.hurtbox.right, self.hurtbox.centery - 50, 150, 100)
                else:
                    return pygame.Rect(self.hurtbox.left - 150, self.hurtbox.centery - 50, 150, 100)
        return None

    def register_hit(self) -> None:
        self._attack_hit = True

    def draw(self, window: pygame.Surface) -> None:
        current_list = self.idle_frames
        if self._state == 'run':
            current_list = self.walk_frames
        elif self._state == 'attack':
            current_list = self.attack_frames
            if self._current_frame >= len(current_list) - 1:
                self._state = 'idle'
                self._current_frame = 0.0
                current_list = self.idle_frames
        elif self._state == 'hurt':
            current_list = self.hurt_frames
            if self._current_frame >= len(current_list) - 1:
                self._state = 'idle'
                self._current_frame = 0.0
                current_list = self.idle_frames
        elif self._state == 'dead':
            current_list = self.dead_frames
            if self._current_frame >= len(current_list) - 1:
                self._current_frame = len(current_list) - 1.0
                self._death_timer += self._game_dt
                if self._death_timer >= 2.0:
                    self.is_removable = True

        self._current_frame += self._animation_speed * self._game_dt

        if self._state != 'dead' and self._state != 'hurt':
            self._current_frame %= len(current_list)

        frame_idx = int(self._current_frame)
        
        if self._state == 'attack' and frame_idx >= len(self.base_attack_frames):
            # Renderiza o corpo do dragão (último frame de ataque físico)
            base_img = self.base_attack_frames[-1]
            if not self.facing_right:
                base_img = pygame.transform.flip(base_img, True, False)
            window.blit(base_img, self._rect)
            
            # Renderiza o efeito VFX de fogo
            fire_idx = frame_idx - len(self.base_attack_frames)
            fire_img = self.fire_frames[fire_idx]
            # --- DESACOPLAMENTO VETORIAL DO VFX ---
            if self.facing_right:
                # Valores calibrados matematicamente (Base: 256px, Fogo: 128px)
                # Boca na direita: x=180. Origem do fogo: x=25. 180 - 25 = 155.
                offset_x = 155
                offset_y = 85
            else:
                # Boca na esquerda (flip): x=76. Origem do fogo (flip): x=103. 76 - 103 = -27.
                offset_x = -27
                offset_y = 85
                fire_img = pygame.transform.flip(fire_img, True, False)
                
            fire_pos = (self._rect.x + offset_x, self._rect.y + offset_y)
            window.blit(fire_img, fire_pos)
        else:
            # Renderização normal dos demais estados
            current_image = current_list[frame_idx]
            if not self.facing_right:
                current_image = pygame.transform.flip(current_image, True, False)
            window.blit(current_image, self._rect)
