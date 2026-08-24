"""Factory module implementing Factory Method for entity instantiation."""

from typing import Dict, Any
from src.entities.hero import Hero
from src.entities.entity import Entity
from src.entities.enemy import BasicEnemy, DragonBoss
from src.utils import settings


class EntityFactory:
    """Factory Method implementation centralizing entity instantiation and configuration."""

    @staticmethod
    def create_hero(x: float, y: float) -> Hero:
        """Instantiates and returns the player-controlled Hero entity."""
        return Hero(name="Player", x=x, y=y, speed=settings.HERO_SPEED)

    @staticmethod
    def create_enemy(enemy_type: str, x: float, y: float) -> Entity:
        """Instantiates and returns an enemy entity by type (DragonBoss or BasicEnemy variant)."""
        if enemy_type == 'boss-dragon':
            return DragonBoss(x=x, y=y, speed=settings.BOSS_SPEED)

        configs: Dict[str, Dict[str, Any]] = {
            'minotaur': {
                'attacks': ['Attack.png'],
                'attack_sounds': ['audio/Attack-Sword-Enemy.mp3'],
            },
            'wizard': {
                'run': 'Run.png',
                'jump': 'Jump.png',
                'attacks': ['Attack_1.png', 'Attack_2.png', 'Flame_jet.png'],
                'attack_sounds': [
                    'audio/Attack-Sword-Enemy.mp3',
                    'audio/Attack-Sword-Enemy.mp3',
                    'audio/Attack-FireBall.mp3',
                ],
            },
            'skeleton': {
                'run': 'Run.png',
                'run_attack': 'Run+attack.png',
                'attacks': ['Attack_1.png', 'Attack_2.png', 'Attack_3.png'],
                'attack_sounds': ['audio/Attack-Sword-Enemy.mp3'] * 3,
                'run_attack_sound': 'audio/Attack-Sword-Enemy.mp3',
            },
            'werewolf': {
                'run': 'Run.png',
                'jump': 'Jump.png',
                'run_attack': 'Run+Attack.png',
                'attacks': ['Attack_1.png', 'Attack_2.png', 'Attack_3.png'],
                'attack_sounds': ['audio/Attack-Werewolf.mp3'] * 3,
                'run_attack_sound': 'audio/Attack-Werewolf.mp3',
            },
            'yokai': {
                'run': 'Run.png',
                'jump': 'Jump.png',
                'attacks': ['Attack_1.png', 'Attack_2.png', 'Attack_3.png'],
                'attack_sounds': ['audio/Attack-Sword-Enemy.mp3'] * 3,
            },
        }

        return BasicEnemy(
            name=enemy_type,
            x=x,
            y=y,
            speed=settings.ENEMY_SPEED,
            config=configs.get(enemy_type, {}),
        )
