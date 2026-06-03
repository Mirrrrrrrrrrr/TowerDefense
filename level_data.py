"""
Format TURRET_LEVELS:
    {
        "NamaClass": [
            LevelData(level, damage, attack_speed, range, upgrade_cost),
            ...  # index 0 = level 1, index 1 = level 2, dst
        ]
    }

    level        : nomor level (1 = base, maks MAX_LEVEL)
    damage       : damage per tembakan
    attack_speed : tembakan per detik
    range        : jangkauan dalam pixel
    upgrade_cost : biaya gold untuk naik KE level ini (level 1 = harga beli awal)
"""

from dataclasses import dataclass


MAX_LEVEL: int = 3


@dataclass(frozen=True)
class LevelData:
    level:        int
    damage:       int
    attack_speed: float   # tembakan / detik
    range:        float   # pixel
    upgrade_cost: int     # gold untuk naik ke level ini


# ══════════════════════════════════════════════════════════════════════════════
#  TURRET LEVEL SHEET
#  Tambah level baru atau ubah nilai sesuai kebutuhan balancing.
# ══════════════════════════════════════════════════════════════════════════════

TURRET_LEVELS: dict[str, list[LevelData]] = {

    # ── ArcherTower ──────────────────────────────────────────────────────────
    # Cepat, single target, jangkauan luas
    "ArcherTower": [
        LevelData(level=1, damage=10,  attack_speed=1.5, range=120.0, upgrade_cost=100),   # harga beli
        LevelData(level=2, damage=12,  attack_speed=1.7, range=145.0, upgrade_cost=75),   # +65% dmg, lebih cepat
        LevelData(level=3, damage=15,  attack_speed=2.0, range=180.0, upgrade_cost=125),  # +67% dmg lagi
    ],

    # ── CannonTower ──────────────────────────────────────────────────────────
    # Lambat, AoE, damage besar
    "CannonTower": [
        LevelData(level=1, damage=40,  attack_speed=0.3, range=80.0, upgrade_cost=225),  # harga beli
        LevelData(level=2, damage=50, attack_speed=0.4, range=110.0, upgrade_cost=150),  # splash makin kuat
        LevelData(level=3, damage=60, attack_speed=0.5, range=140.0, upgrade_cost=275),  # endgame
    ],
}

CANNON_SPLASH: dict[int, float] = {
    1: 20.0, 
    2: 30.0,
    3: 40.0,
}
