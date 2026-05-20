import pygame as pg
from map import Grid
from enemy import NormalEnemy, FastEnemy, TankEnemy

pg.init()
Assets.load()

COLS, ROWS, CELL = 16, 16, 48
HUD_WIDTH = 300
screen = pg.display.set_mode((COLS * CELL + HUD_WIDTH, ROWS * CELL))
grid = Grid(cols = COLS, rows = ROWS, cellSize = CELL, offset_x = HUD_WIDTH)
clock = pg.time.Clock()
font  = pg.font.SysFont("monospace", 14)

# ── Bangun world_path dari grid.path ─────────────────────────────────────────
# world_path = list koordinat pixel pusat setiap cell di path
world_path: list[tuple[float, float]] = [
    cell.get_center() for cell in grid.path
]

# ── List enemy aktif ──────────────────────────────────────────────────────────
enemies: list = []

# ── Spawn timer sederhana ─────────────────────────────────────────────────────
SPAWN_INTERVAL = 2.0   # detik antar spawn
spawn_timer    = 0.0
spawn_queue    = [NormalEnemy, FastEnemy, NormalEnemy, TankEnemy,
                FastEnemy, NormalEnemy, TankEnemy]  # urutan enemy yang muncul
spawn_index    = 0

# ── Game loop ─────────────────────────────────────────────────────────────────
running = True
while running:
    dt = clock.tick(60) / 1000.0   # delta time dalam detik
    mousePos = pg.mouse.get_pos()

    # ── Event ─────────────────────────────────────────────────────────────────
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            running = False

    # ── Spawn enemy ───────────────────────────────────────────────────────────
    if world_path and spawn_index < len(spawn_queue):
        spawn_timer += dt
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0.0
            enemy_cls = spawn_queue[spawn_index]
            enemies.append(enemy_cls(world_path))
            spawn_index += 1

    # ── Update enemy ──────────────────────────────────────────────────────────
    for enemy in enemies:
        enemy.update(dt, world_path)

    # Hapus enemy yang sudah tidak aktif (mati / sampai base)
    enemies = [e for e in enemies if e.alive]

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill((0, 0, 0))
    grid.draw(screen, show_grid=True, mousePos=mousePos)

    for enemy in enemies:
        enemy.draw(screen)

    pg.display.flip()

pg.quit()
