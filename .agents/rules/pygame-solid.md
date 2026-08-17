# Rules: Pygame & SOLID Architecture (pygame-solid.md)

## 1. Escopo de Regras
Este documento define as diretrizes estritas de codificação, arquitetura e formatação para o desenvolvimento do jogo 2D. O descumprimento destas regras resultará em falhas de arquitetura, acoplamento indevido ou rejeição na avaliação da banca acadêmica.

## 2. Princípios SOLID Aplicados (Python/Pygame)
A arquitetura do jogo baseia-se na implementação rigorosa dos princípios SOLID. O código Python deve refletir essas restrições através do módulo `abc` (Abstract Base Classes) e injeção de dependências.

| Princípio | Aplicação Prática no Projeto | Restrição Técnica |
| :--- | :--- | :--- |
| **S**ingle Responsibility | Cada classe tem uma única razão para mudar. O Pygame mistura renderização e lógica de tela; nossa arquitetura **separa** isso. | `LevelState` não calcula dano. Dano é responsabilidade do `CombatMediator`. `LevelState` não instancia *sprites*; isso é feito pela `EntityFactory`. |
| **O**pen/Closed | O loop principal (`Game`) deve estar fechado para modificação, mas aberto para extensão de novas telas. | Novos estados devem implementar a interface abstrata `IState`. O método `change_state()` deve aceitar apenas objetos que cumpram esse contrato genérico. |
| **L**iskov Substitution | O `LevelState` deve poder iterar sobre uma lista do tipo `List[Entity]` e invocar `update()` e `draw()` sem saber se é o `Hero`, um `BasicEnemy` ou o `DragonBoss`. | Subclasses não podem alterar a assinatura dos métodos da classe mãe (`Entity` e `Enemy`). |
| **I**nterface Segregation | Mantenha contratos enxutos. | Em Python, garanta que interfaces como `IState` possuam apenas os métodos estritamente necessários (ex: `run()`). |
| **D**ependency Inversion | Dependa de abstrações, não de implementações concretas. | O `LevelProgressProxy` interage com a abstração da `EntityFactory`, e o `Game` interage com `IState`. |

## 3. Encapsulamento e Tradução UML para Python
A linguagem Python não possui modificadores de acesso nativos como Java ou C#. A tradução dos símbolos do diagrama UML deve seguir a convenção PEP 8 estritamente para simular visibilidade.

* **Público (`+`)**: Métodos e atributos sem *underscore*. Podem ser acessados por qualquer classe (ex: `move()`, `attack()`).
* **Protegido (`#`)**: Variáveis de instância precedidas por um *underscore* simples (ex: `self._hp`, `self._speed`). Indica que o atributo deve ser manipulado apenas pela própria classe ou por suas subclasses diretas (como `DragonBoss` acessando `#hp` herdado de `Enemy`).
* **Privado (`-`)**: Variáveis de instância precedidas por duplo *underscore* (ex: `self.__enemies_killed`). O Python aplica *Name Mangling*, impedindo acesso externo. Use para estado interno estrito (como no `LevelProgressProxy`).
* **Acesso Controlado**: Se o `CombatMediator` precisar ler o `_hp` ou o `rect` de uma Entidade para calcular o combate, utilize o decorador `@property` (Getters legíveis e limpos). Nunca exponha os atributos diretamente para escrita.

## 4. Tipagem Estrita e Assinaturas (Type Hinting)
A base de código deve ser estaticamente analisável. Utilize a biblioteca nativa `typing`.

* **Exigência:** Toda função, método e atributo de classe deve ter *Type Hint*.
* **Retornos Vazios:** Métodos que não retornam dados devem ser explicitamente marcados com `-> None`.
* **Tipos do Pygame:** Utilize as classes nativas para tipagem (ex: `window: pygame.Surface`, `rect: pygame.Rect`).

```python
# Exemplo de tipagem e encapsulamento em conformidade com as regras
from abc import ABC, abstractmethod
import pygame
from typing import List

class Entity(ABC):
    def __init__(self, name: str, surf: pygame.Surface, x: int, y: int) -> None:
        self._name: str = name
        self._surf: pygame.Surface = surf
        self._rect: pygame.Rect = surf.get_rect(topleft=(x, y))
        self._hp: int = 100

    @property
    def rect(self) -> pygame.Rect:
        """Acesso somente leitura para o CombatMediator."""
        return self._rect

    @abstractmethod
    def update(self) -> None:
        pass
```
## 5. Clean Code e Documentação Defensiva
Como o projeto será avaliado por uma banca acadêmica, a legibilidade do código atua como justificativa em tempo de leitura. A banca precisa de uma interpretação fluida.

* **Sem "Magic Numbers":** Limites de tela, quantidade máxima de inimigos (40) e configurações de *cooldown* não devem ser *hardcoded* no meio do código. Extraia-os para constantes no topo do arquivo ou em um arquivo separado (ex: `src/utils/settings.py`).
* **Nomenclatura Descritiva:** Nomes de variáveis devem representar seu estado exato (`is_defending` no lugar de `def`, `check_win_condition` no lugar de `check`).
* **Comentários Táticos:** Comente **exclusivamente** o "porquê" de lógicas não evidentes. Se a matemática de colisão no `CombatMediator` utilizar detecção de intersecção complexa ou se houver uma rotina de deleção de memória no *Proxy*, adicione um bloco de comentário conciso. O "o que" o código faz deve ser autoexplicativo pela sua nomenclatura.
