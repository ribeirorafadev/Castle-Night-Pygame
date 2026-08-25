# 🏛️ Castle Night - Diagrama de Classes UML (Arquitetura SOLID / GoF)

Este documento contém o diagrama de classes UML oficial do projeto **Castle Night**, refletindo com precisão todos os módulos, entidades, padrões de projeto e contratos de interface implementados no código-fonte.

---

```mermaid
classDiagram
    class Game {
        -window: pygame.Surface
        -_current_state: IState
        -_clock: pygame.time.Clock
        -_running: bool
        +fps: float
        +change_state(new_state: IState): void
        +run(): void
        +quit(): void
    }

    class IState {
        <<interface>>
        +run(dt: float): void*
    }

    class MenuState {
        -_game: Game
        -_selected_index: int
        -_show_controls_modal: bool
        -_menu_options: list[str]
        +selected_index: int
        +run(dt: float): void
        +draw_controls(): void
        -_activate_option(index: int): void
    }

    class LevelState {
        -_game: Game
        +hero: Hero
        +enemies: List[Entity]
        +mediator: CombatMediator
        -_proxy: LevelProgressProxy
        -_hud: HUDManager
        -_is_paused: bool
        -_pause_selected_index: int
        +is_paused: bool
        +pause_selected_index: int
        +boss_spawned: bool
        +boss_defeated: bool
        +enemies_to_boss: int
        +run(dt: float): void
        -_spawn_wave(): void
        -_return_to_menu(): void
        -_render_hud(): void
    }

    class HUDManager {
        -_font_small: pygame.font.Font
        -_font_main: pygame.font.Font
        -_font_large: pygame.font.Font
        -_font_title: pygame.font.Font
        -_surface_cache: dict
        -_fullscreen_overlay: pygame.Surface
        +draw_player_hp(surface, hp, max_hp): void
        +draw_enemy_health_bar(surface, enemy): void
        +draw_boss_hp(surface, hp, max_hp, boss_name): void
        +draw_wave_progress(surface, enemies_remaining, total_enemies, is_boss_active): void
        +draw_pause_menu(surface, selected_index): void
        +draw_fps(surface, fps): void
        +draw_game_over(surface, timer): void
        +draw_victory_screen(surface, timer, boss_name, horde_cleared, total_horde, hp_remaining): void
    }

    class LevelProgressProxy {
        -_factory: EntityFactory
        -_enemies_killed: int
        -_total_enemies: int = 20
        -_boss_spawned: bool
        -_boss_defeated: bool
        +total_enemies: int
        +enemies_remaining: int
        +defeated_count: int
        +boss_spawned: bool
        +boss_defeated: bool
        +should_spawn_boss: bool
        +is_victory: bool
        +register_kill(entity_or_name: Any): void
        +request_spawn(hero, active_enemies): List[Entity]
    }

    class CombatMediator {
        -_hero: Hero
        +update(enemies: List[Entity]): void
    }

    class EntityFactory {
        +create_hero(x: float, y: float): Hero$
        +create_enemy(enemy_type: str, x: float, y: float): Entity$
    }

    class AssetLoader {
        +BASE_DIR: str$
        +ASSETS_DIR: str$
        -_image_cache: dict$
        -_sound_cache: dict$
        -_spritesheet_cache: dict$
        +_resolve_safe_path(relative_path: str): str$
        +load_image(path: str): pygame.Surface$
        +load_sound(path: str): pygame.mixer.Sound$
        +load_spritesheet(path: str, frame_width: int, frame_height: int): List[pygame.Surface]$
        +play_music(path: str, loops: int): void$
        +stop_music(): void$
        +pause_music(): void$
        +unpause_music(): void$
        +stop_all_sounds(): void$
        +clear_cache(): void$
    }

    class Entity {
        <<abstract>>
        #_name: str
        #_pos: Vector2
        #_vel: Vector2
        #_hp: int
        +max_hp: int
        +attack_damage: int
        #_is_removable: bool
        +name: str
        +pos: Vector2
        +vel: Vector2
        +hp: int
        +is_boss: bool
        +is_removable: bool
        +rect: pygame.Rect
        +update(dt: float): void*
        +draw(window: pygame.Surface): void*
        +take_damage(amount: int): void
        +apply_knockback(direction, force): void
        +can_block(attacker_x: float): bool
        +set_target(target: Entity): void
        +get_hitbox(): Optional[pygame.Rect]*
        +register_hit(): void*
        +safe_normalize(vec: Vector2): Vector2$
    }

    class PhysicsComponent {
        +pos: Vector2
        +vel: Vector2
        +speed: float
        +gravity: float
        +floor_y: float
        +is_on_ground: bool
        +update(dt: float): void
        +jump(force: float): void
        +apply_knockback(direction, force): void
        +safe_normalize(vec: Vector2): Vector2$
        +get_direction_to(target_pos: Vector2): Vector2
    }

    class AnimationComponent {
        +animations: dict
        -_state: str
        -_current_frame: float
        +speed: float
        -_is_finished: bool
        +state: str
        +current_frame: float
        +is_finished: bool
        +set_state(state: str, force_reset: bool): void
        +update(dt: float, loop: bool): void
        +get_current_image(): pygame.Surface
    }

    class Hero {
        +max_hp: int = 100
        +attack_damage: int = 25
        +is_defending: bool
        +is_attacking: bool
        +is_running: bool
        +facing_right: bool
        +update(dt: float): void
        +draw(window: pygame.Surface): void
        +can_block(attacker_x: float): bool
        +block_hit(): void
        +take_damage(amount: int): void
        +get_hitbox(): Optional[pygame.Rect]
        +register_hit(): void
    }

    class Enemy {
        <<abstract>>
        +current_playing_sound: Optional[Sound]
        +take_damage(amount: int): void
        +is_boss: bool
    }

    class BasicEnemy {
        +vision_range: float
        +attack_range: float
        +facing_right: bool
        +update(dt: float): void
        +draw(window: pygame.Surface): void
        +get_hitbox(): Optional[pygame.Rect]
        +register_hit(): void
    }

    class DragonBoss {
        +max_hp: int = 500
        +attack_damage: int = 35
        +is_boss: bool = True
        -fire_frames: list
        +take_damage(amount: int): void
        +apply_knockback(direction, force): void
        +update(dt: float): void
        +draw(window: pygame.Surface): void
        +get_hitbox(): Optional[pygame.Rect]
        +register_hit(): void
    }

    Game --> IState : manages
    IState <|.. MenuState : implements
    IState <|.. LevelState : implements
    LevelState *-- HUDManager : composition
    LevelState *-- LevelProgressProxy : composition
    LevelState *-- CombatMediator : composition
    LevelState *-- Hero : composition
    LevelProgressProxy ..> EntityFactory : depends
    CombatMediator --> Hero : manages
    CombatMediator --> Enemy : manages
    Entity <|-- Hero : extends
    Entity <|-- Enemy : extends
    Enemy <|-- BasicEnemy : extends
    Enemy <|-- DragonBoss : extends
    EntityFactory ..> Hero : creates
    EntityFactory ..> BasicEnemy : creates
    EntityFactory ..> DragonBoss : creates
    MenuState ..> AssetLoader : uses
    LevelState ..> AssetLoader : uses
    Hero ..> AssetLoader : uses
    Enemy ..> AssetLoader : uses
```
