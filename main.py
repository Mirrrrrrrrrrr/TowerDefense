import pygame as pg
from assets import Assets
from map import Grid
from enemy import NormalEnemy, FastEnemy, TankEnemy
from turret import ArcherTower, CannonTower
from game_manager import GameManager, gameSpeedCtrl, GameSettings
from hud import HUD
from main_menu import MainMenu
from wave_manager import WaveManager

pg.init()
Assets.load()
Assets.play_music("bgm")

COLS, ROWS, CELL = 16, 16, 48
HUD_WIDTH = 300
screen = pg.display.set_mode((COLS * CELL + HUD_WIDTH, ROWS * CELL))
pg.display.set_caption("Tower Defense")

menu = MainMenu(screen)
game_state = "MENU"

grid = Grid(cols = COLS, rows = ROWS, cellSize = CELL, offset_x = 0)
clock = pg.time.Clock()
font  = pg.font.SysFont("monospace", 14)

# ── Variabel Global Game ─────────────────────────────────────────────────────
grid = None
speed_ctrl = None
hud = None
world_path = None
wave_mgr = None

def reset_game():
    global grid, speed_ctrl, hud, world_path, wave_mgr
    grid = Grid(cols=COLS, rows=ROWS, cellSize=CELL, offset_x=0)
    speed_ctrl = gameSpeedCtrl()
    hud = HUD(COLS * CELL + HUD_WIDTH, ROWS * CELL, HUD_WIDTH)
    world_path = [cell.get_center() for cell in grid.path]
    
    GameManager.lives = 100
    GameManager.gold = 200
    GameManager.wave = 1
    GameManager.turrets = []
    GameManager.enemies = []
    GameManager.projectile = []
    GameManager.selected_cell = None
    
    wave_mgr = WaveManager(world_path)

reset_game()

# ── Game loop ─────────────────────────────────────────────────────────────────
running = True
while running:
    raw_dt = clock.tick() / 1000.0   # delta time dalam detik
    dt = speed_ctrl.getDt(raw_dt)
    mousePos = pg.mouse.get_pos()

    # ── Event ─────────────────────────────────────────────────────────────────
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            if game_state in ("GAME", "VICTORY", "DEFEAT"):
                if game_state in ("VICTORY", "DEFEAT"):
                    Assets.play_music("bgm")
                game_state = "MENU"
            else:
                running = False
                
        if game_state == "MENU":
            result = menu.handle_event(event)
            if result == "start_game":
                reset_game()
                game_state = "GAME"
        elif game_state == "GAME":
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Klik Kiri
                    action = hud.handle_click(mousePos, GameManager, speed_ctrl, grid)
                    if not action and mousePos[0] < hud.hud_x:
                        GameManager.selected_cell = grid.cell_at_pos(*mousePos)
        elif game_state in ("VICTORY", "DEFEAT"):
            if event.type == pg.MOUSEBUTTONDOWN:
                game_state = "MENU"
                Assets.play_music("bgm")

    if game_state == "MENU":
        menu.draw()
        pg.display.flip()
        continue
        
    if game_state == "GAME":
        # ── Wave Manager ───────────────────────────────────────────────────────────
        wave_mgr.update(dt, GameManager.enemies)
        
        # Update teks HUD agar menampilkan progres wave dan cooldown
        if wave_mgr.all_done:
            if game_state != "VICTORY":
                GameManager.wave = "CLEARED"
                game_state = "VICTORY"
                pg.mixer.music.stop()
                Assets.play_sound(Assets.SND_VICTORY)
        elif not wave_mgr.active:
            GameManager.wave = f"{wave_mgr.wave_num} (Next: {wave_mgr.next_wave_in:.0f}s)"
        else:
            GameManager.wave = wave_mgr.wave_num

        # ── Update enemy ──────────────────────────────────────────────────────────
        for enemy in GameManager.enemies:
            enemy.update(dt, world_path)
            if enemy.reached_base:
                GameManager.lives = max(0, GameManager.lives - enemy.damage_to_base)
                Assets.play_sound(Assets.SND_MASUKBASE)
            elif not enemy.alive:
                GameManager.gold += enemy.reward

        if GameManager.lives <= 0:
            game_state = "DEFEAT"
            pg.mixer.music.stop()

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
    grid.draw(screen, show_grid=GameSettings.SHOW_GRID, mousePos=mousePos if is_hovering_grid else None)

    for enemy in GameManager.enemies:
        enemy.draw(screen)

    for turret in GameManager.turrets:
        is_hovered = (turret.cell is hovered_cell) or (turret.cell is GameManager.selected_cell)
        turret.draw(screen, hovered=is_hovered)

    for proj in GameManager.projectile:
        proj.draw(screen)

    hud.draw(screen, GameManager, speed_ctrl, hovered_cell, GameManager.selected_cell)

    if game_state == "VICTORY":
        overlay = pg.Surface((screen.get_width(), screen.get_height()), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        font_v = pg.font.SysFont("Arial", 64, bold=True)
        text_v = font_v.render("V I C T O R Y !", True, (255, 215, 0))
        screen.blit(text_v, (screen.get_width()//2 - text_v.get_width()//2, screen.get_height()//2 - 50))
        
        font_s = pg.font.SysFont("Arial", 24)
        text_s = font_s.render("Click anywhere to return to Menu", True, (255, 255, 255))
        screen.blit(text_s, (screen.get_width()//2 - text_s.get_width()//2, screen.get_height()//2 + 30))
    elif game_state == "DEFEAT":
        overlay = pg.Surface((screen.get_width(), screen.get_height()), pg.SRCALPHA)
        overlay.fill((50, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        font_d = pg.font.SysFont("Arial", 64, bold=True)
        text_d = font_d.render("G A M E  O V E R", True, (255, 50, 50))
        screen.blit(text_d, (screen.get_width()//2 - text_d.get_width()//2, screen.get_height()//2 - 50))
        
        font_s = pg.font.SysFont("Arial", 24)
        text_s = font_s.render("Click anywhere to return to Menu", True, (255, 255, 255))
        screen.blit(text_s, (screen.get_width()//2 - text_s.get_width()//2, screen.get_height()//2 + 30))

    pg.display.flip()

pg.quit()
