import pygame as pg

class Assets:
    _loaded = False
    TILES = []  
    
    TILE_STRAIGHT_H = None
    TILE_STRAIGHT_V = None

    TILE_CORNER_LD = None
    TILE_CORNER_LU = None
    TILE_CORNER_RD = None
    TILE_CORNER_RU = None

    TILE_T_NO_R = None
    TILE_T_NO_D = None
    TILE_T_NO_L = None
    TILE_T_NO_U = None

    TILE_CROSS = None
    TILE_EMPTY = None

    @classmethod
    def load(cls):
        if cls._loaded:
            return
        cls._loaded = True

        # ========== Sprites ==========
        cls.PATH = pg.image.load("assets/img/Tiles.png")
        
        # Memotong tileset menjadi tile satuan berukuran 48x48
        cls.TILES = cls.slice_spritesheet(cls.PATH, 48, 48)

        # --- Kategorisasi ---
        cls.TILE_STRAIGHT_H = cls.TILES[0]  # straight horizontal
        cls.TILE_STRAIGHT_V = cls.TILES[1]  # straight vertical

        cls.TILE_CORNER_LD  = cls.TILES[4]  # L = Left, D = Down, U = Up, R = Right
        cls.TILE_CORNER_LU  = cls.TILES[5]
        cls.TILE_CORNER_RU  = cls.TILES[6]
        cls.TILE_CORNER_RD  = cls.TILES[7]

        cls.TILE_T_NO_R     = cls.TILES[8]
        cls.TILE_T_NO_D     = cls.TILES[9]
        cls.TILE_T_NO_L     = cls.TILES[10]
        cls.TILE_T_NO_U     = cls.TILES[11]

        cls.TILE_CROSS      = cls.TILES[12]
        cls.TILE_EMPTY      = cls.TILES[16]

    @classmethod
    def slice_spritesheet(cls, sheet: pg.Surface, tile_width: int, tile_height: int) -> list[pg.Surface]:
        tiles = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        
       
        for y in range(0, sheet_height, tile_height):
            for x in range(0, sheet_width, tile_width):
                rect = pg.Rect(x, y, tile_width, tile_height)
              
                image = pg.Surface((tile_width, tile_height))
                image.blit(sheet, (0, 0), rect)
                tiles.append(image)
                
        return tiles
    
