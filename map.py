import pygame as pg                 # untuk deklarasi pygame gunakan pg 
from dataclasses import dataclass   # baca dataclass.note untuk info lebih lanjut

pg.init()

TILE_EMPTY = 0
TILE_PATH = 1
TILE_SPAWN = 2
TILE_BASE = 3

COLOR_EMPTY = (34,  85,  34)   # hijau gelap
COLOR_PATH  = (160, 130,  80)  # coklat pasir
COLOR_SPAWN = ( 50, 150, 220)  # biru
COLOR_BASE  = (220,  60,  60)  # merah
COLOR_GRID  = ( 20,  60,  20)  # garis grid
COLOR_HOVER = (255, 255, 100)  # highlight hover
COLOR_BLOCKED = (80, 40, 40)   # cell terisi turret



@dataclass
class Cell():
    col: int
    row: int
    tileType: int = TILE_EMPTY
    isOccupied: bool = False
    _cellSize: int = 48
    _offset_x: int = 0
    _offset_y: int = 0

    def get_rect(self) -> pg.Rect:          
        x = self.col * self._cellSize # x = self._offset_x + self.col * self._cellSize untuk HUD kiri
        y = self.row * self._cellSize
        return pg.Rect(x, y, self._cellSize, self._cellSize)

    def get_center(self) -> tuple[float, float]:
        r = self.get_rect() 
        return (r.centerx, r.centery) 

    @property
    def can_place_turret(self) -> bool:
        return self.tileType == TILE_EMPTY and not self.isOccupied

    def draw(self, surface: pg.Surface,
            show_grid: bool = True,
            hovered: bool = False):
        rect = self.get_rect()

        if self.tileType == TILE_SPAWN:
            color = COLOR_SPAWN
        elif self.tileType == TILE_BASE:
            color = COLOR_BASE
        elif self.tileType == TILE_PATH:
            color = COLOR_PATH
        elif self.isOccupied:
            color = COLOR_BLOCKED
        elif self.isOccupied:
            color = COLOR_ROCKY
        else:
            color = COLOR_EMPTY

        pg.draw.rect(surface, color, rect)

        # hover highlight 
        if hovered and self.can_place_turret:
            highlight = pg.Surface(rect.size, pg.SRCALPHA)
            highlight.fill((255, 255, 100, 80))
            surface.blit(highlight, rect.topleft)

        # garis grid
        if show_grid:
            pg.draw.rect(surface, COLOR_GRID, rect, 1)



class Grid:
    def __init__(
        self,
        cols = 20,
        rows = 10,
        cellSize = 48,
        offset_x = 0,
        offset_y = 0,
        waypoints: list[tuple[int, int]] = None,
    ):
        self.cols = cols
        self.rows = rows
        self.cellSize = cellSize
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.cells: list[list[Cell]] = [
            [
                Cell(row = r, col = c, 
                _cellSize = cellSize, 
                _offset_x = offset_x, 
                _offset_y = offset_y)
                for c in range(cols)
            ]
            for r in range(rows)
        ]
        
        
        self.waypoints: list[tuple[int, int]] = ( 
            waypoints if waypoints != None
            else self._defaultWaypoints()
        ) # titik-titik tujuan

        self.rockyTiles: list[tuple[int, int]] = [
            (0, 0),
        ]
        self.path: list[Cell] = []
        self.world_path: list[tuple[float, float]] = []
        
        # panggil fungsi _build_path saat Grid dibuat
        self._build_path()

    def _defaultWaypoints(self) -> list[tuple[int, int]]:
        return[
            (0, 3),
            (4, 3),
            (4, 7),
            (1, 7),
            (1, 13),
            (8, 13),
            (8, 10),
            (12, 10),
            (12, 13),
            (8, 13),
            (8, 4),
            (11, 4),
            (11, 1),
            (15, 1),
        ]
    
    # untuk memetakan waypoints dan cells diantaranya pada path
    def _build_path(self):
        self.path = []
        visited: set[tuple[int, int]] = set() # untuk mencatat path yg sudah diproses

        for i, (c1, r1) in enumerate(self.waypoints): # memetakan waypoints
            is_last = (i == len(self.waypoints) - 1)
            if i < len(self.waypoints) - 1:
                c2, r2 = self.waypoints[i + 1]
            else:
                c2, r2 = c1, r1

            segment = self._segment_cells(c1, r1, c2, r2, include_end = is_last) # memetakan cells antar waypoints
            for (c, r) in segment:
                if (c, r) not in visited:
                    visited.add((c, r))
                    cell = self.cells[r][c]

                    if (c,r) == (self.waypoints[0][0], self.waypoints[0][1]):
                        cell.tileType = TILE_SPAWN
                    elif (c, r) == (self.waypoints[-1][0], self.waypoints[-1][1]):
                        cell.tileType = TILE_BASE
                    else:
                        cell.tileType = TILE_PATH
                    self.path.append(cell)

    def _segment_cells(
        self,
        c1: int, r1: int,
        c2: int, r2: int,
        include_end: bool = False
    ) -> list[tuple[int, int]]:
        segment_coordinates = [] 

        step_c = 1 if c2 > c1 else -1
        for c in range(c1, c2, step_c): 
            segment_coordinates.append((c, r1))

        step_r = 1 if r2 > r1 else -1
        for r in range(r1, r2, step_r):
            segment_coordinates.append((c2, r))       

        if include_end:
            segment_coordinates.append((c2, r2))

        return segment_coordinates 

    # ── akses cell ───────────────────────────────────────────────────────────
    def get_cell(self, row: int, col: int) -> Cell:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return None

    def cell_at_pos(self, px: int, py: int) -> Cell:
        col = px // self.cellSize
        row = py // self.cellSize
        return self.get_cell(row, col)

    # ── draw ─────────────────────────────────────────────────────────────────
    def draw(self, surface: pg.Surface,
            show_grid: bool = True,
            mousePos: tuple[int, int] = None):

        hovered_cell = (
            self.cell_at_pos(*mousePos) if mousePos else None
        )

        for row in self.cells:
            for cell in row:
                hovered = (cell is hovered_cell)
                cell.draw(surface, show_grid = show_grid, hovered = hovered)





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
