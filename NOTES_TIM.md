# Tower Defense — Catatan Pembagian Tugas Tim

> **Status map:** ✅ Selesai (`map.py` + `main.py`)
> Ketika bagian masing-masing sudah selesai (garis besar / skeleton), serahkan ke koordinator untuk digabungkan dan dirapihkan.

---

## Konvensi Umum (wajib diikuti semua)

- **Semua file taruh satu folder** dengan `main.py` dan `map.py`
- **Semua `update()` wajib menerima parameter `dt: float`** — jangan pakai `pygame.time.get_ticks()` sendiri
- **Jangan panggil `pygame.init()` atau `pygame.display.set_mode()`** di luar `main.py`
- Import yang dibutuhkan dari `map.py`:
  ```python
  from map import Grid, Cell, TILE_PATH, TILE_EMPTY, TILE_SPAWN, TILE_BASE
  ```
- Gunakan **type hint** di setiap method agar mudah digabung

---

## 1. Turret & Projectile — `turret.py` + `projectile.py`

**Penanggung jawab:** ___________

### Apa yang harus dibuat

**`projectile.py`** — dua class:

| Class | Keterangan |
|---|---|
| `Projectile` | Abstract base class |
| `Arrow` | Subclass, single target |
| `Cannonball` | Subclass, area damage (splash) |

```
Projectile (ABC)
├── x, y: float
├── damage: int
├── target: Enemy
├── active: bool
├── update(dt) → gerak menuju target
├── on_hit(enemy, enemies) {abstract}
└── draw(surface) {abstract}

Arrow(Projectile)
├── speed = 300
├── on_hit(enemy, enemies) → damage satu target
└── draw(surface) → garis/segitiga kecil

Cannonball(Projectile)
├── speed = 150
├── splash_radius: float
├── on_hit(enemy, enemies) → damage semua enemy dalam radius
└── draw(surface) → lingkaran gelap
```

**`turret.py`** — tiga class:

```
Turret (ABC)
├── cell: Cell          ← dari map.py
├── damage: int
├── attack_speed: float (tembakan/detik)
├── range: float        (pixel)
├── cost: int
├── level: int = 1
├── _cooldown: float = 0
├── target: Enemy | None
├── update(dt, enemies) → kurangi cooldown, cari target, tembak
├── find_target(enemies) → Enemy | None   (terdekat dalam range)
├── shoot(target) → Projectile {abstract}
└── draw(surface) {abstract}

ArcherTower(Turret)
├── damage = 10
├── attack_speed = 1.5
├── range = 150
├── cost = 50
├── shoot(target) → Arrow
└── draw(surface)

CannonTower(Turret)
├── damage = 60
├── attack_speed = 0.4
├── range = 120
├── cost = 120
├── splash_radius = 60
├── shoot(target) → Cannonball
└── draw(surface)
```

### Yang perlu diperhatikan

- `update()` mengembalikan `Projectile | None` — jika ada tembakan baru, kembalikan objeknya agar bisa ditambahkan ke list di `main.py`
- `find_target()` hitung jarak dengan `math.hypot(enemy.x - cx, enemy.y - cy)` dimana `cx, cy = self.cell.get_center()`
- Gambar range circle saat turret dipilih (opsional tapi berguna untuk debug)
- `Cannonball.on_hit()` menerima `enemies: list` untuk iterasi splash

### Contoh skeleton minimal

```python
# turret.py
import pygame, math
from abc import ABC, abstractmethod
from map import Cell

class Turret(ABC):
    def __init__(self, cell: Cell):
        self.cell = cell
        self.level = 1
        self._cooldown = 0.0
        self.target = None
        # subclass definisikan: damage, attack_speed, range, cost

    def update(self, dt: float, enemies: list):
        self._cooldown -= dt
        self.target = self.find_target(enemies)
        if self.target and self._cooldown <= 0:
            self._cooldown = 1.0 / self.attack_speed
            return self.shoot(self.target)
        return None

    def find_target(self, enemies: list):
        cx, cy = self.cell.get_center()
        in_range = [e for e in enemies
                    if e.alive and math.hypot(e.x - cx, e.y - cy) <= self.range]
        return min(in_range, key=lambda e: math.hypot(e.x - cx, e.y - cy), default=None)

    @abstractmethod
    def shoot(self, target) -> "Projectile": ...

    @abstractmethod
    def draw(self, surface: pygame.Surface): ...
```

---

## 2. Enemy — `enemy.py`

**Penanggung jawab:** ___________

### Apa yang harus dibuat

**`enemy.py`** — empat class:

```
Enemy (ABC)
├── x, y: float          ← posisi dunia (pixel), init dari path[0].get_center()
├── hp: int
├── max_hp: int
├── speed: float
├── reward: int          ← gold yang didapat saat enemy mati
├── alive: bool = True
├── reached_base: bool = False
├── path_index: int = 0  ← indeks ke world_path yang sedang dituju
├── take_damage(dmg)     → kurangi hp, set alive=False jika <= 0
├── update(dt, world_path) → gerak sepanjang path
└── draw(surface) {abstract}

NormalEnemy(Enemy)
├── hp = max_hp = 100
├── speed = 1.5  (pixel/frame × dt)  → sesuaikan agar terasa wajar
├── reward = 10
└── draw(surface) → kotak/lingkaran hijau + health bar

FastEnemy(Enemy)
├── hp = max_hp = 40
├── speed = 3.5
├── reward = 15
└── draw(surface) → kotak/lingkaran biru kecil

TankEnemy(Enemy)
├── hp = max_hp = 400
├── speed = 0.8
├── reward = 30
└── draw(surface) → kotak/lingkaran merah besar
```

