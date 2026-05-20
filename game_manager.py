import pygame as pg
from map import Grid
from enemy import NormalEnemy, FastEnemy, TankEnemy
#from hud import HUD
#from turret import ArcherTower, CannonTower

pg.init()

# ========== speed control ==========
class gameSpeedCtrl:
  SPEEDS: list[float] = [1.0, 2.0]

  def __init__(self):
    self.paused : bool = false
    self._speedIdx: int = 0

  def speed(self) -> float;
    return self.SPEEDS[self._speedIdx]

  def togglePause(self):
    self.paused = not self.paused

  def cycleSpeed(self):
    self._speedIdx = (self._speedIdx + 1) % len(self.SPEEDS)

  def getDt(self, rawDt: float) -> float:
    return 0.0 if self.paused else rawDt * self.speed




# ========== game manager ==========
class GameManager:
  lives: int = 100
  gold: int = 0
  gameOver: bool = False
  victory: bool = False

  
  
  turrets: list = []
  enemies: list = []
  projectile: list = []
  
