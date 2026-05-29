"""
level_data.py — Stat sheet upgrade turret per level
Ubah file ini untuk menyeimbangkan ekonomi dan kekuatan turret.

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
        LevelData(level=1, damage=10,  attack_speed=1.5, range=150.0, upgrade_cost=50),   # harga beli
        LevelData(level=2, damage=18,  attack_speed=2.0, range=165.0, upgrade_cost=75),   # +65% dmg, lebih cepat
        LevelData(level=3, damage=30,  attack_speed=2.5, range=180.0, upgrade_cost=100),  # +67% dmg lagi
    ],

    # ── CannonTower ──────────────────────────────────────────────────────────
    # Lambat, AoE, damage besar
    "CannonTower": [
        LevelData(level=1, damage=60,  attack_speed=0.4, range=120.0, upgrade_cost=120),  # harga beli
        LevelData(level=2, damage=100, attack_speed=0.5, range=135.0, upgrade_cost=150),  # splash makin kuat
        LevelData(level=3, damage=160, attack_speed=0.6, range=150.0, upgrade_cost=200),  # endgame
    ],
}

# Splash radius CannonTower per level (terpisah karena unik untuk Cannon)
CANNON_SPLASH: dict[int, float] = {
    1: 60.0,
    2: 75.0,
    3: 90.0,
}


# ══════════════════════════════════════════════════════════════════════════════
#  Helper functions — dipakai oleh UpgradeSystem / HUD
# ══════════════════════════════════════════════════════════════════════════════

def get_level_data(turret_class_name: str, level: int) -> LevelData | None:
    """
    Ambil LevelData untuk turret tertentu di level tertentu.
    Return None jika tidak ditemukan.
    """
    sheet = TURRET_LEVELS.get(turret_class_name)
    if not sheet:
        return None
    for ld in sheet:
        if ld.level == level:
            return ld
    return None


def get_upgrade_cost(turret_class_name: str, current_level: int) -> int | None:
    """
    Biaya upgrade dari current_level ke current_level+1.
    Return None jika sudah MAX_LEVEL.
    """
    if current_level >= MAX_LEVEL:
        return None
    next_ld = get_level_data(turret_class_name, current_level + 1)
    return next_ld.upgrade_cost if next_ld else None


def can_upgrade(turret, gold: int) -> bool:
    """
    Cek apakah turret bisa di-upgrade (level belum maks dan gold cukup).
    turret harus punya atribut .level dan nama class yang ada di TURRET_LEVELS.
    """
    cost = get_upgrade_cost(type(turret).__name__, turret.level)
    if cost is None:
        return False
    return gold >= cost


def apply_upgrade(turret) -> int:
    """
    Terapkan upgrade ke turret: naikkan level dan update stats.
    Return biaya yang harus dipotong dari gold (0 jika gagal).

    Turret harus punya atribut:
        .level, .damage, .attack_speed, .range
    CannonTower juga harus punya .splash_radius.
    """
    class_name = type(turret).__name__
    cost = get_upgrade_cost(class_name, turret.level)
    if cost is None:
        return 0   # sudah max level

    turret.level += 1
    ld = get_level_data(class_name, turret.level)
    if not ld:
        turret.level -= 1   # rollback
        return 0

    # terapkan stats baru
    turret.damage       = ld.damage
    turret.attack_speed = ld.attack_speed
    turret.range        = ld.range

    # khusus Cannon: update splash_radius
    if class_name == "CannonTower" and hasattr(turret, "splash_radius"):
        turret.splash_radius = CANNON_SPLASH.get(turret.level, turret.splash_radius)

    return cost