### Yang perlu diperhatikan

- `x, y` adalah posisi **pixel di layar**, bukan koordinat grid
- `update()` menerima `world_path: list[tuple[float, float]]` dari `grid.world_path`
- Gerak menuju `world_path[path_index]`, jika sudah sampai (`dist < 2`) increment `path_index`
- Jika `path_index >= len(world_path)`: set `reached_base = True`, `alive = False`
- Gambar **health bar** di atas sprite — sangat membantu gameplay

### Contoh skeleton minimal

```python
# enemy.py
import pygame, math
from abc import ABC, abstractmethod

class Enemy(ABC):
    def __init__(self, world_path: list):
        self.x, self.y = world_path[0]
        self.path_index = 1
        self.alive = True
        self.reached_base = False
        # subclass definisikan: hp, max_hp, speed, reward

    def take_damage(self, dmg: int):
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, dt: float, world_path: list):
        if not self.alive or self.path_index >= len(world_path):
            if self.path_index >= len(world_path):
                self.reached_base = True
                self.alive = False
            return
        tx, ty = world_path[self.path_index]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 2:
            self.path_index += 1
        else:
            move = self.speed * dt * 60   # kalikan 60 agar speed terasa wajar di 60 FPS
            self.x += (dx / dist) * move
            self.y += (dy / dist) * move

    def _draw_health_bar(self, surface: pygame.Surface, width: int, height: int):
        ratio = self.hp / self.max_hp
        bar_w = width
        pygame.draw.rect(surface, (180, 0, 0),   (self.x - bar_w//2, self.y - height//2 - 8, bar_w, 5))
        pygame.draw.rect(surface, (0, 220, 0),   (self.x - bar_w//2, self.y - height//2 - 8, int(bar_w * ratio), 5))

    @abstractmethod
    def draw(self, surface: pygame.Surface): ...
```

---

## 3. HUD — `hud.py`

**Penanggung jawab:** ___________

> **Catatan:** `GameState` dan `GameSpeedCtrl` sudah ada di `main.py`.
> HUD hanya perlu **membaca** state tersebut dan **menangani klik tombol**.

### Apa yang harus dibuat

**`hud.py`** — satu class `HUD`:

```
HUD
├── font, font_small: pygame.font.Font
├── btn_pause: pygame.Rect
├── btn_speed: pygame.Rect
├── btn_upgrade: pygame.Rect
├── shop_buttons: list[dict]   ← {rect, turret_type, cost, label}
├── selected_turret_type: type | None
├── draw(surface, state, speed_ctrl, hovered_cell)
└── handle_click(pos, state, speed_ctrl, grid) → str | None
     # return: "placed", "upgraded", "paused", "speed", None
```

### Panel yang harus digambar

| Area | Konten |
|---|---|
| Kiri atas | ❤ lives, ⬡ gold, Wave N |
| Tengah atas | info cell yang dihover (tipe, koordinat) |
| Kanan atas | tombol PAUSE dan tombol SPEED (1×/2×/3×) |
| Bawah layar | shop turret (ArcherTower 50g, CannonTower 120g) + tombol UPGRADE |

### Alur klik yang harus ditangani

```
handle_click(pos, ...)
├── klik btn_pause  → speed_ctrl.toggle_pause()
├── klik btn_speed  → speed_ctrl.cycle_speed()
├── klik shop button
│   └── set selected_turret_type = turret_class
├── klik btn_upgrade
│   └── jika ada turret terpilih di cell → upgrade_system.upgrade(turret)
└── klik grid (delegasikan ke main.py, bukan di sini)
```

### Yang perlu diperhatikan

- HUD **tidak boleh** langsung memanggil `update()` — hanya `draw()` dan event handling
- Tombol shop harus **grey out** jika gold tidak cukup
- Tampilkan level turret (`Lv.1 / Lv.2 / Lv.3`) di tooltip saat hover cell berisi turret
- Tombol UPGRADE hanya aktif jika cell yang diklik berisi turret & level < 3
- `draw()` selalu dipanggil, bahkan saat pause — HUD tidak boleh freeze

### Contoh skeleton minimal

```python
# hud.py
import pygame

class HUD:
    PANEL_H = 60   # tinggi panel atas
    SHOP_H  = 70   # tinggi panel bawah (shop)

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font   = pygame.font.SysFont("monospace", 15)
        self.font_s = pygame.font.SysFont("monospace", 12)
        self.selected_turret_type = None

        # tombol kanan atas
        self.btn_pause = pygame.Rect(screen_w - 160, 12, 70, 34)
        self.btn_speed = pygame.Rect(screen_w -  82, 12, 70, 34)
        self.btn_upgrade = pygame.Rect(screen_w - 160, screen_h - self.SHOP_H + 10, 140, 40)

    def draw(self, surface: pygame.Surface, state, speed_ctrl, hovered_cell=None):
        # TODO: gambar panel atas, panel bawah (shop), tombol-tombol
        pass

    def handle_click(self, pos: tuple, state, speed_ctrl, grid) -> str | None:
        # TODO: deteksi klik pada setiap tombol
        return None
```

---

## Cara Menyerahkan Hasil

1. Pastikan file bisa di-`import` tanpa error: `python -c "import turret"` dsb
2. **Jangan ubah** `map.py` atau `main.py` — jika ada masalah kompatibilitas, catat di komentar
3. Setiap class/method yang belum selesai, tandai dengan `# TODO: ...`
4. Serahkan file `.py` ke koordinator beserta catatan singkat apa yang sudah/belum selesai

---

*Dokumen ini dibuat otomatis. Perbarui kolom penanggung jawab sebelum dibagikan.*
