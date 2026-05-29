"""
wave_data.py — Definisi komposisi setiap wave
Ubah file ini untuk mendesain tingkat kesulitan game.

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
    delay:      float = 0.0  # jeda detik sebelum grup ini mulai di-spawn


# ══════════════════════════════════════════════════════════════════════════════
#  WAVE DATA
#  Tambah baris baru di sini untuk menambah wave.
#  Setiap baris dalam satu wave = satu "grup" enemy.
# ══════════════════════════════════════════════════════════════════════════════

WAVE_DATA: list[list[SpawnEntry]] = [

    # ── Wave 1 — Tutorial ────────────────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 5),
    ],

    # ── Wave 2 — Kenalkan FastEnemy ──────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 4),
        SpawnEntry("FastEnemy",   3, delay=2.0),   # FastEnemy muncul 2 detik setelah Normal
    ],

    # ── Wave 3 — TankEnemy pertama ───────────────────────────────────────────
    [
        SpawnEntry("FastEnemy",   4),
        SpawnEntry("NormalEnemy", 3, delay=1.0),
        SpawnEntry("TankEnemy",   1, delay=3.0),
    ],

    # ── Wave 4 — Tekanan meningkat ───────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 5),
        SpawnEntry("FastEnemy",   5, delay=1.5),
        SpawnEntry("TankEnemy",   2, delay=4.0),
    ],

    # ── Wave 5 — Boss wave ───────────────────────────────────────────────────
    [
        SpawnEntry("FastEnemy",   6),
        SpawnEntry("NormalEnemy", 6, delay=1.0),
        SpawnEntry("TankEnemy",   4, delay=5.0),
    ],

    # ── Wave 6 — Campuran serangan ───────────────────────────────────────────
    [
        SpawnEntry("NormalEnemy", 4),
        SpawnEntry("FastEnemy",   6, delay=0.5),
        SpawnEntry("TankEnemy",   3, delay=3.0),
        SpawnEntry("FastEnemy",   4, delay=2.0),
    ],

    # ── Wave 7 — All-out ─────────────────────────────────────────────────────
    [
        SpawnEntry("TankEnemy",   3),
        SpawnEntry("FastEnemy",   8, delay=2.0),
        SpawnEntry("NormalEnemy", 6, delay=1.0),
        SpawnEntry("TankEnemy",   3, delay=4.0),
    ],
]

# Berapa detik jeda setelah wave selesai sebelum wave berikutnya otomatis mulai
WAVE_COOLDOWN: float = 8.0

# Interval spawn antar enemy dalam satu grup (detik)
SPAWN_INTERVAL: float = 1.2
