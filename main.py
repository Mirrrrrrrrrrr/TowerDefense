import pygame as pg
from assets import Assets
from map import Grid
from enemy import NormalEnemy, FastEnemy, TankEnemy
from turret import ArcherTower, CannonTower
from game_manager import GameManager, gameSpeedCtrl
from hud import HUD

pg.init()
Assets.load()

COLS, ROWS, CELL = 16, 16, 48
HUD_WIDTH = 300
screen = pg.display.set_mode((COLS * CELL + HUD_WIDTH, ROWS * CELL))
grid = Grid(cols = COLS, rows = ROWS, cellSize = CELL, offset_x = HUD_WIDTH)
clock = pg.time.Clock()
font  = pg.font.SysFont("monospace", 14)

# ── Setup HUD & Speed Control ────────────────────────────────────────────────
speed_ctrl = gameSpeedCtrl()
hud = HUD(COLS * CELL + HUD_WIDTH, ROWS * CELL, HUD_WIDTH)

# ── Bangun world_path dari grid.path ─────────────────────────────────────────
# world_path = list koordinat pixel pusat setiap cell di path
world_path: list[tuple[float, float]] = [
    cell.get_center() for cell in grid.path
]

# ── Spawn timer sederhana ─────────────────────────────────────────────────────
SPAWN_INTERVAL = 2.0   # detik antar spawn
spawn_timer    = 0.0
spawn_queue    = [NormalEnemy, FastEnemy, NormalEnemy, TankEnemy,
                FastEnemy, NormalEnemy, TankEnemy]  # urutan enemy yang muncul
spawn_index    = 0

# ── Beri Gold Awal ────────────────────────────────────────────────────────────
GameManager.gold = 500  # Agar bisa membeli turret untuk testing

# ── Game loop ─────────────────────────────────────────────────────────────────
running = True
while running:
    raw_dt = clock.tick(60) / 1000.0   # delta time dalam detik
    dt = speed_ctrl.getDt(raw_dt)
    mousePos = pg.mouse.get_pos()

    # ── Event ─────────────────────────────────────────────────────────────────
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:  # Klik Kiri
                action = hud.handle_click(mousePos, GameManager, speed_ctrl, grid)
                if not action and mousePos[0] < hud.hud_x:
                    GameManager.selected_cell = grid.cell_at_pos(*mousePos)

    # ── Spawn enemy ───────────────────────────────────────────────────────────
    if world_path and spawn_index < len(spawn_queue):
        spawn_timer += dt
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0.0
            enemy_cls = spawn_queue[spawn_index]
            GameManager.enemies.append(enemy_cls(world_path))
            spawn_index += 1

    # ── Update enemy ──────────────────────────────────────────────────────────
    for enemy in GameManager.enemies:
        enemy.update(dt, world_path)
        if enemy.reached_base:
            GameManager.lives = max(0, GameManager.lives - enemy.damage_to_base)
        elif not enemy.alive:
            GameManager.gold += enemy.reward

    GameManager.enemies = [e for e in GameManager.enemies if e.alive]

    # ── Update turret ─────────────────────────────────────────────────────────
    for turret in GameManager.turrets:
        proj = turret.update(dt, GameManager.enemies)
        if proj:
            GameManager.projectile.append(proj)

    # ── Update projectile ─────────────────────────────────────────────────────
    for proj in GameManager.projectile:
        proj.update(dt, GameManager.enemies)

    GameManager.projectile = [p for p in GameManager.projectile if p.active]

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill((0, 0, 0))
    
    is_hovering_grid = mousePos[0] < hud.hud_x
    hovered_cell = grid.cell_at_pos(*mousePos) if is_hovering_grid else None
    grid.draw(screen, show_grid=True, mousePos=mousePos if is_hovering_grid else None)

    for enemy in GameManager.enemies:
        enemy.draw(screen)

    for turret in GameManager.turrets:
        turret.draw(screen)

    for proj in GameManager.projectile:
        proj.draw(screen)

    hud.draw(screen, GameManager, speed_ctrl, hovered_cell, GameManager.selected_cell)

    pg.display.flip()

pg.quit()
