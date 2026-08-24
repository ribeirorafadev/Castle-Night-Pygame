"""Centralized game settings and configuration constants for Castle Night."""

# Screen and Display Settings
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FLOOR_HEIGHT: int = 450
FPS: int = 60
TITLE: str = "Castle Night - Demo"

# Physics Settings
GRAVITY: float = 800.0
HERO_SPEED: float = 200.0
HERO_JUMP_FORCE: float = -400.0
ENEMY_SPEED: float = 150.0
BOSS_SPEED: float = 100.0
ENEMY_JUMP_FORCE: float = -400.0
KNOCKBACK_FORCE: float = 20.0

# Combat Settings
HERO_MAX_HP: int = 100
HERO_ATTACK_DAMAGE: int = 25
ENEMY_MAX_HP: int = 100
ENEMY_ATTACK_DAMAGE: int = 5
BOSS_MAX_HP: int = 500
BOSS_ATTACK_DAMAGE: int = 25

# AI and Ranges
ENEMY_VISION_RANGE: float = 300.0
ENEMY_ATTACK_RANGE: float = 60.0
ENEMY_ATTACK_COOLDOWN: float = 1.5
BOSS_VISION_RANGE: float = 600.0
BOSS_ATTACK_RANGE: float = 120.0
BOSS_ATTACK_COOLDOWN: float = 2.0

# Progression and Timers
MAX_REGULAR_ENEMIES: int = 20
ENEMY_DEATH_DELAY: float = 2.0
BOSS_DEATH_DELAY: float = 2.0
SCREEN_SHAKE_DURATION: float = 2.0
SCREEN_SHAKE_INTENSITY: int = 8

# Animation Speeds
HERO_ANIMATION_SPEED: float = 10.0
ENEMY_ANIMATION_SPEED: float = 8.0
BOSS_ANIMATION_SPEED: float = 8.0

# UI and HUD Settings (Medieval 8-bit aesthetic)
HUD_HP_BAR_WIDTH: int = 240
HUD_HP_BAR_HEIGHT: int = 22
HUD_BOSS_BAR_WIDTH: int = 600
HUD_BOSS_BAR_HEIGHT: int = 24
ENEMY_HP_BAR_WIDTH: int = 40
ENEMY_HP_BAR_HEIGHT: int = 5
ENEMY_HP_BAR_OFFSET_Y: int = 10
PAUSE_MENU_WIDTH: int = 380
PAUSE_MENU_HEIGHT: int = 240

