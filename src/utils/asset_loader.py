import os
import sys
import pygame
from typing import List

class AssetLoader:
    """
    Gerenciador estático de caminhos e carregamento de mídias.
    Garante resiliência a falhas de rota após compilação pelo PyInstaller (--onefile).
    """

    # Tratamento de rotas estritas para o compilador PyInstaller (Requisito Acadêmico)
    if getattr(sys, 'frozen', False):
        # Se estiver rodando como executável, a base é a pasta do .exe
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # Se estiver rodando no interpretador, a base é a raiz do projeto (dois níveis acima)
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    
    # Padrão Estrutural 'Flyweight': Cache em memória para evitar gargalos de I/O de disco e manter FPS estável durante Spawns de entidades.
    _image_cache = {}
    _sound_cache = {}
    _spritesheet_cache = {}

    @staticmethod
    def _get_path(relative_path: str) -> str:
        """Resolve o caminho absoluto mesclando a pasta assets com a rota interna requerida."""
        return os.path.join(AssetLoader.ASSETS_DIR, os.path.normpath(relative_path))

    @staticmethod
    def load_image(path: str) -> pygame.Surface:
        """
        Carrega imagem de forma segura e converte para alpha otimizado, 
        evitando gargalos de renderização na CPU.
        """
        if path in AssetLoader._image_cache:
            return AssetLoader._image_cache[path]
            
        full_path = AssetLoader._get_path(path)
        img = pygame.image.load(full_path).convert_alpha()
        AssetLoader._image_cache[path] = img
        return img

    @staticmethod
    def load_sound(path: str) -> pygame.mixer.Sound:
        """Carrega efeito sonoro na memória."""
        if path in AssetLoader._sound_cache:
            return AssetLoader._sound_cache[path]
            
        full_path = AssetLoader._get_path(path)
        snd = pygame.mixer.Sound(full_path)
        AssetLoader._sound_cache[path] = snd
        return snd

    @staticmethod
    def load_spritesheet(path: str, frame_width: int, frame_height: int) -> List[pygame.Surface]:
        """
        Fatia uma spritesheet usando subsurfaces para poupar memória RAM (compartilhamento de textura base).
        """
        cache_key = (path, frame_width, frame_height)
        if cache_key in AssetLoader._spritesheet_cache:
            return AssetLoader._spritesheet_cache[cache_key]
            
        sheet = AssetLoader.load_image(path)
        sheet_width, sheet_height = sheet.get_size()
        frames: List[pygame.Surface] = []

        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                rect = pygame.Rect(x, y, frame_width, frame_height)
                # subsurface é O(1) e não aloca nova memória de imagem, apontando para o original
                frames.append(sheet.subsurface(rect))

        AssetLoader._spritesheet_cache[cache_key] = frames
        return frames
