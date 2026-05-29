"""
wave_manager.py — Spawn dan manajemen wave enemy
Membaca komposisi wave dari wave_data.py.

Penggunaan di main.py / game_manager.py:
    from wave_manager import WaveManager

    wave_mgr = WaveManager(world_path)
    wave_mgr.start_wave()       # mulai wave pertama

    # di game loop:
    wave_mgr.update(dt, enemies)
"""

from collections import deque
from enemy import NormalEnemy, FastEnemy, TankEnemy
from wave_data import WAVE_DATA, SpawnEntry, WAVE_COOLDOWN, SPAWN_INTERVAL


# ── Mapping nama string → class enemy ────────────────────────────────────────
ENEMY_REGISTRY: dict[str, type] = {
    "NormalEnemy": NormalEnemy,
    "FastEnemy":   FastEnemy,
    "TankEnemy":   TankEnemy,
}


# ════════════════════════════════════════════════════════════════════════════
#  WaveManager
# ════════════════════════════════════════════════════════════════════════════

class WaveManager:
    """
    Mengelola urutan wave dan spawn enemy berdasarkan WAVE_DATA.

    State machine sederhana:
        IDLE  → start_wave() → DELAY (jika ada delay grup)
              → SPAWNING     → (queue habis) → WAITING
              → (semua enemy mati) → COOLDOWN
              → (cooldown habis) → IDLE / selesai
    """

    def __init__(self, world_path: list[tuple[float, float]]):
        self.world_path = world_path

        # ── state ────────────────────────────────────────────────────────────
        self.wave_num:   int  = 0          # wave yang sedang/sudah berjalan (1-based)
        self.active:     bool = False      # True selama wave sedang berjalan
        self.all_done:   bool = False      # True setelah semua wave selesai

        # ── antrian spawn ────────────────────────────────────────────────────
        # Tiap item: (enemy_class, sisa_delay_grup)
        # sisa_delay_grup > 0  → tunggu dulu, belum boleh spawn
        self._queue:        deque = deque()
        self._spawn_timer:  float = 0.0    # timer interval antar enemy dalam grup
        self._group_delay:  float = 0.0    # sisa delay sebelum grup berikutnya boleh spawn

        # ── cooldown antar wave ───────────────────────────────────────────────
        self._cooldown_timer: float = 0.0

    # ════════════════════════════════════════════════════════════════════════
    #  Public API
    # ════════════════════════════════════════════════════════════════════════

    def start_wave(self):
        """Mulai wave berikutnya. Dipanggil manual atau otomatis dari update()."""
        if self.wave_num >= len(WAVE_DATA):
            self.all_done = True
            return

        self.wave_num    += 1
        self.active       = True
        self._spawn_timer = 0.0
        self._group_delay = 0.0
        self._queue       = self._build_queue(self.wave_num - 1)

        print(f"[WaveManager] Wave {self.wave_num} dimulai "
              f"({sum(1 for _ in self._queue)} enemy)")

    def update(self, dt: float, enemies: list):
        """
        Dipanggil setiap frame.
        - Saat active: spawn enemy dari queue
        - Saat queue habis + semua enemy mati: masuk cooldown
        - Saat cooldown habis: auto-start wave berikutnya
        """
        if self.all_done:
            return

        if self.active:
            self._update_spawning(dt, enemies)
        else:
            self._update_cooldown(dt, enemies)

    # ── query ────────────────────────────────────────────────────────────────

    @property
    def is_wave_cleared(self, enemies: list = None) -> bool:
        """True jika queue kosong dan tidak ada enemy hidup."""
        # enemies harus dikirim lewat update(); properti ini untuk HUD saja
        return not self.active and not self._queue

    @property
    def next_wave_in(self) -> float:
        """Sisa detik sebelum wave berikutnya (untuk HUD countdown)."""
        return max(0.0, WAVE_COOLDOWN - self._cooldown_timer)

    @property
    def total_waves(self) -> int:
        return len(WAVE_DATA)

    # ════════════════════════════════════════════════════════════════════════
    #  Internal
    # ════════════════════════════════════════════════════════════════════════

    def _build_queue(self, wave_idx: int) -> deque:
        """
        Bangun antrian dari WAVE_DATA[wave_idx].
        Format antrian: deque of (enemy_class, group_delay)
        group_delay hanya diterapkan pada enemy pertama tiap grup.
        """
        q: deque = deque()
        groups: list[SpawnEntry] = WAVE_DATA[wave_idx]

        for entry in groups:
            enemy_cls = ENEMY_REGISTRY.get(entry.enemy_type)
            if enemy_cls is None:
                print(f"[WaveManager] WARNING: enemy '{entry.enemy_type}' tidak dikenal, dilewati.")
                continue
            for i in range(entry.count):
                # delay grup hanya pada enemy pertama dalam grup
                group_delay = entry.delay if i == 0 else 0.0
                q.append((enemy_cls, group_delay))

        return q

    def _update_spawning(self, dt: float, enemies: list):
        """Handle spawn logic saat wave aktif."""
        if not self._queue:
            # Queue kosong → tunggu semua enemy mati
            if not any(e.alive for e in enemies):
                self.active          = False
                self._cooldown_timer = 0.0
                print(f"[WaveManager] Wave {self.wave_num} selesai.")
            return

        # Hitung sisa delay grup
        if self._group_delay > 0:
            self._group_delay -= dt
            return

        # Hitung interval antar spawn
        self._spawn_timer += dt
        if self._spawn_timer < SPAWN_INTERVAL:
            return

        # Spawn satu enemy
        self._spawn_timer = 0.0
        enemy_cls, group_delay = self._queue.popleft()
        self._group_delay = group_delay   # terapkan ke enemy berikutnya (kepala queue baru)

        new_enemy = enemy_cls(self.world_path)
        enemies.append(new_enemy)
        print(f"[WaveManager] Spawn {enemy_cls.__name__} "
              f"(sisa antrian: {len(self._queue)})")

    def _update_cooldown(self, dt: float, enemies: list):
        """Handle cooldown antar wave."""
        if self.wave_num == 0:
            # Belum pernah mulai → auto-start wave pertama
            self.start_wave()
            return

        if self.wave_num >= len(WAVE_DATA):
            # Semua wave sudah selesai
            if not any(e.alive for e in enemies):
                self.all_done = True
            return

        self._cooldown_timer += dt
        if self._cooldown_timer >= WAVE_COOLDOWN:
            self._cooldown_timer = 0.0
            self.start_wave()
