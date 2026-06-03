from collections import deque
from enemy import NormalEnemy, FastEnemy, TankEnemy
from wave_data import WAVE_DATA, SpawnEntry, WAVE_COOLDOWN
from assets import Assets

ENEMY_REGISTRY: dict[str, type] = {
    "NormalEnemy": NormalEnemy,
    "FastEnemy":   FastEnemy,
    "TankEnemy":   TankEnemy,
}

class WaveManager:
    def __init__(self, world_path: list[tuple[float, float]]):
        self.world_path = world_path

        self.wave_num:   int  = 0          # wave yang sedang/sudah berjalan (1-based)
        self.active:     bool = False      # True selama wave sedang berjalan
        self.all_done:   bool = False      # True setelah semua wave selesai

        # Tiap item: (enemy_class, wait_time)
        self._queue:        deque = deque()
        self._spawn_timer:  float = 0.0    # timer hitungan mundur antar spawn

        # ── cooldown antar wave ───────────────────────────────────────────────
        self._cooldown_timer: float = 0.0

    def start_wave(self):
        if self.wave_num >= len(WAVE_DATA):
            self.all_done = True
            return

        self.wave_num    += 1
        self.active       = True
        self._spawn_timer = 0.0
        self._queue       = self._build_queue(self.wave_num - 1)
        Assets.play_sound(Assets.SND_TEROMPET)

        print(f"[WaveManager] Wave {self.wave_num} dimulai "
              f"({sum(1 for _ in self._queue)} enemy)")

    def update(self, dt: float, enemies: list):
        if self.all_done:
            return

        if self.active:
            self._update_spawning(dt, enemies)
        else:
            self._update_cooldown(dt, enemies)

    # ── query ────────────────────────────────────────────────────────────────

    @property
    def is_wave_cleared(self, enemies: list = None) -> bool:
        # enemies harus dikirim lewat update(); properti ini untuk HUD saja
        return not self.active and not self._queue

    @property
    def next_wave_in(self) -> float:
        return max(0.0, WAVE_COOLDOWN - self._cooldown_timer)

    @property
    def total_waves(self) -> int:
        return len(WAVE_DATA)

    # ════════════════════════════════════════════════════════════════════════
    #  Internal
    # ════════════════════════════════════════════════════════════════════════

    def _build_queue(self, wave_idx: int) -> deque:
        q: deque = deque()
        groups: list[SpawnEntry] = WAVE_DATA[wave_idx]

        prev_interval = 0.0
        for entry in groups:
            if not isinstance(entry, SpawnEntry):
                print(f"[WaveManager] WARNING: tipe data tidak valid pada konfigurasi wave, dilewati.")
                continue
            enemy_cls = ENEMY_REGISTRY.get(entry.enemy_type)
            if enemy_cls is None:
                print(f"[WaveManager] WARNING: enemy '{entry.enemy_type}' tidak dikenal, dilewati.")
                continue
            for i in range(entry.count):
                wait = entry.delay if len(q) == 0 else prev_interval
                if i == 0 and len(q) > 0:
                    wait += entry.delay
                q.append((enemy_cls, wait))
                prev_interval = getattr(entry, "interval", 1.2)

        return q

    def _update_spawning(self, dt: float, enemies: list):
        if not self._queue:
            # Queue kosong -> tunggu semua enemy mati
            if len(enemies) == 0:
                self.active          = False
                self._cooldown_timer = 0.0
                print(f"[WaveManager] Wave {self.wave_num} selesai.")
            return

        enemy_cls, wait_time = self._queue[0]

        self._spawn_timer += dt
        if self._spawn_timer < wait_time:
            return

        self._spawn_timer = 0.0
        self._queue.popleft()

        new_enemy = enemy_cls(self.world_path)
        enemies.append(new_enemy)
        print(f"[WaveManager] Spawn {enemy_cls.__name__} "
              f"(sisa antrian: {len(self._queue)})")

    def _update_cooldown(self, dt: float, enemies: list):
        if self.wave_num == 0:
            # Belum pernah mulai -> auto-start wave pertama
            self.start_wave()
            return

        if self.wave_num >= len(WAVE_DATA):
            # Semua wave sudah selesai
            if len(enemies) == 0:
                self.all_done = True
            return

        self._cooldown_timer += dt
        if self._cooldown_timer >= WAVE_COOLDOWN:
            self._cooldown_timer = 0.0
            self.start_wave()
