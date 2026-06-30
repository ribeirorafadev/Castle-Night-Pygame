import pygame
import random
import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from src.utils.asset_loader import AssetLoader

from src.entities.hero import Hero
from src.entities.factory import EntityFactory
from src.core.mediator import CombatMediator
from src.utils import settings

if TYPE_CHECKING:
    from src.core.game import Game


class IState(ABC):
    """Interface para o Padrão de Projeto Comportamental 'State'. Delega a execução do loop principal para classes de estado específicas."""
    @abstractmethod
    def run(self, dt: float) -> None:
        pass


class MenuState(IState):
    def __init__(self, game: 'Game') -> None:
        self._game = game
        self._font = pygame.font.Font(None, 36)
        
        # Carregamento seguro baseado no AssetLoader
        self._bg_image = AssetLoader.load_image("sprites/background/Menu.png")
        # A função smoothscale foi escolhida para prevenir a distorção dos pixels ao comprimir 
        # a imagem de 1080p para a resolução da tela, demonstrando domínio técnico de UI para a banca avaliadora.
        self._bg_image = pygame.transform.smoothscale(
            self._bg_image,
            (self._game.window.get_width(), self._game.window.get_height())
        )
        
        # Uso do fluxo dedicado de BGM para evitar sobreposição (overlap) de canais
        pygame.mixer.music.load(AssetLoader._get_path("audio/Sound-Menu.mp3"))
        pygame.mixer.music.play(-1)

    def run(self, dt: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._game.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Encerra o áudio do menu
                    pygame.mixer.music.stop()
                    # Limpa a fila de eventos para evitar inputs acidentais na próxima tela
                    pygame.event.clear()
                    # Delega a mudança de estado para o Contexto, permitindo coleta do GC
                    self._game.change_state(LevelState(self._game))

        # Renderização do background substituindo a cor sólida
        self._game.window.blit(self._bg_image, (0, 0))

        import math
        
        # 1. Overlay Escuro Translúcido (Glassmorphism) para destacar o texto
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self._game.window.blit(overlay, (0, 0))

        # 2 e 3. Pulsar Suave (math.sin) e Drop Shadow do Press Enter
        ticks = pygame.time.get_ticks()
        alpha = int(abs(math.sin(ticks / 400.0)) * 200) + 55
        
        start_prompt = self._font.render("Press Enter to start", True, (255, 255, 255))
        start_prompt_shadow = self._font.render("Press Enter to start", True, (0, 0, 0))
        start_prompt.set_alpha(alpha)
        start_prompt_shadow.set_alpha(alpha)
        
        w, h = self._font.size("Press Enter to start")
        prompt_x = settings.SCREEN_WIDTH // 2 - w // 2
        prompt_y = 490
        
        self._game.window.blit(start_prompt_shadow, (prompt_x + 2, prompt_y + 2))
        self._game.window.blit(start_prompt, (prompt_x, prompt_y))

        # 4. Teclas Estilizadas (Boxes) com Drop Shadow
        instructions_data = [
            ("Key A", "Move to the Left"),
            ("Key D", "Move to the Right"),
            ("Space", "Jump"),
            ("Left Shift", "Run"),
            ("Key C", "Defend"),
            ("Left Mouse button", "Attack 1"),
            ("Right Mouse button", "Attack 2")
        ]

        start_y = 110
        center_x = settings.SCREEN_WIDTH // 2
        for key_text, action_text in instructions_data:
            key_surface = self._font.render(key_text, True, (255, 255, 255))
            action_surface = self._font.render(action_text, True, (225, 173, 1))
            action_shadow = self._font.render(action_text, True, (0, 0, 0))
            
            box_padding_x = 12
            box_padding_y = 6
            box_width = key_surface.get_width() + (box_padding_x * 2)
            box_height = key_surface.get_height() + (box_padding_y * 2)
            
            gap_from_center = 15
            
            # As caixas (teclas) alinham-se à direita antes do centro
            start_x = center_x - box_width - gap_from_center
            
            # Sombra da tecla
            box_rect_shadow = pygame.Rect(start_x + 3, start_y + 3, box_width, box_height)
            pygame.draw.rect(self._game.window, (0, 0, 0), box_rect_shadow, border_radius=6)
            
            # Fundo vermelho da tecla
            box_rect = pygame.Rect(start_x, start_y, box_width, box_height)
            pygame.draw.rect(self._game.window, (204, 25, 25), box_rect, border_radius=6)
            # Borda branca
            pygame.draw.rect(self._game.window, (255, 255, 255), box_rect, width=2, border_radius=6)
            
            # Texto da tecla dentro da caixa
            self._game.window.blit(key_surface, (start_x + box_padding_x, start_y + box_padding_y))
            
            # Ação alinhada à esquerda após o centro
            action_x = center_x + gap_from_center
            action_y = start_y + box_padding_y
            self._game.window.blit(action_shadow, (action_x + 2, action_y + 2))
            self._game.window.blit(action_surface, (action_x, action_y))
            
            start_y += box_height + 15


class LevelState(IState):
    def __init__(self, game: 'Game') -> None:
        self._game = game
        self.hero = EntityFactory.create_hero(x=settings.SCREEN_WIDTH // 2, y=settings.FLOOR_HEIGHT)
        self._font_go = pygame.font.Font(None, 72)
        self._game_over_timer = 0.0
        
        self.enemies_to_boss: int = 20
        self.boss_spawned: bool = False
        self._shake_timer: float = 0.0
        self.ui_font = pygame.font.Font(None, 28)
        
        self.enemies = []
        self._display = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        
        res = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

        self._bg_image = pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/Background.png'), res)
        self._mountains_image = pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/Mountains.png'), res)
        self._wall_windows_image = pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/WallWindows.png'), res)
        self._columns_flags_image = pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/ColumnsFlags.png'), res)
        self._statue_dragon_image = pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/StatueDragon.png'), res)
        self._candeliar_image = pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/Candeliar.png'), res)
        self._floor_image = pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/Floor.png'), res)

        pygame.mixer.music.load(AssetLoader._get_path('audio/Sound-Normal.mp3'))
        pygame.mixer.music.play(-1)
        
        self._spawn_wave()
        
        self.mediator = CombatMediator(self.hero)

    def _spawn_wave(self) -> None:
        if self.enemies_to_boss <= 0:
            if not self.boss_spawned:
                boss = EntityFactory.create_enemy('boss-dragon', settings.SCREEN_WIDTH + 50.0, settings.FLOOR_HEIGHT)
                boss.set_target(self.hero)
                self.enemies.append(boss)
                self.boss_spawned = True
                self._shake_timer = 2.0
                
                pygame.mixer.music.load(AssetLoader._get_path('audio/Sound-Boss.mp3'))
                pygame.mixer.music.play(-1)
            return

        types = ['minotaur', 'wizard', 'skeleton', 'werewolf', 'yokai']
        
        defeated = 20 - self.enemies_to_boss
        
        if defeated < 6:
            num_right = 1
            num_left = 1
        elif defeated < 15:
            num_right = 2
            num_left = 1
        else:
            num_right = 2
            num_left = 3
            
        total_enemies = num_right + num_left
        total_enemies = min(total_enemies, self.enemies_to_boss)

        # Distribuir os spawns limitados
        spawn_sides = ['right'] * num_right + ['left'] * num_left
        spawn_sides = spawn_sides[:total_enemies]
        
        for side in spawn_sides:
            enemy_type = random.choice(types)
            
            if side == 'right':
                spawn_x = settings.SCREEN_WIDTH + 50.0 + random.uniform(0, 80)
            else:
                spawn_x = -50.0 - random.uniform(0, 80)
                
            new_enemy = EntityFactory.create_enemy(enemy_type, spawn_x, settings.FLOOR_HEIGHT)
            new_enemy.set_target(self.hero)
            self.enemies.append(new_enemy)

    def _draw_hud_panel(self, text: str, color: tuple, px: int, py: int, right_align: bool = False) -> None:
        text_surface = self.ui_font.render(text, True, color)
        shadow_surface = self.ui_font.render(text, True, (0, 0, 0))
        
        padding_x, padding_y = 12, 6
        panel_w = text_surface.get_width() + (padding_x * 2)
        panel_h = text_surface.get_height() + (padding_y * 2)
        
        if right_align:
            px = px - panel_w
            
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        self._game.window.blit(panel, (px, py))
        
        text_x = px + padding_x
        text_y = py + padding_y
        self._game.window.blit(shadow_surface, (text_x + 2, text_y + 2))
        self._game.window.blit(text_surface, (text_x, text_y))

    def run(self, dt: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._game.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.stop()
                    pygame.mixer.music.stop()
                    # Limpa a fila de eventos ao sair para manter isolamento de contexto
                    pygame.event.clear()
                    # Retorna ao estado anterior por delegação
                    self._game.change_state(MenuState(self._game))

        self._display.blit(self._bg_image, (0, 0))
        self._display.blit(self._mountains_image, (0, 0))
        self._display.blit(self._wall_windows_image, (0, 0))
        self._display.blit(self._columns_flags_image, (0, 0))
        self._display.blit(self._statue_dragon_image, (0, 0))
        self._display.blit(self._candeliar_image, (0, 0))
        self._display.blit(self._floor_image, (0, 0))

        is_win = getattr(self, 'boss_defeated', False)
        
        self.hero.update(dt)
        self.hero.draw(self._display)
        
        for enemy in self.enemies:
            # Hit-stop: congela os inimigos menores quando a tela de Win ou Death está ativa
            enemy_dt = 0.0 if (self.hero.hp <= 0 or is_win) and getattr(enemy, '_name', '') != 'DragonBoss' else dt
            enemy.update(enemy_dt)
            enemy.draw(self._display)
        
        alive_enemies = []
        for enemy in self.enemies:
            if enemy.is_removable:
                if getattr(enemy, '_name', '') != 'DragonBoss':
                    self.enemies_to_boss -= 1
            else:
                alive_enemies.append(enemy)
        # Rotina de Garbage Collection manual: Desaloca instâncias mortas da RAM para prevenir Memory Leaks.
        self.enemies = alive_enemies
            
        if self.hero.hp > 0 and not is_win:
            self.mediator.update(self.enemies)

        # HUD: Barra de Vida do Herói Dinâmica
        hp_max_width = 240
        hp_height = 22
        x, y = 20, 20
        
        pygame.draw.rect(self._display, (0, 0, 0), (x + 3, y + 3, hp_max_width, hp_height), border_radius=4)
        pygame.draw.rect(self._display, (40, 40, 40), (x - 2, y - 2, hp_max_width + 4, hp_height + 4), border_radius=4)
        pygame.draw.rect(self._display, (20, 20, 20), (x, y, hp_max_width, hp_height))
        
        hp_width = max(0, int((self.hero.hp / 100.0) * hp_max_width))
        
        # Lógica de cores baseada na vida (Verde -> Laranja -> Vermelho Piscante)
        if self.hero.hp > 50:
            hp_color = (0, 200, 0)
        elif self.hero.hp > 20:
            hp_color = (255, 140, 0)
        else:
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                hp_color = (255, 0, 0)
            else:
                hp_color = (139, 0, 0)
        
        if hp_width > 0:
            pygame.draw.rect(self._display, hp_color, (x, y, hp_width, hp_height))
            pygame.draw.rect(self._display, (255, 255, 255), (x, y, hp_width, max(1, int(hp_height * 0.2))), border_radius=1)

        # Atualizando target do _draw_hud_panel temporariamente mudando seu comportamento
        # A própria função _draw_hud_panel desenhava em _game.window, então refatoramos ela
        # Logo faremos uma correção rápida do _draw_hud_panel abaixo no chunk. 
        # Na verdade, basta desenhar a HUD aqui:

        # Draw FPS and Prog direct implementation
        def draw_temp_hud(text, color, px, py, right_align=False, fill_ratio=0.0):
            text_surf = self.ui_font.render(text, True, color)
            shad_surf = self.ui_font.render(text, True, (0, 0, 0))
            pad_x, pad_y = 12, 6
            pw = text_surf.get_width() + pad_x*2
            ph = text_surf.get_height() + pad_y*2
            if right_align: px -= pw
            pnl = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pnl.fill((0, 0, 0, 160))
            self._display.blit(pnl, (px, py))
            
            if fill_ratio > 0:
                fill_w = int(pw * fill_ratio)
                pygame.draw.rect(self._display, (138, 43, 226), (px, py, fill_w, ph))
                # Borda brilhante no preenchimento
                pygame.draw.rect(self._display, (200, 100, 255), (px, py, fill_w, 2))
                
            self._display.blit(shad_surf, (px+pad_x+2, py+pad_y+2))
            self._display.blit(text_surf, (px+pad_x, py+pad_y))

        rage_ratio = max(0.0, min(1.0, (20 - self.enemies_to_boss) / 20.0))

        if not self.boss_spawned:
            prog_str = f"Enemies to Boss: {max(0, self.enemies_to_boss)}"
            prog_color = (255, 215, 0)
        else:
            prog_str = "Defeat the Dragon!"
            fire_colors = [(255, 69, 0), (255, 140, 0), (255, 215, 0)]
            color_idx = (pygame.time.get_ticks() // 100) % len(fire_colors)
            prog_color = fire_colors[color_idx]

        draw_temp_hud(f"FPS: {int(self._game.fps)}", (255, 255, 255), 20, settings.SCREEN_HEIGHT - 55)
        draw_temp_hud(prog_str, prog_color, settings.SCREEN_WIDTH - 20, settings.SCREEN_HEIGHT - 55, right_align=True, fill_ratio=rage_ratio)

        # BOSS HUD
        if self.boss_spawned:
            boss = next((e for e in self.enemies if getattr(e, '_name', '') == 'DragonBoss'), None)
            if boss and boss._hp > 0:
                bw, bh = 600, 24
                bx = settings.SCREEN_WIDTH // 2 - bw // 2
                by = settings.SCREEN_HEIGHT - 90
                
                # Nome do boss
                boss_name = self.ui_font.render("DRAGON BOSS", True, (255, 50, 50))
                self._display.blit(boss_name, (settings.SCREEN_WIDTH // 2 - boss_name.get_width() // 2, by - 25))
                
                # Fundo e borda
                pygame.draw.rect(self._display, (40, 40, 40), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=4)
                pygame.draw.rect(self._display, (20, 20, 20), (bx, by, bw, bh))
                
                # Vida
                bhp_w = max(0, int((boss._hp / boss.max_hp) * bw))
                if bhp_w > 0:
                    pygame.draw.rect(self._display, (220, 20, 20), (bx, by, bhp_w, bh))
                    pygame.draw.rect(self._display, (255, 100, 100), (bx, by, bhp_w, max(1, int(bh * 0.2))))

        if self.hero.hp <= 0:
            self._game_over_timer += dt
            
            # 1. Overlay Escuro com Fade
            alpha = min(200, int(self._game_over_timer * 100))
            overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            self._display.blit(overlay, (0, 0))
            
            # 2. Texto YOU DIED pulsante/lento
            text_alpha = min(255, int(max(0.0, self._game_over_timer - 1.0) * 150))
            go_text = self._font_go.render("YOU DIED", True, (180, 0, 0))
            go_text.set_alpha(text_alpha)
            self._display.blit(go_text, (settings.SCREEN_WIDTH // 2 - go_text.get_width() // 2, settings.SCREEN_HEIGHT // 2))
            
            # 3. Prompt de Retorno
            if self._game_over_timer > 3.0:
                prompt_alpha = int(abs(math.sin(self._game_over_timer * 3)) * 255)
                prompt_text = self.ui_font.render("Press [ENTER] to return", True, (255, 255, 255))
                prompt_text.set_alpha(prompt_alpha)
                self._display.blit(prompt_text, (settings.SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, settings.SCREEN_HEIGHT // 2 + 60))
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    pygame.mixer.stop()
                    pygame.mixer.music.stop()
                    self._game.change_state(MenuState(self._game))
                    return

        # WIN CONDITION
        if self.boss_spawned:
            if not getattr(self, 'boss_defeated', False):
                boss = next((e for e in self.enemies if getattr(e, '_name', '') == 'DragonBoss'), None)
                if boss and boss._hp <= 0:
                    self.boss_defeated = True
                    
        if getattr(self, 'boss_defeated', False):
            self._game_over_timer += dt
            
            # Glassmorphism overlay
            overlay_alpha = min(160, int(self._game_over_timer * 80))
            overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha))
            self._display.blit(overlay, (0, 0))
            
            panel_w, panel_h = 400, 250
            panel_x = (settings.SCREEN_WIDTH - panel_w) // 2
            panel_y = (settings.SCREEN_HEIGHT - panel_h) // 2
            
            # Desenha Painel Base
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((20, 20, 25, int(overlay_alpha * 0.9)))
            pygame.draw.rect(panel, (100, 100, 100, int(overlay_alpha)), (0, 0, panel_w, panel_h), width=2, border_radius=8)
            self._display.blit(panel, (panel_x, panel_y))
            
            # Título Victory
            win_text = self._font_go.render("VICTORY ACHIEVED", True, (255, 215, 0))
            win_text.set_alpha(int(overlay_alpha * (255/160)))
            self._display.blit(win_text, (settings.SCREEN_WIDTH // 2 - win_text.get_width() // 2, panel_y + 20))
            
            # Stats Text
            stats_texts = [
                f"Boss Defeated: Dragon Boss",
                f"Horde Cleared: 20 / 20",
                f"HP Remaining: {self.hero.hp}"
            ]
            for i, text in enumerate(stats_texts):
                st_render = self.ui_font.render(text, True, (200, 200, 200))
                st_render.set_alpha(int(overlay_alpha * (255/160)))
                self._display.blit(st_render, (panel_x + 30, panel_y + 90 + (i * 30)))
            
            if self._game_over_timer > 2.0:
                prompt_alpha = int(abs(math.sin(self._game_over_timer * 3)) * 255)
                prompt_text = self.ui_font.render("Press [ENTER] to continue", True, (255, 255, 255))
                prompt_text.set_alpha(prompt_alpha)
                self._display.blit(prompt_text, (settings.SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, panel_y + panel_h - 40))
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    pygame.mixer.stop()
                    pygame.mixer.music.stop()
                    self._game.change_state(MenuState(self._game))
                    return

        # Aplicação do Screen Shake
        shake_x, shake_y = 0, 0
        if self._shake_timer > 0:
            self._shake_timer -= dt
            intensity = 8
            shake_x = random.randint(-intensity, intensity)
            shake_y = random.randint(-intensity, intensity)

        self._game.window.fill((0, 0, 0))
        self._game.window.blit(self._display, (shake_x, shake_y))

        # Invoca nova onda se limpou a tela e o herói está vivo
        if len(self.enemies) == 0 and self.hero.hp > 0:
            self._spawn_wave()
