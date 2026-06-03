"""
Format WAVE_DATA:
    list of wave, tiap wave = list of SpawnEntry(enemy_class_name, count, delay)

    enemy_class_name : string nama class ("NormalEnemy" | "FastEnemy" | "TankEnemy")
    count            : jumlah enemy yang di-spawn
    delay            : jeda tambahan (detik) SEBELUM grup ini di-spawn
                       (berguna untuk membuat "gelombang dalam gelombang")
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class SpawnEntry:
    enemy_type: str   # nama class enemy, di-resolve oleh WaveManager
    count:      int   # jumlah yang di-spawn berurutan
    interval:   float = 1.2  # jeda spawn antar enemy
    delay:      float = 0.0  # jeda detik sebelum grup ini mulai di-spawn


# ══════════════════════════════════════════════════════════════════════════════
#  WAVE DATA
#  Tambah baris baru di sini untuk menambah wave.
#  Setiap baris dalam satu wave = satu "grup" enemy.
# ══════════════════════════════════════════════════════════════════════════════

WAVE_DATA: list[list[SpawnEntry]] = [

    # ── Wave 1 — Tutorial ────────────────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 15, interval=1.0)
    ],

    # ── Wave 2 — Kenalkan FastEnemy ──────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 25, interval=0.6)
    ],

    # ── Wave 3 — TankEnemy pertama ───────────────────S────────────────────────
    [
        SpawnEntry("NormalEnemy", 15, interval=1.0),
        SpawnEntry("FastEnemy",   10, interval=0.6, delay=0.6)
    ],

    # ── Wave 4 — Tekanan meningkat ───────────────────────────────────────────
    [
        SpawnEntry("FastEnemy",   15, interval=0.4),
        SpawnEntry("NormalEnemy", 15, interval=0.6, delay=0.4)
    ],

    # ── Wave 5 — Boss wave ───────────────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 10, interval=0.6),
        SpawnEntry("FastEnemy",    5, interval=0.2, delay=0.75),
        SpawnEntry("NormalEnemy", 10, interval=0.6, delay=0.5),
        SpawnEntry("FastEnemy",    5, interval=0.2, delay=0.75),
        SpawnEntry("NormalEnemy", 10, interval=0.6, delay=0.5)
    ],

    # ── Wave 6 — Campuran serangan ───────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 10, interval=0.6),
        SpawnEntry("TankEnemy",   1, delay=1.2),
        SpawnEntry("FastEnemy",   15, interval=0.4, delay=0.8)
    ],

    # ── Wave 7 — All-out ─────────────────────────────────────────────────────
    [
        SpawnEntry("TankEnemy",   2, interval= 1.4),
        SpawnEntry("FastEnemy",   15, interval=0.4, delay=2.1)
    ],
    
    # ── Wave 8 — All-out ─────────────────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 10, interval=0.4),
        SpawnEntry("TankEnemy",   2, interval= 1.4, delay=0.4),
        SpawnEntry("FastEnemy",   10, interval=0.4, delay=0.4)
    ],

    # ── Wave 9 — All-out ─────────────────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 20, interval=0.4),
        SpawnEntry("FastEnemy",   20, interval=0.2, delay=0.6)
    ],

    # ── Wave 10 — All-out ─────────────────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 10, interval=0.4),
        SpawnEntry("TankEnemy",   3, interval= 1.4, delay=0.4),
        SpawnEntry("FastEnemy",   15, interval=0.2, delay=0.2),
        SpawnEntry("TankEnemy",   3,  interval= 1.4, delay=0.4),
        SpawnEntry("FastEnemy",   15, interval=0.2, delay=0.2),
        SpawnEntry("NormalEnemy", 10, interval=0.3, delay=2.1),
        SpawnEntry("TankEnemy",   5,  interval= 0.7, delay=0.2)
    ],
]

# Berapa detik jeda setelah wave selesai sebelum wave berikutnya otomatis mulai
WAVE_COOLDOWN: float = 8.0
