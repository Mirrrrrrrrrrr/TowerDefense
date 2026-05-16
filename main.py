import pygame as pg
from map import Grid

pg.init()

COLS, ROWS, CELL = 16, 16, 48
HUD_WIDTH = 300 
screen = pg.display.set_mode((COLS * CELL + HUD_WIDTH, ROWS * CELL))
grid = Grid(cols = COLS, rows = ROWS, cellSize = CELL, offset_x = HUD_WIDTH)
clock  = pg.time.Clock()
font   = pg.font.SysFont("monospace", 14)

running = True
while running:
    mousePos = pg.mouse.get_pos()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            running = False

    grid.draw(screen, show_grid = True, mousePos = mousePos)

    pg.display.flip()


pg.quit()
