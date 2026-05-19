    import pygame
import math
from abc import ABC, abstractmethod


# ── Enemy ABC ────────────────────────────────────────────────────────────────

class Enemy(ABC):
    """Abstract base class untuk semua enemy."""

    hp: int = 100
    max_hp: int = 100
    speed: float = 1.5          # pixel per frame (dikalikan dt*60)
    reward: int = 10            # gold yang didapat saat enemy mati
    damage_to_base: int = 1     # nyawa yang dikurangi saat mencapai base

    def __init__(self, world_path: list[tuple[float, float]]):
        self.x, self.y = world_path[0]
        self.path_index: int = 0   # sesuai notes; index 0 = waypoint pertama
        self.alive: bool = True
        self.reached_base: bool = False
        self.rect: pygame.Rect = pygame.Rect(int(self.x) - 8, int(self.y) - 8, 16, 16)
        self.target_index: int = 0   # alias path_index (sesuai class diagram)

    # ── damage & state ────────────────────────────────────────────────────────

    def take_damage(self, amount: float):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def is_dead(self) -> bool:
        return not self.alive

    # ── movement ──────────────────────────────────────────────────────────────

    def update(self, dt: float, world_path: list[tuple[float, float]]):
        if not self.alive:
            return

        if self.path_index >= len(world_path):
            self.reached_base = True
            self.alive = False
            return

        tx, ty = world_path[self.path_index]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)

        if dist < 2:
            self.path_index += 1
            self.target_index = self.path_index
        else:
            move = self.speed * dt * 60   # ×60 agar terasa wajar di 60 FPS
            self.x += (dx / dist) * move
            self.y += (dy / dist) * move

        # update rect untuk collision / klik
        self.rect.center = (int(self.x), int(self.y))

    # ── health bar ────────────────────────────────────────────────────────────

    def _draw_health_bar(self, surface: pygame.Surface,
                        width: int, height: int):
        ratio = max(0.0, self.hp / self.max_hp)
        bar_x = int(self.x - width // 2)
        bar_y = int(self.y - height // 2 - 10)
        pygame.draw.rect(surface, (180, 0, 0),   (bar_x, bar_y, width, 5))
        pygame.draw.rect(surface, (0, 220, 0),   (bar_x, bar_y, int(width * ratio), 5))
        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, width, 5), 1)

    # ── abstract ──────────────────────────────────────────────────────────────

    @abstractmethod
    def draw(self, surface: pygame.Surface): ...


# ── NormalEnemy ───────────────────────────────────────────────────────────────

class NormalEnemy(Enemy):
    """Balanced stats"""

    def __init__(self, world_path: list[tuple[float, float]]):
        super().__init__(world_path)
        self.hp = 100
        self.max_hp = 100
        self.speed = 1
        self.reward = 10
        self.damage_to_base = 5
        self.color = (60, 200, 60)
        self.size = 14

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        # badan
        pygame.draw.rect(surface, self.color,
                         (int(self.x) - self.size // 2,
                          int(self.y) - self.size // 2,
                          self.size, self.size))
        pygame.draw.rect(surface, (0, 140, 0),
                         (int(self.x) - self.size // 2,
                          int(self.y) - self.size // 2,
                          self.size, self.size), 2)
        self._draw_health_bar(surface, self.size + 6, self.size)


# ── FastEnemy ─────────────────────────────────────────────────────────────────

class FastEnemy(Enemy):
    """High speed, low health"""

    def __init__(self, world_path: list[tuple[float, float]]):
        super().__init__(world_path)
        self.hp = 40
        self.max_hp = 40
        self.speed = 2
        self.reward = 15
        self.damage_to_base = 5
        self.color = (80, 160, 255)
        self.size = 10

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        # lingkaran kecil biru
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), self.size // 2 + 2)
        pygame.draw.circle(surface, (30, 80, 200),
                           (int(self.x), int(self.y)), self.size // 2 + 2, 2)
        self._draw_health_bar(surface, self.size + 6, self.size)


# ── TankEnemy ─────────────────────────────────────────────────────────────────

class TankEnemy(Enemy):
    """High health, slow, heavy damage to base."""

    def __init__(self, world_path: list[tuple[float, float]]):
        super().__init__(world_path)
        self.hp = 400
        self.max_hp = 400
        self.speed = 0.5
        self.reward = 30
        self.damage_to_base = 20
        self.color = (200, 60, 60)
        self.size = 22

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        # kotak besar merah
        pygame.draw.rect(surface, self.color,
                         (int(self.x) - self.size // 2,
                          int(self.y) - self.size // 2,
                          self.size, self.size),
                         border_radius=3)
        pygame.draw.rect(surface, (130, 20, 20),
                         (int(self.x) - self.size // 2,
                          int(self.y) - self.size // 2,
                          self.size, self.size), 3, border_radius=3)
        self._draw_health_bar(surface, self.size + 8, self.size)
