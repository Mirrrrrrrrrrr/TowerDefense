import pygame as pg                 # untuk deklarasi pygame gunakan pg 
from assets import Assets

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


class Cell():
    def __init__(self, col: int, row: int, tileType: int = TILE_EMPTY, 
                 isOccupied: bool = False, _cellSize: int = 48, 
                 _offset_x: int = 0, _offset_y: int = 0):
        self.col = col
        self.row = row
        self.tileType = tileType
        self.isOccupied = isOccupied
        self._cellSize = _cellSize
        self._offset_x = _offset_x
        self._offset_y = _offset_y
        self.image = None

    def get_rect(self) -> pg.Rect:          
        x = self.col * self._cellSize # x = self._offset_x + self.col * self._cellSize untuk HUD kiri
        y = self.row * self._cellSize
        return pg.Rect(x, y, self._cellSize, self._cellSize)

    def get_center(self) -> tuple[float, float]:
        r = self.get_rect() 
        return (r.centerx, r.centery) 

    def is_path(self) -> bool:
        return self.tileType in (TILE_PATH, TILE_SPAWN, TILE_BASE)

    def can_place_turret(self) -> bool:
        return self.tileType == TILE_EMPTY and not self.isOccupied

    def draw(self, surface: pg.Surface,
            show_grid: bool = True,
            hovered: bool = False):
        rect = self.get_rect()

        if self.tileType == TILE_EMPTY:
            if Assets.TILE_EMPTY:
                surface.blit(Assets.TILE_EMPTY, rect)
            else:
                pg.draw.rect(surface, COLOR_EMPTY, rect)

        elif self.is_path():
            if self.image:
                surface.blit(self.image, rect.topleft)
             # Fallback warna jika gambar gagal dimuat
            else: 
                if self.tileType == TILE_SPAWN:
                    color = COLOR_SPAWN 
                elif self.tileType == TILE_BASE:
                    color = COLOR_BASE
                else: 
                    color = COLOR_PATH
                pg.draw.rect(surface, color, rect)

        # hover highlight 
        if hovered and self.can_place_turret():
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

        for i, (c1, r1) in enumerate(self.waypoints): # memetakan waypoints
            is_last = (i == len(self.waypoints) - 1)
            if i < len(self.waypoints) - 1:
                c2, r2 = self.waypoints[i + 1]
            else:
                c2, r2 = c1, r1

            segment = self._segment_cells(c1, r1, c2, r2, include_end = is_last) # memetakan cells antar waypoints
            for (c, r) in segment:
                if (c, r):
                    cell = self.cells[r][c]

                    if (c,r) == self.waypoints[0]:
                        cell.tileType = TILE_SPAWN
                    elif (c, r) == self.waypoints[-1]:
                        cell.tileType = TILE_BASE
                    else:
                        cell.tileType = TILE_PATH
                    self.path.append(cell)
                    
        self._update_path_image()

    def _update_path_image(self):
        # Nilai tetangga: Atas=1, Kanan=2, Bawah=4, Kiri=8
        BITMASK_MAP = {
            1: Assets.TILE_STRAIGHT_V,    2: Assets.TILE_STRAIGHT_H,
            4: Assets.TILE_STRAIGHT_V,    8: Assets.TILE_STRAIGHT_H,
            5: Assets.TILE_STRAIGHT_V,    10: Assets.TILE_STRAIGHT_H,
            3: Assets.TILE_CORNER_RU,     6: Assets.TILE_CORNER_RD,
            9: Assets.TILE_CORNER_LU,     12: Assets.TILE_CORNER_LD,
            13: Assets.TILE_T_NO_R,       11: Assets.TILE_T_NO_D,
            7: Assets.TILE_T_NO_L,        14: Assets.TILE_T_NO_U,
            15: Assets.TILE_CROSS,
        }

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.cells[row][col]
                if cell.is_path():
                    mask = 0
                    # Cek cell tetangga apakah cell tetangga merupakan jalan 
                    if row > 0 and self.cells[row-1][col].is_path(): mask += 1
                    if col > 0 and self.cells[row][col-1].is_path(): mask += 8
                    if row < self.rows - 1 and self.cells[row+1][col].is_path(): mask += 4
                    if col < self.cols - 1 and self.cells[row][col+1].is_path(): mask += 2

                    cell.image = BITMASK_MAP.get(mask, None)

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

    # ========== akses cell ==========
    def get_cell(self, row: int, col: int) -> Cell:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return None

    def cell_at_pos(self, px: int, py: int) -> Cell:
        col = px // self.cellSize
        row = py // self.cellSize
        return self.get_cell(row, col)

    # ========== draw ==========
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
