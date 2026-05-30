import pygame
import math
from abc import ABC, abstractmethod
from map import Cell


# ══════════════════════════════════════════════════════════════════════════════
#  PROJECTILE
# ══════════════════════════════════════════════════════════════════════════════

class Projectile(ABC):
    """Abstract base class untuk semua proyektil."""

    def __init__(self, x: float, y: float, target, damage: int, speed: float):
        self.x: float = x
        self.y: float = y
        self.target = target      # Enemy yang dituju
        self.damage: int = damage
        self.speed: float = speed
        self.active: bool = True

    def update(self, dt: float, enemies: list):
        """Gerak menuju target. Jika sudah sampai (atau target mati), panggil on_hit."""
        if not self.active:
            return

        # Target sudah mati sebelum peluru sampai → nonaktifkan peluru
        if not self.target.alive:
            self.active = False
            return

        tx, ty = self.target.x, self.target.y
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)

        move = self.speed * dt
        if dist <= move:
            # Sampai ke target
            self.x, self.y = tx, ty
            self.on_hit(self.target, enemies)
            self.active = False
        else:
            self.x += (dx / dist) * move
            self.y += (dy / dist) * move

    @abstractmethod
    def on_hit(self, enemy, enemies: list): ...

    @abstractmethod
    def draw(self, surface: pygame.Surface): ...


# ── Arrow ─────────────────────────────────────────────────────────────────────

class Arrow(Projectile):
    """Proyektil single-target. Digambar sebagai garis kecil / segitiga."""

    speed_default: float = 300.0   # pixel / detik

    def __init__(self, x: float, y: float, target, damage: int):
        super().__init__(x, y, target, damage, speed=self.speed_default)
        self.prev_x: float = x
        self.prev_y: float = y

    def update(self, dt: float, enemies: list):
        self.prev_x, self.prev_y = self.x, self.y
        super().update(dt, enemies)

    def on_hit(self, enemy, enemies: list):
        """Damage hanya ke satu target."""
        enemy.take_damage(self.damage)

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return
        # Garis kuning tipis dari posisi sebelumnya ke posisi sekarang
        pygame.draw.line(
            surface,
            (255, 220, 50),
            (int(self.prev_x), int(self.prev_y)),
            (int(self.x),      int(self.y)),
            2,
        )
        # Kepala panah (titik kecil)
        pygame.draw.circle(surface, (200, 160, 20), (int(self.x), int(self.y)), 3)


# ── Cannonball ────────────────────────────────────────────────────────────────

class Cannonball(Projectile):
    """Proyektil area-damage (splash). Digambar sebagai lingkaran gelap."""

    speed_default: float = 150.0   # pixel / detik

    def __init__(self, x: float, y: float, target, damage: int,
                 splash_radius: float = 60.0):
        super().__init__(x, y, target, damage, speed=self.speed_default)
        self.splash_radius: float = splash_radius

    def on_hit(self, enemy, enemies: list):
        """Damage ke semua enemy dalam splash_radius dari titik impact."""
        impact_x, impact_y = self.target.x, self.target.y
        for e in enemies:
            if e.alive:
                dist = math.hypot(e.x - impact_x, e.y - impact_y)
                if dist <= self.splash_radius:
                    e.take_damage(self.damage)

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return
        # Lingkaran gelap berukuran sedang
        pygame.draw.circle(surface, (50, 30, 10),  (int(self.x), int(self.y)), 7)
        pygame.draw.circle(surface, (120, 80, 30), (int(self.x), int(self.y)), 7, 2)


# ══════════════════════════════════════════════════════════════════════════════
#  TURRET
# ══════════════════════════════════════════════════════════════════════════════

class Turret(ABC):
    """Abstract base class untuk semua turret."""

    # Subclass harus mendefinisikan nilai ini
    damage: int       = 0
    attack_speed: float = 1.0   # tembakan per detik
    range: float      = 100.0   # pixel
    cost: int         = 0

    def __init__(self, cell: Cell):
        self.cell: Cell = cell
        self.level: int = 1
        self._cooldown: float = 0.0
        self.target = None

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, enemies: list) -> "Projectile | None":
        """
        Kurangi cooldown, cari target, tembak jika siap.
        Return Projectile baru jika ada tembakan, else None.
        """
        self._cooldown -= dt
        self.target = self.find_target(enemies)

        if self.target and self._cooldown <= 0:
            self._cooldown = 1.0 / self.attack_speed
            return self.shoot(self.target)

        return None

    # ── targeting ─────────────────────────────────────────────────────────────

    def find_target(self, enemies: list):
        """Pilih enemy hidup terdekat yang masih dalam jangkauan."""
        cx, cy = self.cell.get_center()
        in_range = [
            e for e in enemies
            if e.alive and math.hypot(e.x - cx, e.y - cy) <= self.range
        ]
        if not in_range:
            return None
        return min(in_range, key=lambda e: math.hypot(e.x - cx, e.y - cy))

    # ── draw range (opsional, berguna saat debug / selected) ─────────────────

    def draw_range(self, surface: pygame.Surface):
        cx, cy = self.cell.get_center()
        range_surf = pygame.Surface(
            (int(self.range * 2), int(self.range * 2)), pygame.SRCALPHA
        )
        pygame.draw.circle(
            range_surf, (255, 255, 255, 30),
            (int(self.range), int(self.range)), int(self.range)
        )
        pygame.draw.circle(
            range_surf, (255, 255, 255, 80),
            (int(self.range), int(self.range)), int(self.range), 1
        )
        surface.blit(range_surf, (int(cx - self.range), int(cy - self.range)))

    # ── abstract ──────────────────────────────────────────────────────────────

    @abstractmethod
    def shoot(self, target) -> Projectile: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface): ...


