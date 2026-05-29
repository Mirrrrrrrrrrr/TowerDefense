import pygame as pg
from map import Grid
from enemy import NormalEnemy, FastEnemy, TankEnemy
#from hud import HUD
#from turret import ArcherTower, CannonTower
import level_data

pg.init()

# ========== speed control ==========
class gameSpeedCtrl:
  SPEEDS: list[float] = [1.0, 2.0, 3.0]

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
    """Mencoba membeli dan menempatkan turret baru di cell."""
    if cell.can_place_turret():
      if cls.gold >= turret_class.cost:
        cls.gold -= turret_class.cost
        new_turret = turret_class(cell)
        cls.turrets.append(new_turret)
        cell.occupy()
        return True
      else:
        print(f"Gold tidak cukup! Harga: {turret_class.cost}, Gold kamu: {cls.gold}")
    return False

  @classmethod
  def get_turret_at(cls, cell):
    """Mengembalikan objek turret yang berada di cell tertentu."""
    if not cell:
      return None
    for t in cls.turrets:
      if t.cell is cell:
        return t
    return None

  @classmethod
  def can_upgrade_turret(cls, cell) -> bool:
    """Mengecek apakah turret di cell bisa di-upgrade."""
    target_turret = cls.get_turret_at(cell)
    if target_turret:
      return level_data.can_upgrade(target_turret, cls.gold)
    return False

  @classmethod
  def upgrade_turret(cls, cell) -> bool:
    """Menerapkan upgrade ke turret di cell jika gold cukup."""
    target_turret = cls.get_turret_at(cell)
    if target_turret and level_data.can_upgrade(target_turret, cls.gold):
      cost = level_data.apply_upgrade(target_turret)
      if cost > 0:
        cls.gold -= cost
        return True
    return False
  
