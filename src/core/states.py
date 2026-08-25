"""State machine implementation for Castle Night.

Provides concrete state classes (MenuState, LevelState) orchestrating
the main game loop, user inputs, entity updates, and UI rendering.
"""
from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

import pygame

from src.core.mediator import CombatMediator
from src.core.proxy import LevelProgressProxy
from src.entities.entity import Entity
from src.entities.factory import EntityFactory
from src.entities.hero import Hero
from src.ui.hud import HUDManager
from src.utils import settings
from src.utils.asset_loader import AssetLoader

if TYPE_CHECKING:
    from src.core.game import Game


class IState(ABC):
    """Interface for the State design pattern delegating main loop execution to concrete states."""

    @abstractmethod
    def run(self, dt: float) -> None:
        """Execute a single frame event polling, kinematic update, and render pass.

        Args:
            dt: Delta time elapsed since last frame in fractional seconds.
        """
        pass


class MenuState(IState):
    """Medieval main menu state featuring interactive navigation, controls modal, and retro aesthetics."""

    def __init__(self, game: Game) -> None:
        """Initialize menu resources, fonts, background surfaces, and music streaming.

        Args:
            game: Central Game engine instance controlling window and state transitions.
        """
        self._game: Game = game
        self._font_small: pygame.font.Font = pygame.font.Font(None, 22)
        self._font: pygame.font.Font = pygame.font.Font(None, 32)
        self._font_large: pygame.font.Font = pygame.font.Font(None, 44)
        self._font_title: pygame.font.Font = pygame.font.Font(None, 76)

        # Scale background image to current window dimensions
        raw_bg = AssetLoader.load_image("sprites/background/Menu.png")
        self._bg_image: pygame.Surface = pygame.transform.smoothscale(
            raw_bg,
            (self._game.window.get_width(), self._game.window.get_height()),
        )

        # Dedicated pre-allocated fullscreen overlay surface for glassmorphism
        self._overlay: pygame.Surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
            pygame.SRCALPHA,
        )

        self._menu_options: list[str] = [
            "INICIAR JORNADA",
            "GUIA DE CONTROLES",
            "SAIR DO JOGO",
        ]
        self._selected_index: int = 0
        self._show_controls_modal: bool = False

        # Play dedicated menu BGM via safe AssetLoader method
        AssetLoader.play_music("audio/Sound-Menu.mp3", loops=-1)

    @property
    def selected_index(self) -> int:
        """Current highlighted menu item index.

        Returns:
            int: 0-based index of highlighted option.
        """
        return self._selected_index

    def draw_controls(self) -> None:
        """Render medieval glassmorphic controls guide overlay with styled key badges."""
        screen_w = settings.SCREEN_WIDTH
        screen_h = settings.SCREEN_HEIGHT

        # 1. Dark Backdrop Overlay
        modal_overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        modal_overlay.fill((0, 0, 0, 180))
        self._game.window.blit(modal_overlay, (0, 0))

        # 2. Medieval Container Panel (Broad panel to accommodate all legends)
        modal_w, modal_h = 660, 460
        modal_x = (screen_w - modal_w) // 2
        modal_y = (screen_h - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        panel_bg = pygame.Surface((modal_w, modal_h), pygame.SRCALPHA)
        panel_bg.fill((18, 16, 24, 235))
        self._game.window.blit(panel_bg, modal_rect.topleft)
        pygame.draw.rect(self._game.window, (218, 165, 32), modal_rect, width=2, border_radius=8)

        # 3. Header Title
        title_surf = self._font_large.render("GUIA DE CONTROLES", True, (255, 215, 0))
        title_shad = self._font_large.render("GUIA DE CONTROLES", True, (0, 0, 0))
        tx = modal_x + (modal_w - title_surf.get_width()) // 2
        ty = modal_y + 20
        self._game.window.blit(title_shad, (tx + 2, ty + 2))
        self._game.window.blit(title_surf, (tx, ty))

        # Gold accent divider line
        div_y = ty + 38
        pygame.draw.line(self._game.window, (180, 140, 40), (modal_x + 40, div_y), (modal_x + modal_w - 40, div_y), 2)
        pygame.draw.rect(self._game.window, (255, 215, 0), (screen_w // 2 - 3, div_y - 2, 6, 6))

        # 4. Instructions Mapping Table
        instructions = [
            ("A / D", "Mover para Esquerda / Direita"),
            ("Space", "Pular / Salto"),
            ("Left Shift", "Correr (Dash Attack)"),
            ("Key C", "Bloquear / Defender com Escudo"),
            ("Mouse Esq.", "Ataque com Espada 1"),
            ("Mouse Dir.", "Ataque Especial 2"),
            ("ESC", "Pausar o Jogo / Voltar"),
        ]

        start_y = modal_y + 75
        center_split_x = modal_x + 230

        for key_text, action_text in instructions:
            key_surface = self._font.render(key_text, True, (255, 255, 255))
            action_surface = self._font.render(action_text, True, (225, 173, 1))
            action_shadow = self._font.render(action_text, True, (0, 0, 0))

            box_padding_x, box_padding_y = 10, 4
            box_width = key_surface.get_width() + (box_padding_x * 2)
            box_height = key_surface.get_height() + (box_padding_y * 2)
            gap = 14

            start_x = center_split_x - box_width - gap

            # Key Box shadow and background
            pygame.draw.rect(
                self._game.window,
                (0, 0, 0),
                pygame.Rect(start_x + 2, start_y + 2, box_width, box_height),
                border_radius=5,
            )
            key_rect = pygame.Rect(start_x, start_y, box_width, box_height)
            pygame.draw.rect(self._game.window, (160, 20, 20), key_rect, border_radius=5)
            pygame.draw.rect(self._game.window, (255, 215, 0), key_rect, width=1, border_radius=5)

            self._game.window.blit(key_surface, (start_x + box_padding_x, start_y + box_padding_y))

            action_x = center_split_x + gap
            action_y = start_y + box_padding_y
            self._game.window.blit(action_shadow, (action_x + 2, action_y + 2))
            self._game.window.blit(action_surface, (action_x, action_y))

            start_y += box_height + 10

        # 5. Pulsating Return Prompt
        ticks = pygame.time.get_ticks()
        pulse = int(abs(math.sin(ticks / 300.0)) * 155) + 100
        close_surf = self._font_small.render("Pressione [ESC] ou [ENTER] para fechar", True, (255, 255, 255))
        close_surf.set_alpha(pulse)
        cx = modal_x + (modal_w - close_surf.get_width()) // 2
        cy = modal_y + modal_h - 30
        self._game.window.blit(close_surf, (cx, cy))


    def run(self, dt: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._game.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if self._show_controls_modal:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_BACKSPACE):
                        self._show_controls_modal = False
                else:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self._selected_index = (self._selected_index - 1) % len(self._menu_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self._selected_index = (self._selected_index + 1) % len(self._menu_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._activate_option(self._selected_index)
                        return
                    elif event.key == pygame.K_1:
                        self._activate_option(0)
                        return
                    elif event.key == pygame.K_2:
                        self._activate_option(1)
                    elif event.key in (pygame.K_3, pygame.K_ESCAPE):
                        self._activate_option(2)
                        return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._show_controls_modal:
                    self._show_controls_modal = False
                else:
                    mx, my = pygame.mouse.get_pos()
                    btn_w, btn_h = 320, 48
                    btn_x = (settings.SCREEN_WIDTH - btn_w) // 2
                    start_y = 280
                    for i in range(len(self._menu_options)):
                        opt_y = start_y + (i * (btn_h + 14))
                        if pygame.Rect(btn_x, opt_y, btn_w, btn_h).collidepoint(mx, my):
                            self._activate_option(i)
                            return

        # 1. Background image
        self._game.window.blit(self._bg_image, (0, 0))

        # 2. Translucent glassmorphism overlay
        self._overlay.fill((10, 10, 16, 175))
        self._game.window.blit(self._overlay, (0, 0))

        # 3. Imposing Gothic/Medieval Game Title
        title_text = "CASTLE NIGHT"
        title_surf = self._font_title.render(title_text, True, (255, 215, 0))
        title_shad = self._font_title.render(title_text, True, (0, 0, 0))
        tx = (settings.SCREEN_WIDTH - title_surf.get_width()) // 2
        ty = 85
        self._game.window.blit(title_shad, (tx + 3, ty + 3))
        self._game.window.blit(title_surf, (tx, ty))

        # Subtitle banner
        sub_text = "— Demo 2D Metroidvania em Pygame —"
        sub_surf = self._font_small.render(sub_text, True, (200, 190, 210))
        sx = (settings.SCREEN_WIDTH - sub_surf.get_width()) // 2
        sy = ty + 70
        self._game.window.blit(sub_surf, (sx, sy))

        # 4. Interactive Medieval Navigation Menu
        btn_w, btn_h = 320, 48
        btn_x = (settings.SCREEN_WIDTH - btn_w) // 2
        start_y = 280

        ticks = pygame.time.get_ticks()
        pulse_alpha = int(abs(math.sin(ticks / 280.0)) * 90) + 165

        for i, option_text in enumerate(self._menu_options):
            opt_y = start_y + (i * (btn_h + 14))
            btn_rect = pygame.Rect(btn_x, opt_y, btn_w, btn_h)

            is_selected = (i == self._selected_index)

            # Check mouse hover for responsive feedback
            mx, my = pygame.mouse.get_pos()
            if btn_rect.collidepoint(mx, my):
                self._selected_index = i
                is_selected = True

            # Button drop shadow
            shadow_rect = pygame.Rect(btn_x + 3, opt_y + 3, btn_w, btn_h)
            pygame.draw.rect(self._game.window, (0, 0, 0), shadow_rect, border_radius=8)

            if is_selected:
                btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                btn_surf.fill((65, 45, 20, pulse_alpha))
                self._game.window.blit(btn_surf, btn_rect.topleft)
                pygame.draw.rect(self._game.window, (255, 215, 0), btn_rect, width=2, border_radius=8)

                label_text = f">  {option_text}  <"
                label_color = (255, 225, 90)
            else:
                btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                btn_surf.fill((22, 22, 32, 160))
                self._game.window.blit(btn_surf, btn_rect.topleft)
                pygame.draw.rect(self._game.window, (80, 85, 105), btn_rect, width=1, border_radius=8)

                label_text = option_text
                label_color = (230, 230, 240)

            opt_surf = self._font.render(label_text, True, label_color)
            opt_shad = self._font.render(label_text, True, (0, 0, 0))
            lx = btn_x + (btn_w - opt_surf.get_width()) // 2
            ly = opt_y + (btn_h - opt_surf.get_height()) // 2
            self._game.window.blit(opt_shad, (lx + 2, ly + 2))
            self._game.window.blit(opt_surf, (lx, ly))

        # 5. Bottom Navigation Hints
        nav_hint = "[W/S / Setas] Navegar  •  [ENTER] Selecionar  •  [1-3] Atalhos"
        hint_surf = self._font_small.render(nav_hint, True, (160, 165, 185))
        hx = (settings.SCREEN_WIDTH - hint_surf.get_width()) // 2
        hy = settings.SCREEN_HEIGHT - 45
        self._game.window.blit(hint_surf, (hx, hy))

        # 6. Controls Modal Overlay (if toggled)
        if self._show_controls_modal:
            self.draw_controls()

    def _activate_option(self, index: int) -> None:
        """Handle execution of the selected menu item."""
        if index == 0:  # Iniciar Jornada
            AssetLoader.stop_music()
            pygame.event.clear()
            self._game.change_state(LevelState(self._game))
        elif index == 1:  # Guia de Controles
            self._show_controls_modal = True
        elif index == 2:  # Sair do Jogo
            self._game.quit()


class LevelState(IState):
    """Orchestrator state for active gameplay, managing entities, combat, pause, and level progression."""

    def __init__(self, game: Game) -> None:
        """Initialize level state, player entity, proxy, mediator, HUD manager, and parallax backgrounds.

        Args:
            game: Central Game engine instance controlling window and state transitions.
        """
        self._game: Game = game
        self.hero: Hero = EntityFactory.create_hero(
            x=settings.SCREEN_WIDTH // 2,
            y=settings.FLOOR_HEIGHT,
        )
        self.mediator: CombatMediator = CombatMediator(self.hero)
        self._proxy: LevelProgressProxy = LevelProgressProxy(EntityFactory)
        self._hud: HUDManager = HUDManager()

        self.enemies: List[Entity] = []
        self._shake_timer: float = 0.0
        self._game_over_timer: float = 0.0
        self._boss_music_started: bool = False

        # In-game pause modal management
        self._is_paused: bool = False
        self._pause_selected_index: int = 0

        # Pre-scale parallax background surfaces to screen resolution
        res = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self._display: pygame.Surface = pygame.Surface(res)
        self._bg_layers: list[pygame.Surface] = [
            pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/Background.png'), res),
            pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/Mountains.png'), res),
            pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/WallWindows.png'), res),
            pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/ColumnsFlags.png'), res),
            pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/StatueDragon.png'), res),
            pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/Candeliar.png'), res),
            pygame.transform.smoothscale(AssetLoader.load_image('sprites/background/Floor.png'), res),
        ]

        AssetLoader.play_music('audio/Sound-Normal.mp3', loops=-1)

        # Spawn initial wave
        self._spawn_wave()

    @property
    def is_paused(self) -> bool:
        """Whether gameplay is currently paused.

        Returns:
            bool: True if game loop is paused, False otherwise.
        """
        return self._is_paused

    @is_paused.setter
    def is_paused(self, value: bool) -> None:
        """Set in-game pause status flag.

        Args:
            value: Boolean value for paused state.
        """
        self._is_paused = value

    @property
    def pause_selected_index(self) -> int:
        """Currently highlighted option in the Pause modal menu.

        Returns:
            int: 0-based index of highlighted pause option.
        """
        return self._pause_selected_index

    @pause_selected_index.setter
    def pause_selected_index(self, value: int) -> None:
        """Set highlighted option in the Pause modal menu.

        Args:
            value: 0-based integer option index.
        """
        self._pause_selected_index = value

    @property
    def boss_spawned(self) -> bool:
        """Whether the DragonBoss encounter has been triggered.

        Returns:
            bool: True if boss has spawned, False otherwise.
        """
        return self._proxy.boss_spawned

    @boss_spawned.setter
    def boss_spawned(self, value: bool) -> None:
        """Set boss spawned state flag.

        Args:
            value: Boolean value for boss spawned status.
        """
        self._proxy.boss_spawned = value

    @property
    def boss_defeated(self) -> bool:
        """Whether the DragonBoss has been defeated.

        Returns:
            bool: True if boss is slain, False otherwise.
        """
        return self._proxy.boss_defeated

    @boss_defeated.setter
    def boss_defeated(self, value: bool) -> None:
        """Set boss defeated state flag.

        Args:
            value: Boolean value for boss defeated status.
        """
        self._proxy.boss_defeated = value

    @property
    def enemies_to_boss(self) -> int:
        """Number of regular enemies remaining before boss fight.

        Returns:
            int: Remaining enemy quota.
        """
        return self._proxy.enemies_remaining

    @enemies_to_boss.setter
    def enemies_to_boss(self, value: int) -> None:
        """Set remaining enemies quota by adjusting proxy defeated count.

        Args:
            value: Desired remaining enemy count.
        """
        self._proxy._enemies_killed = max(0, self._proxy.total_enemies - value)

    def _spawn_wave(self) -> None:
        """Delegate enemy wave or boss generation to LevelProgressProxy."""
        new_enemies = self._proxy.request_spawn(self.hero, self.enemies)
        if self._proxy.boss_spawned and not self._boss_music_started:
            self._boss_music_started = True
            self._shake_timer = settings.SCREEN_SHAKE_DURATION
            AssetLoader.play_music('audio/Sound-Boss.mp3', loops=-1)
        self.enemies.extend(new_enemies)

    def _return_to_menu(self) -> None:
        """Stop all audio playback channels, clear pending input events, and return to main menu."""
        AssetLoader.stop_all_sounds()
        AssetLoader.stop_music()
        pygame.event.clear()
        self._game.change_state(MenuState(self._game))

    def _render_hud(self) -> None:
        """Render common HUD elements (Player HP, Wave meter, FPS badge, Boss Gauge)."""
        self._hud.draw_player_hp(self._display, hp=self.hero.hp, max_hp=self.hero.max_hp)
        self._hud.draw_wave_progress(
            self._display,
            enemies_remaining=self._proxy.enemies_remaining,
            total_enemies=self._proxy.total_enemies,
            is_boss_active=self._proxy.boss_spawned,
        )
        self._hud.draw_fps(self._display, fps=self._game.fps)

        if self._proxy.boss_spawned:
            boss = next(
                (e for e in self.enemies if getattr(e, 'is_boss', False) or getattr(e, '_name', '') == 'DragonBoss'),
                None,
            )
            if boss and boss.hp > 0:
                self._hud.draw_boss_hp(self._display, hp=boss.hp, max_hp=boss.max_hp, boss_name="DRAGON BOSS")

    def run(self, dt: float) -> None:
        """Execute gameplay frame lifecycle: event handling, physics simulation, combat, and rendering.

        Args:
            dt: Delta time elapsed since last frame in fractional seconds.
        """
        # 1. Process events (including Pause toggling and navigation)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._game.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._is_paused = not self._is_paused
                    if self._is_paused:
                        AssetLoader.pause_music()
                    else:
                        AssetLoader.unpause_music()
                elif self._is_paused:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self._pause_selected_index = (self._pause_selected_index - 1) % 2
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self._pause_selected_index = (self._pause_selected_index + 1) % 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self._pause_selected_index == 0:  # Continuar
                            self._is_paused = False
                            AssetLoader.unpause_music()
                        elif self._pause_selected_index == 1:  # Voltar ao Menu
                            self._return_to_menu()
                            return

        # 2. Render background layers
        for layer in self._bg_layers:
            self._display.blit(layer, (0, 0))

        # 3. Paused State Branch (Freeze physics, timers, wave spawn, and combat)
        if self._is_paused:
            self.hero.draw(self._display)
            for enemy in self.enemies:
                enemy.draw(self._display)
                self._hud.draw_enemy_health_bar(self._display, enemy)

            # Draw standard HUD underneath modal via extracted helper
            self._render_hud()

            self._game.window.fill((0, 0, 0))
            self._game.window.blit(self._display, (0, 0))

            # Draw Pause Modal onto main window
            self._hud.draw_pause_menu(self._game.window, self._pause_selected_index)
            return

        # 4. Active Gameplay: Update and render entities
        is_victory = self._proxy.is_victory
        self.hero.update(dt)
        self.hero.draw(self._display)

        for enemy in self.enemies:
            is_boss = getattr(enemy, 'is_boss', False) or getattr(enemy, '_name', '') == 'DragonBoss'
            enemy_dt = 0.0 if (self.hero.hp <= 0 or is_victory) and not is_boss else dt
            enemy.update(enemy_dt)
            enemy.draw(self._display)
            self._hud.draw_enemy_health_bar(self._display, enemy)

        # 5. Clean up defeated entities via proxy registration
        alive_enemies: list[Entity] = []
        for enemy in self.enemies:
            if enemy.is_removable:
                self._proxy.register_kill(enemy)
            else:
                alive_enemies.append(enemy)
        self.enemies = alive_enemies

        # 6. Resolve combat collisions
        if self.hero.hp > 0 and not is_victory:
            self.mediator.update(self.enemies)

        # 7. Render HUD elements via extracted helper
        self._render_hud()

        # 8. Handle Game Over and Victory screens
        if self.hero.hp <= 0:
            self._game_over_timer += dt
            self._hud.draw_game_over(self._display, timer=self._game_over_timer)
            if self._game_over_timer > 3.0 and pygame.key.get_pressed()[pygame.K_RETURN]:
                self._return_to_menu()
                return

        if is_victory:
            self._game_over_timer += dt
            self._hud.draw_victory_screen(
                self._display,
                timer=self._game_over_timer,
                boss_name="Dragon Boss",
                horde_cleared=self._proxy.defeated_count,
                total_horde=self._proxy.total_enemies,
                hp_remaining=self.hero.hp,
            )
            if self._game_over_timer > 2.0 and pygame.key.get_pressed()[pygame.K_RETURN]:
                self._return_to_menu()
                return

        # 9. Apply screen shake and blit to main window
        shake_x, shake_y = 0, 0
        if self._shake_timer > 0:
            self._shake_timer -= dt
            intensity = settings.SCREEN_SHAKE_INTENSITY
            shake_x = random.randint(-intensity, intensity)
            shake_y = random.randint(-intensity, intensity)

        self._game.window.fill((0, 0, 0))
        self._game.window.blit(self._display, (shake_x, shake_y))

        # 10. Trigger next wave if floor cleared
        if len(self.enemies) == 0 and self.hero.hp > 0:
            self._spawn_wave()

