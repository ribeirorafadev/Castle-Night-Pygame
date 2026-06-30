from src.entities.hero import Hero
from src.entities.entity import Entity
from src.entities.enemy import BasicEnemy, DragonBoss
from src.utils.asset_loader import AssetLoader

class EntityFactory:
    """Implementação do Padrão de Projeto Criacional 'Factory Method'. Centraliza a complexidade de instanciação, injeção de dependências e configuração de catálogos de animação."""
    @staticmethod
    def create_hero(x: float, y: float) -> Hero:
        return Hero(name="Player", x=x, y=y, speed=200.0)

    @staticmethod
    def create_enemy(enemy_type: str, x: float, y: float) -> Entity:
        if enemy_type == 'boss-dragon':
            return DragonBoss(x, y, 100.0)
        else:
            configs = {
                'minotaur': {
                    'attacks': ['Attack.png'], 
                    'attack_sounds': ['audio/Attack-Sword-Enemy.mp3']
                },
                'wizard': {
                    'run': 'Run.png', 'jump': 'Jump.png', 
                    'attacks': ['Attack_1.png', 'Attack_2.png', 'Flame_jet.png'],
                    'attack_sounds': ['audio/Attack-Sword-Enemy.mp3', 'audio/Attack-Sword-Enemy.mp3', 'audio/Attack-FireBall.mp3']
                },
                'skeleton': {
                    'run': 'Run.png', 'run_attack': 'Run+attack.png', 
                    'attacks': ['Attack_1.png', 'Attack_2.png', 'Attack_3.png'],
                    'attack_sounds': ['audio/Attack-Sword-Enemy.mp3', 'audio/Attack-Sword-Enemy.mp3', 'audio/Attack-Sword-Enemy.mp3'],
                    'run_attack_sound': 'audio/Attack-Sword-Enemy.mp3'
                },
                'werewolf': {
                    'run': 'Run.png', 'jump': 'Jump.png', 'run_attack': 'Run+Attack.png', 
                    'attacks': ['Attack_1.png', 'Attack_2.png', 'Attack_3.png'],
                    'attack_sounds': ['audio/Attack-Werewolf.mp3', 'audio/Attack-Werewolf.mp3', 'audio/Attack-Werewolf.mp3'],
                    'run_attack_sound': 'audio/Attack-Werewolf.mp3'
                },
                'yokai': {
                    'run': 'Run.png', 'jump': 'Jump.png', 
                    'attacks': ['Attack_1.png', 'Attack_2.png', 'Attack_3.png'],
                    'attack_sounds': ['audio/Attack-Sword-Enemy.mp3', 'audio/Attack-Sword-Enemy.mp3', 'audio/Attack-Sword-Enemy.mp3']
                }
            }
            enemy = BasicEnemy(name=enemy_type, x=x, y=y, speed=150.0, config=configs.get(enemy_type, {}))
            
            return enemy
