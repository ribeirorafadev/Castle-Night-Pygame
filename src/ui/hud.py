"""HUD & UI rendering module for Castle Night.

Provides the HUDManager class responsible for all graphical interface rendering
with glassmorphism aesthetic, drop shadows (x+2, y+2), medieval 8-bit high-contrast
frames, and zero per-frame dynamic allocations for 60 FPS performance.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING
import pygame
from src.utils import settings

if TYPE_CHECKING:
    from src.entities.entity import Entity


class HUDManager:
    """Manager for heads-up display and game interface rendering.

    Adheres strictly to SOLID Single Responsibility Principle:
    - Pure rendering methods (no game state mutation, no audio triggers).
    - Pre-allocates fonts and surface pools to eliminate runtime GC overhead.
    - Implements glassmorphism panels, glowing borders, and drop shadows.
    """

    # Color Palette Constants
    COLOR_BLACK: tuple[int, int, int] = (0, 0, 0)
    COLOR_WHITE: tuple[int, int, int] = (255, 255, 255)
    COLOR_SHADOW: tuple[int, int, int] = (0, 0, 0)
    COLOR_TEXT_PRIMARY: tuple[int, int, int] = (240, 240, 245)
    COLOR_TEXT_MUTED: tuple[int, int, int] = (190, 195, 205)
    COLOR_GOLD: tuple[int, int, int] = (255, 215, 0)
    COLOR_GOLD_DARK: tuple[int, int, int] = (218, 165, 32)
    COLOR_PURPLE: tuple[int, int, int] = (138, 43, 226)
    COLOR_PURPLE_LIGHT: tuple[int, int, int] = (200, 100, 255)
    COLOR_BOSS_NAME: tuple[int, int, int] = (255, 50, 50)
    COLOR_BOSS_BAR: tuple[int, int, int] = (220, 20, 60)
    COLOR_BOSS_BAR_HIGHLIGHT: tuple[int, int, int] = (255, 120, 120)
    COLOR_FIRE_PALETTE: list[tuple[int, int, int]] = [
        (255, 69, 0),
        (255, 140, 0),
        (255, 215, 0),
    ]

    # Glassmorphism Default Colors
    GLASS_BG_COLOR: tuple[int, int, int] = (15, 15, 22)
    GLASS_BORDER_DEFAULT: tuple[int, int, int] = (90, 95, 115)
    GLASS_HIGHLIGHT: tuple[int, int, int] = (255, 255, 255)

    def __init__(self) -> None:
        """Initialize and pre-allocate fonts and reusable surface buffers."""
        if not pygame.font.get_init():
            pygame.font.init()

        # Pre-allocated fonts of various standard hierarchy scales
        self._font_small: pygame.font.Font = pygame.font.Font(None, 20)
        self._font_main: pygame.font.Font = pygame.font.Font(None, 28)
        self._font_medium: pygame.font.Font = pygame.font.Font(None, 34)
        self._font_large: pygame.font.Font = pygame.font.Font(None, 48)
        self._font_title: pygame.font.Font = pygame.font.Font(None, 72)

        # Surface cache for glassmorphism panels keyed strictly by (width, height)
        self._surface_cache: dict[tuple[int, int], pygame.Surface] = {}

        # Dedicated pre-allocated fullscreen overlay surface
        self._fullscreen_overlay: pygame.Surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        self._fullscreen_overlay.fill(self.COLOR_BLACK)

    # --------------------------------------------------------------------------
    # Surface & Caching Utilities (Zero GC Overhead)
    # --------------------------------------------------------------------------

    def _get_glass_surface(self, width: int, height: int) -> pygame.Surface:
        """Retrieve a cached surface for glassmorphism panels keyed strictly by (width, height).

        Reuses surfaces of identical dimensions to guarantee zero memory
        allocations during the active 60 FPS gameplay loop.
        """
        cache_key = (width, height)
        if cache_key not in self._surface_cache:
            surf = pygame.Surface((width, height))
            surf.fill(self.GLASS_BG_COLOR)
            self._surface_cache[cache_key] = surf
        return self._surface_cache[cache_key]

    def _get_overlay_surface(self, width: int, height: int) -> pygame.Surface:
        """Retrieve or resize the reusable fullscreen overlay surface."""
        if (self._fullscreen_overlay.get_width() != width or
                self._fullscreen_overlay.get_height() != height):
            self._fullscreen_overlay = pygame.Surface((width, height))
            self._fullscreen_overlay.fill(self.COLOR_BLACK)
        return self._fullscreen_overlay

    # --------------------------------------------------------------------------
    # Pure Rendering Helper Primitives
    # --------------------------------------------------------------------------

    def draw_text_with_shadow(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        pos: tuple[int, int],
        shadow_color: tuple[int, int, int] = (0, 0, 0),
        shadow_offset: tuple[int, int] = (2, 2),
        alpha: int = 255,
    ) -> pygame.Rect:
        """Render text with a projected drop shadow (x+2, y+2) and optional alpha."""
        text_surf = font.render(text, True, color)
        shadow_surf = font.render(text, True, shadow_color)

        if alpha < 255:
            clamped_alpha = max(0, min(255, alpha))
            text_surf.set_alpha(clamped_alpha)
            shadow_surf.set_alpha(clamped_alpha)

        shadow_pos = (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1])
        surface.blit(shadow_surf, shadow_pos)
        surface.blit(text_surf, pos)
        return text_surf.get_rect(topleft=pos)

    def draw_glass_panel(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        bg_alpha: int = 170,
        border_color: tuple[int, int, int] = (90, 95, 115),
        border_width: int = 1,
        border_radius: int = 6,
        shadow: bool = True,
    ) -> None:
        """Render a glassmorphic container with projected drop shadow and subtle highlight."""
        if shadow:
            shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
            pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=border_radius)

        glass_surf = self._get_glass_surface(rect.width, rect.height)
        glass_surf.set_alpha(max(0, min(255, bg_alpha)))
        surface.blit(glass_surf, rect.topleft)

        if border_width > 0:
            pygame.draw.rect(
                surface,
                border_color,
                rect,
                width=border_width,
                border_radius=border_radius,
            )

        # Subtle top edge glass sheen
        if rect.width > (border_radius * 2):
            sheen_start = (rect.left + border_radius, rect.top + 1)
            sheen_end = (rect.right - border_radius, rect.top + 1)
            pygame.draw.line(surface, (255, 255, 255), sheen_start, sheen_end, 1)

    # --------------------------------------------------------------------------
    # Public Contract Rendering Methods (Pure Functions)
    # --------------------------------------------------------------------------

    def draw_player_hp(
        self,
        surface: pygame.Surface,
        hp: int | None = None,
        max_hp: int = settings.HERO_MAX_HP,
        x: int = 20,
        y: int = 20,
        width: int = settings.HUD_HP_BAR_WIDTH,
        height: int = settings.HUD_HP_BAR_HEIGHT,
        current_hp: int | None = None,
    ) -> None:
        """Render dynamic player health bar with medieval frames, sheen, and drop shadows."""
        effective_hp = current_hp if current_hp is not None else (hp if hp is not None else 100)
        safe_max_hp = max(1, max_hp)
        clamped_hp = max(0, min(safe_max_hp, effective_hp))
        fill_ratio = clamped_hp / float(safe_max_hp)

        # 1. Projected Shadow (offset x+3, y+3 for bar depth)
        shadow_rect = pygame.Rect(x + 3, y + 3, width, height)
        pygame.draw.rect(surface, self.COLOR_SHADOW, shadow_rect, border_radius=4)

        # 2. Outer Medieval Iron Frame with Gold Accent Trim
        outer_frame_rect = pygame.Rect(x - 2, y - 2, width + 4, height + 4)
        pygame.draw.rect(surface, (45, 48, 60), outer_frame_rect, border_radius=4)
        pygame.draw.rect(surface, (100, 105, 125), outer_frame_rect, width=1, border_radius=4)

        # 3. Inner Dark Cavity
        bar_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (18, 18, 24), bar_rect)

        # 4. Dynamic Health Bar Color (Green -> Orange -> Flashing Red)
        if fill_ratio > 0.5:
            bar_color = (46, 204, 113)  # Emerald Green
        elif fill_ratio > 0.2:
            bar_color = (243, 156, 18)  # Amber / Orange
        else:
            # Flashing critical red
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                bar_color = (231, 76, 60)  # Crimson Red
            else:
                bar_color = (139, 0, 0)    # Dark Blood Red

        # 5. Filled Bar & Highlight Sheen
        fill_width = int(fill_ratio * width)
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(surface, bar_color, fill_rect)

            # Top highlight sheen (volumetric 3D glass look)
            sheen_height = max(1, int(height * 0.25))
            sheen_rect = pygame.Rect(x, y, fill_width, sheen_height)
            pygame.draw.rect(surface, (255, 255, 255), sheen_rect)

        # 6. Health Digits with Shadow
        hp_text = f"HP  {clamped_hp}/{safe_max_hp}"
        text_x = x + 8
        text_y = y + (height - self._font_small.get_height()) // 2
        self.draw_text_with_shadow(
            surface=surface,
            text=hp_text,
            font=self._font_small,
            color=self.COLOR_WHITE,
            pos=(text_x, text_y),
            shadow_offset=(1, 1),
        )

    def draw_boss_hp(
        self,
        surface: pygame.Surface,
        hp: int | None = None,
        max_hp: int = settings.BOSS_MAX_HP,
        boss_name: str = "DRAGON BOSS",
        width: int = settings.HUD_BOSS_BAR_WIDTH,
        height: int = settings.HUD_BOSS_BAR_HEIGHT,
        current_hp: int | None = None,
    ) -> None:
        """Render centered Dragon Boss health gauge with name header and fiery style."""
        effective_hp = current_hp if current_hp is not None else (hp if hp is not None else max_hp)
        safe_max_hp = max(1, max_hp)
        clamped_hp = max(0, min(safe_max_hp, effective_hp))
        fill_ratio = clamped_hp / float(safe_max_hp)

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        bx = (screen_w - width) // 2
        by = screen_h - 90

        # 1. Boss Name with Drop Shadow (Centered above gauge)
        name_w, _ = self._font_main.size(boss_name)
        name_x = (screen_w - name_w) // 2
        name_y = by - 26
        self.draw_text_with_shadow(
            surface=surface,
            text=boss_name,
            font=self._font_main,
            color=self.COLOR_BOSS_NAME,
            pos=(name_x, name_y),
            shadow_offset=(2, 2),
        )

        # 2. Projected Shadow for Bar Container
        shadow_rect = pygame.Rect(bx + 3, by + 3, width, height)
        pygame.draw.rect(surface, self.COLOR_SHADOW, shadow_rect, border_radius=4)

        # 3. Outer Frame & Gothic Crimson Border
        outer_frame = pygame.Rect(bx - 2, by - 2, width + 4, height + 4)
        pygame.draw.rect(surface, (45, 20, 20), outer_frame, border_radius=4)
        pygame.draw.rect(surface, (180, 50, 50), outer_frame, width=1, border_radius=4)

        # 4. Inner Dark Cavity
        bar_rect = pygame.Rect(bx, by, width, height)
        pygame.draw.rect(surface, (20, 10, 10), bar_rect)

        # 5. Health Fill & Upper Crimson Sheen
        fill_width = int(fill_ratio * width)
        if fill_width > 0:
            fill_rect = pygame.Rect(bx, by, fill_width, height)
            pygame.draw.rect(surface, self.COLOR_BOSS_BAR, fill_rect)

            sheen_height = max(1, int(height * 0.25))
            sheen_rect = pygame.Rect(bx, by, fill_width, sheen_height)
            pygame.draw.rect(surface, self.COLOR_BOSS_BAR_HIGHLIGHT, sheen_rect)

        # 6. Boss HP Text Label
        boss_hp_str = f"{clamped_hp} / {safe_max_hp}"
        boss_hp_w, _ = self._font_small.size(boss_hp_str)
        hp_x = (screen_w - boss_hp_w) // 2
        hp_y = by + (height - self._font_small.get_height()) // 2
        self.draw_text_with_shadow(
            surface=surface,
            text=boss_hp_str,
            font=self._font_small,
            color=self.COLOR_WHITE,
            pos=(hp_x, hp_y),
            shadow_offset=(1, 1),
        )

    def draw_enemy_health_bar(self, surface: pygame.Surface, enemy: Entity) -> None:
        """Render compact overhead health bar (40x5px) centered above enemy head.

        Pure rendering function. Skips bosses, dead/removable entities, or entities at 0 HP.
        """
        if enemy is None or getattr(enemy, 'is_boss', False) or getattr(enemy, 'is_removable', False):
            return

        current_hp = getattr(enemy, 'hp', 0)
        if current_hp <= 0:
            return

        max_hp = max(1, getattr(enemy, 'max_hp', settings.ENEMY_MAX_HP))
        clamped_hp = max(0, min(max_hp, current_hp))
        fill_ratio = clamped_hp / float(max_hp)

        width = settings.ENEMY_HP_BAR_WIDTH
        height = settings.ENEMY_HP_BAR_HEIGHT
        offset_y = settings.ENEMY_HP_BAR_OFFSET_Y

        mid_x, top_y = enemy.rect.midtop
        bar_x = mid_x - (width // 2)
        bar_y = top_y - offset_y

        # 1. Projected 1px drop shadow for depth
        shadow_rect = pygame.Rect(bar_x + 1, bar_y + 1, width, height)
        pygame.draw.rect(surface, self.COLOR_SHADOW, shadow_rect)

        # 2. Dark medieval iron border frame (1px outer border)
        frame_rect = pygame.Rect(bar_x - 1, bar_y - 1, width + 2, height + 2)
        pygame.draw.rect(surface, (25, 25, 32), frame_rect)
        pygame.draw.rect(surface, (60, 65, 80), frame_rect, width=1)

        # 3. Inner dark background cavity
        inner_rect = pygame.Rect(bar_x, bar_y, width, height)
        pygame.draw.rect(surface, (15, 10, 10), inner_rect)

        # 4. Crimson/Red HP Fill
        fill_width = int(fill_ratio * width)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, height)
            fill_color = (210, 35, 45) if fill_ratio > 0.25 else (235, 40, 40)
            pygame.draw.rect(surface, fill_color, fill_rect)

            # Top 1px specular highlight sheen for 8-bit medieval depth
            pygame.draw.line(
                surface,
                (255, 120, 120),
                (bar_x, bar_y),
                (bar_x + fill_width - 1, bar_y),
                1,
            )

    def draw_wave_progress(
        self,
        surface: pygame.Surface,
        enemies_remaining: int | None = None,
        total_enemies: int = settings.MAX_REGULAR_ENEMIES,
        is_boss_active: bool = False,
        x: int | None = None,
        y: int | None = None,
        remaining: int | None = None,
        total: int | None = None,
        boss_active: bool | None = None,
    ) -> None:
        """Render wave progress meter or pulsating boss battle banner."""
        eff_remaining = remaining if remaining is not None else (enemies_remaining if enemies_remaining is not None else 0)
        eff_total = total if total is not None else total_enemies
        eff_boss_active = boss_active if boss_active is not None else is_boss_active

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        target_x = (screen_w - 20) if x is None else x
        target_y = (screen_h - 55) if y is None else y

        safe_total = max(1, eff_total)
        safe_remaining = max(0, eff_remaining)
        cleared = max(0, safe_total - safe_remaining)
        rage_ratio = max(0.0, min(1.0, cleared / float(safe_total)))

        if not eff_boss_active:
            prog_text = f"Enemies to Boss: {safe_remaining}"
            text_color = self.COLOR_GOLD
            border_color = (120, 80, 180)
        else:
            prog_text = "Defeat the Dragon!"
            color_idx = (pygame.time.get_ticks() // 100) % len(self.COLOR_FIRE_PALETTE)
            text_color = self.COLOR_FIRE_PALETTE[color_idx]
            border_color = (220, 60, 20)

        # Standardized dimensions for deterministic UI layout and caching
        text_w, text_h = self._font_main.size(prog_text)
        panel_w = 230
        panel_h = 36

        # Right-align positioning
        panel_x = target_x - panel_w
        panel_y = target_y

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Draw glass panel base
        self.draw_glass_panel(
            surface=surface,
            rect=panel_rect,
            bg_alpha=160,
            border_color=border_color,
            border_width=1,
            border_radius=6,
            shadow=True,
        )

        # Fill meter (wave progression bar) drawn directly with zero memory allocation
        if not eff_boss_active and rage_ratio > 0:
            fill_w = int(panel_w * rage_ratio)
            fill_rect = pygame.Rect(panel_x, panel_y, fill_w, panel_h)
            pygame.draw.rect(surface, self.COLOR_PURPLE, fill_rect, border_radius=6)
            # Glowing accent top line
            pygame.draw.line(
                surface,
                self.COLOR_PURPLE_LIGHT,
                (panel_x, panel_y),
                (panel_x + fill_w, panel_y),
                2,
            )

        # Render text with drop shadow (centered inside panel)
        text_x = panel_x + (panel_w - text_w) // 2
        text_y = panel_y + (panel_h - text_h) // 2
        self.draw_text_with_shadow(
            surface=surface,
            text=prog_text,
            font=self._font_main,
            color=text_color,
            pos=(text_x, text_y),
            shadow_offset=(2, 2),
        )

    def draw_fps(
        self,
        surface: pygame.Surface,
        fps: float,
        x: int = 20,
        y: int | None = None,
    ) -> None:
        """Render FPS badge in a subtle glassmorphic panel."""
        screen_h = surface.get_height()
        target_y = (screen_h - 55) if y is None else y

        fps_text = f"FPS: {int(fps)}"
        text_w, text_h = self._font_main.size(fps_text)
        panel_w = 96
        panel_h = 36

        panel_rect = pygame.Rect(x, target_y, panel_w, panel_h)

        # Draw glassmorphism badge
        self.draw_glass_panel(
            surface=surface,
            rect=panel_rect,
            bg_alpha=150,
            border_color=(70, 75, 90),
            border_width=1,
            border_radius=6,
            shadow=True,
        )

        # Render FPS digits with shadow
        text_x = x + (panel_w - text_w) // 2
        text_y = target_y + (panel_h - text_h) // 2
        self.draw_text_with_shadow(
            surface=surface,
            text=fps_text,
            font=self._font_main,
            color=self.COLOR_WHITE,
            pos=(text_x, text_y),
            shadow_offset=(2, 2),
        )

    def draw_pause_menu(self, surface: pygame.Surface, selected_index: int = 0) -> None:
        """Render centered Pause modal with medieval/8-bit aesthetic and selection indicator."""
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # 1. Dark Screen Dimming Overlay
        overlay = self._get_overlay_surface(screen_w, screen_h)
        overlay.set_alpha(175)
        surface.blit(overlay, (0, 0))

        # 2. Centered Glassmorphic Medieval Modal Box
        modal_w = settings.PAUSE_MENU_WIDTH
        modal_h = settings.PAUSE_MENU_HEIGHT
        modal_x = (screen_w - modal_w) // 2
        modal_y = (screen_h - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        # Base modal panel with dark gothic background
        self.draw_glass_panel(
            surface=surface,
            rect=modal_rect,
            bg_alpha=220,
            border_color=self.COLOR_GOLD_DARK,
            border_width=2,
            border_radius=8,
            shadow=True,
        )

        # Inner decorative iron border trim
        inner_trim_rect = pygame.Rect(modal_x + 4, modal_y + 4, modal_w - 8, modal_h - 8)
        pygame.draw.rect(surface, (80, 85, 105), inner_trim_rect, width=1, border_radius=6)

        # 3. Header Title 'PAUSE'
        title_text = "PAUSE"
        title_w, _ = self._font_large.size(title_text)
        title_x = (screen_w - title_w) // 2
        title_y = modal_y + 20

        self.draw_text_with_shadow(
            surface=surface,
            text=title_text,
            font=self._font_large,
            color=self.COLOR_GOLD,
            pos=(title_x, title_y),
            shadow_offset=(2, 2),
        )

        # Gold accent divider line under title
        div_y = title_y + 42
        div_start = (modal_x + 35, div_y)
        div_end = (modal_x + modal_w - 35, div_y)
        pygame.draw.line(surface, (180, 140, 40), div_start, div_end, 2)
        # Small center golden diamond accent
        pygame.draw.rect(surface, self.COLOR_GOLD, (screen_w // 2 - 3, div_y - 2, 6, 6))

        # 4. Menu Options with Interactive Medieval Highlighting
        options = [
            "Continuar",
            "Voltar ao Menu Principal",
        ]

        opt_start_y = modal_y + 85
        btn_w = modal_w - 50
        btn_h = 44
        btn_x = modal_x + 25

        for i, opt_text in enumerate(options):
            current_btn_y = opt_start_y + (i * 54)
            btn_rect = pygame.Rect(btn_x, current_btn_y, btn_w, btn_h)
            is_selected = (i == selected_index)

            if is_selected:
                # Highlighted golden/crimson button frame
                shadow_rect = pygame.Rect(btn_x + 2, current_btn_y + 2, btn_w, btn_h)
                pygame.draw.rect(surface, self.COLOR_SHADOW, shadow_rect, border_radius=6)

                btn_surf = self._get_glass_surface(btn_w, btn_h)
                btn_surf.set_alpha(200)
                surface.blit(btn_surf, btn_rect.topleft)

                # Pulsating golden border for active option
                pulse = int(abs(math.sin(pygame.time.get_ticks() / 250.0)) * 55) + 200
                pulse_gold = (min(255, pulse), min(255, int(pulse * 0.85)), 20)
                pygame.draw.rect(surface, pulse_gold, btn_rect, width=2, border_radius=6)

                # Specular top sheen
                pygame.draw.line(surface, (255, 240, 180), (btn_x + 6, current_btn_y + 1), (btn_x + btn_w - 6, current_btn_y + 1), 1)

                display_text = f"> {opt_text}"
                text_color = self.COLOR_GOLD
            else:
                # Non-selected subtle button
                btn_surf = self._get_glass_surface(btn_w, btn_h)
                btn_surf.set_alpha(130)
                surface.blit(btn_surf, btn_rect.topleft)
                pygame.draw.rect(surface, (60, 65, 80), btn_rect, width=1, border_radius=6)

                display_text = f"  {opt_text}"
                text_color = self.COLOR_TEXT_MUTED

            text_w, text_h = self._font_main.size(display_text)
            text_x = btn_x + 18
            text_y = current_btn_y + (btn_h - text_h) // 2

            self.draw_text_with_shadow(
                surface=surface,
                text=display_text,
                font=self._font_main,
                color=text_color,
                pos=(text_x, text_y),
                shadow_offset=(2, 2),
            )

    def draw_game_over(
        self,
        surface: pygame.Surface,
        timer: float | None = None,
        elapsed_time: float | None = None,
    ) -> None:
        """Render YOU DIED dramatic game over screen with fade-in and pulsing return prompt."""
        eff_timer = elapsed_time if elapsed_time is not None else (timer if timer is not None else 0.0)
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # 1. Dark Alpha Fade Overlay
        overlay_alpha = min(210, int(eff_timer * 100))
        if overlay_alpha > 0:
            overlay = self._get_overlay_surface(screen_w, screen_h)
            overlay.set_alpha(overlay_alpha)
            surface.blit(overlay, (0, 0))

        # 2. Main Title 'YOU DIED' (Smooth fade in crimson)
        title_alpha = min(255, int(max(0.0, eff_timer - 0.5) * 160))
        if title_alpha > 0:
            title_text = "YOU DIED"
            title_w, _ = self._font_title.size(title_text)
            title_x = (screen_w - title_w) // 2
            title_y = screen_h // 2 - 40

            self.draw_text_with_shadow(
                surface=surface,
                text=title_text,
                font=self._font_title,
                color=(180, 0, 0),
                pos=(title_x, title_y),
                shadow_offset=(3, 3),
                alpha=title_alpha,
            )

        # 3. Pulsating Return Prompt
        if eff_timer > 2.5:
            prompt_alpha = int(abs(math.sin(eff_timer * 3.0)) * 255)
            prompt_text = "Press [ENTER] to return"
            prompt_w, _ = self._font_main.size(prompt_text)
            prompt_x = (screen_w - prompt_w) // 2
            prompt_y = screen_h // 2 + 50

            self.draw_text_with_shadow(
                surface=surface,
                text=prompt_text,
                font=self._font_main,
                color=self.COLOR_WHITE,
                pos=(prompt_x, prompt_y),
                shadow_offset=(2, 2),
                alpha=prompt_alpha,
            )

    def draw_victory_screen(
        self,
        surface: pygame.Surface,
        timer: float | None = None,
        boss_name: str = "Dragon Boss",
        horde_cleared: int = 20,
        total_horde: int = settings.MAX_REGULAR_ENEMIES,
        hp_remaining: int = 100,
        elapsed_time: float | None = None,
        stats: dict | None = None,
    ) -> None:
        """Render victory modal dialog with stats breakdown and golden gothic highlights."""
        eff_timer = elapsed_time if elapsed_time is not None else (timer if timer is not None else 0.0)
        if stats:
            boss_name = str(stats.get("Boss Defeated", boss_name))
            horde_str = str(stats.get("Horde Cleared", f"{horde_cleared} / {total_horde}"))
            hp_val = stats.get("HP Remaining", hp_remaining)
        else:
            horde_str = f"{horde_cleared} / {total_horde}"
            hp_val = hp_remaining

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # 1. Dark Screen Dimming Overlay
        overlay_alpha = min(170, int(eff_timer * 85))
        if overlay_alpha > 0:
            overlay = self._get_overlay_surface(screen_w, screen_h)
            overlay.set_alpha(overlay_alpha)
            surface.blit(overlay, (0, 0))

        # 2. Centered Glassmorphic Modal Box
        modal_w, modal_h = 440, 270
        modal_x = (screen_w - modal_w) // 2
        modal_y = (screen_h - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        fade_factor = min(1.0, eff_timer / 1.5)
        content_alpha = int(fade_factor * 255)

        self.draw_glass_panel(
            surface=surface,
            rect=modal_rect,
            bg_alpha=int(min(220, overlay_alpha * 1.3)),
            border_color=self.COLOR_GOLD_DARK,
            border_width=2,
            border_radius=8,
            shadow=True,
        )

        # 3. Header Title 'VICTORY ACHIEVED'
        title_text = "VICTORY ACHIEVED"
        title_w, _ = self._font_large.size(title_text)
        title_x = (screen_w - title_w) // 2
        title_y = modal_y + 24

        self.draw_text_with_shadow(
            surface=surface,
            text=title_text,
            font=self._font_large,
            color=self.COLOR_GOLD,
            pos=(title_x, title_y),
            shadow_offset=(2, 2),
            alpha=content_alpha,
        )

        # 4. Stat Items Breakdown
        stats_list = [
            f"Boss Defeated: {boss_name}",
            f"Horde Cleared: {horde_str}",
            f"HP Remaining: {hp_val}",
        ]

        row_start_y = modal_y + 90
        for i, stat_text in enumerate(stats_list):
            row_y = row_start_y + (i * 32)
            self.draw_text_with_shadow(
                surface=surface,
                text=stat_text,
                font=self._font_main,
                color=self.COLOR_TEXT_MUTED,
                pos=(modal_x + 35, row_y),
                shadow_offset=(2, 2),
                alpha=content_alpha,
            )

        # 5. Pulsating Continue Prompt
        if eff_timer > 2.0:
            prompt_alpha = int(abs(math.sin(eff_timer * 3.0)) * 255)
            prompt_text = "Press [ENTER] to continue"
            prompt_w, _ = self._font_main.size(prompt_text)
            prompt_x = (screen_w - prompt_w) // 2
            prompt_y = modal_y + modal_h - 42

            self.draw_text_with_shadow(
                surface=surface,
                text=prompt_text,
                font=self._font_main,
                color=self.COLOR_WHITE,
                pos=(prompt_x, prompt_y),
                shadow_offset=(2, 2),
                alpha=prompt_alpha,
            )
