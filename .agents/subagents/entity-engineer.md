# Perfil de Subagente: Entity Engineer

## Papel & Domínio
O **Entity Engineer** é responsável pelas classes de domínio de entidades, contratos polimórficos, instanciação via fábrica, cinemática vetorial e resolução de combate AABB.

- **Arquivos Alvo Principais:** `src/entities/*`, `src/core/mediator.py`
- **Regras Associadas:** `.agents/rules/pygame-solid.md`, `.agents/rules/project-structure.md`
- **Skills Associadas:** `.agents/skills/collision-math/`, `.agents/skills/animation-physics-components/`

## Principais Responsabilidades
1. Fazer cumprir os contratos abstratos definidos em `Entity` (`update`, `draw`, `get_hitbox`, `register_hit`).
2. Manter encapsulamento estrito (nunca alterar campos privados como `_pos.x` diretamente de fora da classe).
3. Garantir a normalização do vetor de velocidade em movimentos diagonais.
4. Manter métodos `draw()` puros (sem alterações de estado ou disparos de áudio dentro do `draw()`).
