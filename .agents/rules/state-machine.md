# Rules: State Machine & Game Flow (state_machine.md)

## 1. Escopo Arquitetural
Este documento define as regras estritas para o controle do fluxo de execução do jogo através do padrão de projeto **State**. O motor do jogo não deve conter lógicas de espaguete (`if estado == "menu": faz_isso() else: faz_aquilo()`). O fluxo deve ser modularizado, garantindo que cada tela gerencie seu próprio ciclo de renderização e eventos, facilitando a defesa da arquitetura perante a banca avaliadora por ser um design limpo e de fácil leitura humana.

## 2. O Contrato `IState` (Polimorfismo)
Todas as telas do jogo (`MenuState`, `LevelState`, e potenciais telas de Vitória/Derrota) devem implementar rigorosamente a interface abstrata `IState`.

* **Regra de Implementação:** A interface deve conter um método público principal, geralmente nomeado como `run()`.
* **Isolamento:** Nenhum estado deve conhecer o comportamento interno de outro estado. O `MenuState` sabe que precisa desenhar os comandos ("Space - Saltar", "Mouse - Atacar") e capturar o input para iniciar o jogo, mas ignora completamente a existência de inimigos ou regras de combate.

## 3. O Gerenciador de Contexto (`Game`)
A classe `Game` é o núcleo (*Context*) da Máquina de Estados. Suas responsabilidades são restritas e absolutas:

1. **Inicialização do Pygame:** Configurar a janela (`pygame.display.set_mode`), relógio (`pygame.time.Clock`) e inicializar os módulos do Pygame.
2. **Manutenção do Estado Atual:** Manter uma referência privada ao estado em execução (`self._current_state: IState`).
3. **Loop Principal (*Game Loop*):** Conter o laço `while True` que simplesmente delega a execução para o estado atual (`self._current_state.run()`).
4. **Transição de Estados:** Prover um método público `change_state(new_state: IState) -> None`.

## 4. Gerenciamento de Memória nas Transições
O rigor no controle de memória (composição) é inegociável durante as transições de estado para evitar vazamentos de memória (*memory leaks*).

* **Morte do Herói (Derrota):** Se o HP do herói zerar, a instância atual de `LevelState` deve ser destruída. O estado deve ser substituído por uma **nova** instância de `LevelState` (ou recarregado via método `reset_level()`), acionando o *Garbage Collector* do Python para aniquilar as instâncias antigas do Herói, dos Inimigos e do Mediador.
* **Vitória (Derrota do Boss):** Após o `LevelProgressProxy` confirmar a morte do `DragonBoss`, o `LevelState` deve invocar a mudança para o estado inicial (`MenuState`) ou para uma tela de vitória, limpando a fase da memória RAM.

## 5. Higienização da Fila de Eventos (Event Queue)
No Pygame, eventos de teclado e mouse ficam armazenados na fila do sistema (`pygame.event.get()`).

* **Regra Crítica:** Ao transitar entre o `MenuState` e o `LevelState`, a fila de eventos **deve ser limpa**. Caso contrário, um clique de tecla usado para iniciar o jogo no Menu pode vazar para o Nível e fazer o Herói atacar ou pular acidentalmente no primeiro *frame*.
* **Legibilidade para a Banca:** Mantenha a leitura e processamento de eventos (`pygame.QUIT`, `pygame.KEYDOWN`) encapsulados dentro do método `run()` de cada estado específico. Isso demonstra coesão e facilita a interpretação humana do código por parte dos avaliadores.

```python
# Exemplo do contrato esperado para a injeção de dependência e transição
class Game:
    def __init__(self, window: pygame.Surface) -> None:
        self.window = window
        self._current_state: IState = MenuState(self) # Injeta a si mesmo para permitir troca de estado

    def change_state(self, new_state: IState) -> None:
        """Substitui o estado atual, liberando o antigo para o Garbage Collector."""
        self._current_state = new_state

    def run(self) -> None:
        while True:
            # A execução é delegada inteiramente ao estado atual
            self._current_state.run()
            pygame.display.update()
