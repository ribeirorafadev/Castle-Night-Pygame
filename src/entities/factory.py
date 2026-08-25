"""Factory module implementing Factory Method for entity instantiation."""

from __future__ import annotations

from typing import Dict, Any
from src.entities.hero import Hero
from src.entities.entity import Entity
from src.entities.enemy import BasicEnemy, DragonBoss
from src.utils import settings


class EntityFactory:
    """Factory Method implementation centralizing character instantiation and archetype configuration."""

    @staticmethod
    def create_hero(x: float, y: float) -> Hero:
        """Instantiate and return the player-controlled Hero character.

        Args:
            x: Initial horizontal world coordinate in pixels.
            y: Initial vertical world coordinate in pixels.

        Returns:
            Hero: Configured player entity.
        """
        return Hero(name="Player", x=x, y=y, speed=settings.HERO_SPEED)

    @staticmethod
    def create_enemy(enemy_type: str, x: float, y: float) -> Entity:
        """Instantiate and return an enemy entity by archetype (DragonBoss or BasicEnemy variant).

        Args:
            enemy_type: Identifier string for the enemy archetype ('boss-dragon', 'minotaur',
                'wizard', 'skeleton', 'werewolf', 'yokai').
            x: Initial horizontal world coordinate in pixels.
            y: Initial vertical world coordinate in pixels.

        Returns:
            Entity: Instantiated and configured enemy instance.
        """
        if enemy_type == "boss-dragon":
            return DragonBoss(x=x, y=y, speed=settings.BOSS_SPEED)

        # Archetype asset and attack configurations for basic enemies
        configs: Dict[str, Dict[str, Any]] = {
            "minotaur": {
                "attacks": ["Attack.png"],
                "attack_sounds": ["audio/Attack-Sword-Enemy.mp3"],
            },
            "wizard": {
                "run": "Run.png",
                "jump": "Jump.png",
                "attacks": ["Attack_1.png", "Attack_2.png", "Flame_jet.png"],
                "attack_sounds": [
                    "audio/Attack-Sword-Enemy.mp3",
                    "audio/Attack-Sword-Enemy.mp3",
                    "audio/Attack-FireBall.mp3",
                ],
            },
            "skeleton": {
                "run": "Run.png",
                "run_attack": "Run+attack.png",
                "attacks": ["Attack_1.png", "Attack_2.png", "Attack_3.png"],
                "attack_sounds": ["audio/Attack-Sword-Enemy.mp3"] * 3,
                "run_attack_sound": "audio/Attack-Sword-Enemy.mp3",
            },
            "werewolf": {
                "run": "Run.png",
                "jump": "Jump.png",
                "run_attack": "Run+Attack.png",
                "attacks": ["Attack_1.png", "Attack_2.png", "Attack_3.png"],
                "attack_sounds": ["audio/Attack-Werewolf.mp3"] * 3,
                "run_attack_sound": "audio/Attack-Werewolf.mp3",
            },
            "yokai": {
                "run": "Run.png",
                "jump": "Jump.png",
                "attacks": ["Attack_1.png", "Attack_2.png", "Attack_3.png"],
                "attack_sounds": ["audio/Attack-Sword-Enemy.mp3"] * 3,
            },
        }

        return BasicEnemy(
            name=enemy_type,
            x=x,
            y=y,
            speed=settings.ENEMY_SPEED,
            config=configs.get(enemy_type, {}),
        )

