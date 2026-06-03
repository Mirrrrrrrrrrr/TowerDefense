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
    
    SND_SHOOT_ARCHER = None
    SND_SHOOT_CANNON = None
    SND_HIT = None
    SND_BUY = None
    SND_DEATH_F = None
    SND_DEATH_N = None
    SND_DEATH_T = None
    SND_MASUKBASE = None
    SND_TEROMPET = None
    SND_UPGRADE = None
    SND_VICTORY = None

    @classmethod
    def _load_sound(cls, path: str, vol: float = 0.5):
        try:
            snd = pg.mixer.Sound(path)
            snd.set_volume(vol)
            return snd
        except Exception:
            return None

    @classmethod
    def load(cls, initial_music_track: str = "bgm"):
        if cls._loaded:
            return
        cls._loaded = True
        
        # ========== Sounds & Music ==========
        if not pg.mixer.get_init():
            pg.mixer.init()
            
        cls.SND_SHOOT_ARCHER = cls._load_sound("assets/sound/arrow.mp3")
        cls.SND_SHOOT_CANNON = cls._load_sound("assets/sound/cannonsound.mp3")
        cls.SND_HIT          = cls._load_sound("assets/sound/hit.wav")
        cls.SND_BUY          = cls._load_sound("assets/sound/buy.mp3")
        cls.SND_DEATH_F      = cls._load_sound("assets/sound/deathFEnemy.wav")
        cls.SND_DEATH_N      = cls._load_sound("assets/sound/deathNEnemy.wav")
        cls.SND_DEATH_T      = cls._load_sound("assets/sound/deathTEnemy.wav")
        cls.SND_MASUKBASE    = cls._load_sound("assets/sound/masukbase.mp3")
        cls.SND_TEROMPET     = cls._load_sound("assets/sound/terompetwave.mp3", vol=0.2)
        cls.SND_UPGRADE      = cls._load_sound("assets/sound/upgrade.wav")
        cls.SND_VICTORY      = cls._load_sound("assets/sound/victory.mp3", vol=0.7)

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
    def play_sound(cls, sound):
        from game_manager import GameSettings
        if GameSettings.SOUND_ON and sound is not None:
            try:
                sound.play()
            except Exception:
                pass

    @classmethod
    def play_music(cls, track="bgm"):
        if not pg.mixer.get_init():
            return
        try:
            pg.mixer.music.load("assets/sound/bgm.mp3")
            pg.mixer.music.play(-1)
            pg.mixer.music.set_volume(0.2)
            from game_manager import GameSettings
            if not GameSettings.MUSIC_ON:
                pg.mixer.music.pause()
        except Exception:
            pass

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
