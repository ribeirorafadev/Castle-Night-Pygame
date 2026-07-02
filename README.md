<div align="center">

# 🏰 Castle Night - Demo

**Technologies and principles used in the project.**

![Python Badge](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame Badge](https://img.shields.io/badge/Pygame-D22128?style=for-the-badge&logo=pygame&logoColor=white)
![SOLID Architecture](https://img.shields.io/badge/Architecture-SOLID-brightgreen?style=for-the-badge)

</div>

<br/>

**Castle Night** It is an academic challenge aimed at creating a 2D game in Python for the Applied Programming Language course within the Software Engineering program (Uninter).

**Design Patterns used in the project:**
* **State Pattern:** Orchestration of screen transitions (Menu vs. Level), ensuring context isolation and facilitating entity garbage collection.
* **Mediator Pattern:** Centralization of the combat system (`CombatMediator`). The `Hero` and `Enemy` entities are completely decoupled, unaware of each other's existence. The Mediator evaluates hitbox collisions using AABB (*Axis-Aligned Bounding Box*) mathematics and reverse sweeping.
* **Factory Method:** The `EntityFactory` abstracts the entire complexity of enemy instantiation by injecting dynamic sprite catalogs (Dependency Injection) and attributes based on the requested type.
* **Finite State Machine (FSM):** AI and animations controlled by rigorous Finite State Machines, preventing *Animation Locks*, *Memory Leaks* in corpses, and pathfinding *Z-Fighting*.
* **Flyweight / Singleton:** In-memory cache (`AssetLoader`) to mitigate disk I/O bottlenecks during procedural *spawns*.

---

**To compile the project ⬇️**

📘 **[Read the Definitive Compilation Guide Here](./docs/guide-compilation.txt)**