# ── ArcherTower ───────────────────────────────────────────────────────────────

class ArcherTower(Turret):
    """Turret pemanah. Cepat, damage sedang, jangkauan luas."""

    damage: int         = 10
    attack_speed: float = 1.5   # tembakan/detik
    range: float        = 150.0
    cost: int           = 50

    def __init__(self, cell: Cell):
        super().__init__(cell)

    def shoot(self, target) -> Arrow:
        cx, cy = self.cell.get_center()
        return Arrow(cx, cy, target, self.damage)

    def draw(self, surface: pygame.Surface, hovered: bool = False):
        cx, cy = self.cell.get_center()
        size = 12

        # Badan: persegi coklat kayu
        body_rect = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
        pygame.draw.rect(surface, (139, 90, 43), body_rect, border_radius=2)
        pygame.draw.rect(surface, (90, 55, 20), body_rect, 2, border_radius=2)

        # "Busur": garis melengkung simulasi (arc)
        arc_rect = pygame.Rect(cx - 8, cy - 8, 16, 16)
        pygame.draw.arc(surface, (60, 35, 10), arc_rect,
                        math.radians(30), math.radians(150), 2)

        # Level badge (titik kecil di pojok)
        for i in range(self.level):
            pygame.draw.circle(surface, (255, 215, 0),
                               (int(cx) - 6 + i * 5, int(cy) + size // 2 + 4), 2)

        if hovered:
            self.draw_range(surface)
            rect = self.cell.get_rect()
            highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
            highlight.fill((255, 255, 100, 80))
            surface.blit(highlight, rect.topleft)


# ── CannonTower ───────────────────────────────────────────────────────────────

class CannonTower(Turret):
    """Turret meriam. Lambat, damage besar, splash area."""

    damage: int         = 60
    attack_speed: float = 0.4   # tembakan/detik
    range: float        = 120.0
    cost: int           = 120
    splash_radius: float = 60.0

    def __init__(self, cell: Cell):
        super().__init__(cell)

    def shoot(self, target) -> Cannonball:
        cx, cy = self.cell.get_center()
        return Cannonball(cx, cy, target, self.damage, self.splash_radius)

    def draw(self, surface: pygame.Surface, hovered: bool = False):
        cx, cy = self.cell.get_center()
        size = 18

        # Badan: lingkaran abu-abu besi
        pygame.draw.circle(surface, (80, 80, 90), (int(cx), int(cy)), size // 2 + 2)
        pygame.draw.circle(surface, (40, 40, 50), (int(cx), int(cy)), size // 2 + 2, 3)

        # Laras meriam: persegi panjang gelap
        barrel_rect = pygame.Rect(cx, cy - 3, size // 2 + 4, 6)
        if self.target:
            # Arahkan laras ke target jika ada
            tx, ty = self.target.x, self.target.y
            angle = math.atan2(ty - cy, tx - cx)
            barrel_len = size // 2 + 4
            ex = cx + math.cos(angle) * barrel_len
            ey = cy + math.sin(angle) * barrel_len
            pygame.draw.line(surface, (30, 30, 35), (int(cx), int(cy)),
                             (int(ex), int(ey)), 6)
            pygame.draw.line(surface, (60, 60, 70), (int(cx), int(cy)),
                             (int(ex), int(ey)), 3)
        else:
            # Default: laras ke kanan
            pygame.draw.rect(surface, (30, 30, 35), barrel_rect)

        # Level badge
        for i in range(self.level):
            pygame.draw.circle(surface, (255, 215, 0),
                               (int(cx) - 6 + i * 5, int(cy) + size // 2 + 4), 2)

        if hovered:
            self.draw_range(surface)
            rect = self.cell.get_rect()
            highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
            highlight.fill((255, 255, 100, 80))
            surface.blit(highlight, rect.topleft)
