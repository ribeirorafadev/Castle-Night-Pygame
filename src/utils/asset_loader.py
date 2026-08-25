"""Asset manager module providing cached, path-safe, and resilient loading for Castle Night."""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple
import pygame


class DummySound:
    """Safe no-op fallback Sound object for headless or soundless environments."""

    def play(self, *args: object, **kwargs: object) -> None:
        """No-op sound playback."""
        pass

    def stop(self) -> None:
        """No-op stop playback."""
        pass

    def set_volume(self, *args: object, **kwargs: object) -> None:
        """No-op set volume."""
        pass

    def get_volume(self) -> float:
        """No-op get volume."""
        return 0.0


class AssetLoader:
    """Static manager for resolving filesystem asset paths and cached loading of images/audio.

    Adheres to Zero-Trust security:
    - Strictly prevents Path Traversal attacks (CWE-22 / CWE-23).
    - Explicitly raises FileNotFoundError with actionable paths if assets are absent.
    - Gracefully handles missing audio drivers or headless environments without crash.
    - Uses Flyweight caching to prevent disk I/O bottlenecks during active gameplay.
    """

    # Resolve base directory (handles PyInstaller frozen executables and dev interpreter)
    if getattr(sys, "frozen", False):
        BASE_DIR: str = os.path.dirname(sys.executable)
    else:
        BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    ASSETS_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "assets"))

    # Flyweight memory caches
    _image_cache: Dict[str, pygame.Surface] = {}
    _sound_cache: Dict[str, pygame.mixer.Sound | DummySound] = {}
    _spritesheet_cache: Dict[Tuple[str, int, int], List[pygame.Surface]] = {}

    @classmethod
    def _resolve_safe_path(cls, relative_path: str) -> str:
        """Validates and resolves an asset path, preventing path traversal outside ASSETS_DIR.

        Args:
            relative_path: Relative path within the assets directory.

        Returns:
            The normalized absolute filesystem path.

        Raises:
            ValueError: If path traversal or illegal relative escapes are detected.
            FileNotFoundError: If the asset file does not exist on disk.
        """
        # Normalize and remove any leading slashes/backslashes
        clean_rel = os.path.normpath(relative_path).lstrip(os.path.sep + (os.path.altsep or ""))
        full_path = os.path.abspath(os.path.join(cls.ASSETS_DIR, clean_rel))

        # Zero-Trust Path Traversal Guard (must reside strictly within ASSETS_DIR)
        assets_dir = os.path.abspath(cls.ASSETS_DIR)
        if not (full_path == assets_dir or full_path.startswith(assets_dir + os.path.sep)):
            raise ValueError(f"Security error: Path traversal detected for path '{relative_path}'")

        if not os.path.exists(full_path):
            raise FileNotFoundError(
                f"Asset file not found at '{full_path}' (requested relative path: '{relative_path}')"
            )

        return full_path

    @classmethod
    def _get_path(cls, relative_path: str) -> str:
        """Helper returning safe validated absolute path within assets directory."""
        return cls._resolve_safe_path(relative_path)

    @classmethod
    def load_image(cls, path: str) -> pygame.Surface:
        """Loads an image with convert_alpha() and caches it in memory.

        Args:
            path: Relative path to image within assets directory.

        Returns:
            Loaded pygame.Surface with alpha channel.

        Raises:
            FileNotFoundError: If image does not exist.
            ValueError: If path traversal is attempted.
        """
        if path in cls._image_cache:
            return cls._image_cache[path]

        full_path = cls._resolve_safe_path(path)
        img = pygame.image.load(full_path).convert_alpha()
        cls._image_cache[path] = img
        return img

    @classmethod
    def load_sound(cls, path: str) -> pygame.mixer.Sound | DummySound:
        """Loads a sound effect, with graceful fallback if audio mixer is unavailable.

        Args:
            path: Relative path to audio file within assets directory.

        Returns:
            Loaded pygame.mixer.Sound or DummySound fallback.

        Raises:
            FileNotFoundError: If audio file does not exist.
            ValueError: If path traversal is attempted.
        """
        if path in cls._sound_cache:
            return cls._sound_cache[path]

        full_path = cls._resolve_safe_path(path)

        # Attempt mixer initialization if not ready
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass

        if pygame.mixer.get_init():
            try:
                snd: pygame.mixer.Sound | DummySound = pygame.mixer.Sound(full_path)
            except Exception:
                snd = DummySound()
        else:
            snd = DummySound()

        cls._sound_cache[path] = snd
        return snd

    @classmethod
    def load_spritesheet(
        cls, path: str, frame_width: int, frame_height: int
    ) -> List[pygame.Surface]:
        """Slices a spritesheet using subsurfaces to minimize memory overhead.

        Args:
            path: Relative path to spritesheet within assets directory.
            frame_width: Width of each individual frame (> 0).
            frame_height: Height of each individual frame (> 0).

        Returns:
            List of sliced pygame.Surface frame instances.

        Raises:
            ValueError: If frame_width or frame_height is <= 0.
            FileNotFoundError: If spritesheet file does not exist.
        """
        if frame_width <= 0 or frame_height <= 0:
            raise ValueError(
                f"Invalid frame dimensions: width={frame_width}, height={frame_height} (must be > 0)"
            )

        cache_key = (path, frame_width, frame_height)
        if cache_key in cls._spritesheet_cache:
            return cls._spritesheet_cache[cache_key]

        sheet = cls.load_image(path)
        sheet_width, sheet_height = sheet.get_size()
        frames: List[pygame.Surface] = []

        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                rect = pygame.Rect(x, y, frame_width, frame_height)
                frames.append(sheet.subsurface(rect))

        cls._spritesheet_cache[cache_key] = frames
        return frames

    @classmethod
    def play_music(cls, path: str, loops: int = -1) -> None:
        """Safely load and play background music stream without crashing if audio fails.

        Args:
            path: Relative path to audio file within assets directory.
            loops: Number of loop repetitions (-1 for indefinite looping).
        """
        full_path = cls._resolve_safe_path(path)
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                return

        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.play(loops)
            except Exception:
                pass

    @classmethod
    def stop_music(cls) -> None:
        """Safely stop background music streaming."""
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    @classmethod
    def pause_music(cls) -> None:
        """Safely pause background music streaming."""
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.pause()
            except Exception:
                pass

    @classmethod
    def unpause_music(cls) -> None:
        """Safely unpause background music streaming."""
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.unpause()
            except Exception:
                pass

    @classmethod
    def stop_all_sounds(cls) -> None:
        """Safely stop all active sound mixer playback channels."""
        if pygame.mixer.get_init():
            try:
                pygame.mixer.stop()
            except Exception:
                pass

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all in-memory cached images, sound objects, and sliced spritesheets."""
        cls._image_cache.clear()
        cls._sound_cache.clear()
        cls._spritesheet_cache.clear()
