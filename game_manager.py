import pygame as pg
from map import Grid
from enemy import NormalEnemy, FastEnemy, TankEnemy
from assets import Assets
import level_data

pg.init()

# ========== game settings ==========
class GameSettings:
    SOUND_ON = True
    MUSIC_ON = True
    SHOW_GRID = True

# ========== speed control ==========
class gameSpeedCtrl:
  SPEEDS: list[float] = [1.0, 2.0, 4.0]

  def __init__(self):
    self.paused : bool = False
    self._speedIdx: int = 0

  @property
  def speed(self) -> float:
    return self.SPEEDS[self._speedIdx]

  def toggle_pause(self):
    self.paused = not self.paused

  def cycle_speed(self):
    self._speedIdx = (self._speedIdx + 1) % len(self.SPEEDS)

  def getDt(self, rawDt: float) -> float:
    return 0.0 if self.paused else rawDt * self.speed


# ========== game manager ==========
class GameManager:
  lives: int = 100
  gold: int = 0
  wave: int = 1
  selected_cell = None
  gameOver: bool = False
  victory: bool = False

  turrets: list = []
  enemies: list = []
  projectile: list = []

  @classmethod
  def buy_and_place_turret(cls, turret_class, cell) -> bool:
    if cell.can_place_turret():
      if cls.gold >= turret_class.cost:
        cls.gold -= turret_class.cost
        new_turret = turret_class(cell)
        cls.turrets.append(new_turret)
        cell.occupy()
        Assets.play_sound(Assets.SND_BUY)
        return True
      else:
        print(f"Gold tidak cukup! Harga: {turret_class.cost}, Gold kamu: {cls.gold}")
    return False

  @classmethod
  def get_turret_at(cls, cell):
    if not cell:
      return None
    for t in cls.turrets:
      if t.cell is cell:
        return t
    return None

  @classmethod
  def can_upgrade_turret(cls, cell) -> bool:
    target_turret = cls.get_turret_at(cell)
    if target_turret:
      return cls.can_upgrade(target_turret, cls.gold)
    return False

  @classmethod
  def upgrade_turret(cls, cell) -> bool:
    target_turret = cls.get_turret_at(cell)
    if target_turret and cls.can_upgrade(target_turret, cls.gold):
      cost = cls.__apply_upgrade(target_turret)
      if cost > 0:
        cls.gold -= cost
        Assets.play_sound(Assets.SND_UPGRADE)
        return True
    return False

  @classmethod
  def __apply_upgrade(cls, turret) -> int:
    class_name = type(turret).__name__
    cost = cls.get_upgrade_cost(class_name, turret.level)
    if cost is None:
        return 0

    turret.level += 1
    ld = cls.get_level_data(class_name, turret.level)
    if not ld:
        turret.level -= 1
        return 0

    turret.damage       = ld.damage
    turret.attack_speed = ld.attack_speed
    turret.range        = ld.range

    if class_name == "CannonTower" and hasattr(turret, "splash_radius"):
        turret.splash_radius = level_data.CANNON_SPLASH.get(turret.level, turret.splash_radius)

    return cost

  @classmethod
  def get_level_data(cls, turret_class_name: str, level: int):
    """
    Ambil LevelData untuk turret tertentu di level tertentu.
    Return None jika tidak ditemukan.
    """
    sheet = level_data.TURRET_LEVELS.get(turret_class_name)
    if not sheet:
        return None
    for ld in sheet:
        if ld.level == level:
            return ld
    return None

  @classmethod
  def get_upgrade_cost(cls, turret_class_name: str, current_level: int) -> int | None:
    """
    Biaya upgrade dari current_level ke current_level+1.
    Return None jika sudah MAX_LEVEL.
    """
    if current_level >= level_data.MAX_LEVEL:
        return None
    next_ld = cls.get_level_data(turret_class_name, current_level + 1)
    return next_ld.upgrade_cost if next_ld else None

  @classmethod
  def can_upgrade(cls, turret, gold: int) -> bool:
    """
    Cek apakah turret bisa di-upgrade (level belum maks dan gold cukup).
    turret harus punya atribut .level dan nama class yang ada di TURRET_LEVELS.
    """
    cost = cls.get_upgrade_cost(type(turret).__name__, turret.level)
    if cost is None:
        return False
    return gold >= cost
