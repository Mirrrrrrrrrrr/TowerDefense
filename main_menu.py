import pygame as pg
import sys
from game_manager import GameSettings

pg.init()

C_BG          = (10,  22,  40)
C_GRID        = (255, 255, 255, 8)
C_TITLE       = (232, 216, 122)
C_SUBTITLE    = (90,  122, 154)
C_BTN_BG      = (13,  31,  56)
C_BTN_BDR     = (30,  58,  95)
C_BTN_HOV     = (20,  45,  77)
C_BTN_HOV_BDR = (232, 216, 122)
C_TEXT        = (168, 196, 224)
C_TEXT_HOV    = (232, 216, 122)
C_DIM         = (58,  90, 122)

MEMBERS = ["Arya", "Mirza", "Galang", "Reynaldy"]

def draw_text_centered(surface, text, font, color, cx, y):
    t = font.render(text, True, color)
    surface.blit(t, (cx - t.get_width() // 2, y))
    return t.get_height()


def draw_button(surface, rect, label, font, hovered):
    bg  = C_BTN_HOV     if hovered else C_BTN_BG
    bdr = C_BTN_HOV_BDR if hovered else C_BTN_BDR
    tc  = C_TEXT_HOV    if hovered else C_TEXT
    pg.draw.rect(surface, bg,  rect, border_radius=4)
    pg.draw.rect(surface, bdr, rect, 1, border_radius=4)
    t = font.render(label, True, tc)
    surface.blit(t, t.get_rect(center=rect.center))


def draw_grid(surface, w, h, cell=48):
    grid_surf = pg.Surface((w, h), pg.SRCALPHA)
    for x in range(0, w, cell):
        pg.draw.line(grid_surf, C_GRID, (x, 0), (x, h))
    for y in range(0, h, cell):
        pg.draw.line(grid_surf, C_GRID, (0, y), (w, y))
    surface.blit(grid_surf, (0, 0))


class MainMenu:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.w, self.h = screen.get_size()
        self.cx = self.w // 2

        self.font_title  = pg.font.SysFont("Arial", 34, bold=True)
        self.font_sub    = pg.font.SysFont("Arial", 11)
        self.font_btn    = pg.font.SysFont("Arial", 13)
        self.font_label  = pg.font.SysFont("Arial", 11)

        # state: "home" | "settings" | "credits"
        self.state = "home"

        # Home buttons — PLAY goes straight to ingame (no level select)
        bw, bh, gap = 240, 44, 10
        bx = self.cx - bw // 2
        by = self.h // 2 - 20
        self.home_btns = [
            {"label": "PLAY",     "rect": pg.Rect(bx, by,              bw, bh), "action": "play"},
            {"label": "SETTINGS", "rect": pg.Rect(bx, by + bh + gap,   bw, bh), "action": "settings"},
            {"label": "CREDITS",  "rect": pg.Rect(bx, by + (bh+gap)*2, bw, bh), "action": "credits"},
        ]

        # Back button
        self.back_btn = pg.Rect(self.cx - 60, self.h - 80, 120, 36)

        # Settings buttons
        rw, rh = 280, 40
        ry = self.h // 2 - 80
        self.setting_rects = {
            "sound": pg.Rect(self.cx - rw // 2, ry, rw, rh),
            "music": pg.Rect(self.cx - rw // 2, ry + rh + 8, rw, rh),
            "grid":  pg.Rect(self.cx - rw // 2, ry + (rh + 8)*2, rw, rh),
        }

    def handle_event(self, event) -> str | None:
        """Return 'start_game' when PLAY is clicked, None otherwise."""
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return None
        pos = event.pos

        if self.state == "home":
            for btn in self.home_btns:
                if btn["rect"].collidepoint(pos):
                    if btn["action"] == "play":
                        return "start_game"
                    self.state = btn["action"]

        elif self.state in ("settings", "credits"):
            if self.back_btn.collidepoint(pos):
                self.state = "home"
            elif self.state == "settings":
                if self.setting_rects["sound"].collidepoint(pos):
                    GameSettings.SOUND_ON = not GameSettings.SOUND_ON
                elif self.setting_rects["music"].collidepoint(pos):
                    GameSettings.MUSIC_ON = not GameSettings.MUSIC_ON
                    if GameSettings.MUSIC_ON:
                        pg.mixer.music.unpause()
                    else:
                        pg.mixer.music.pause()
                elif self.setting_rects["grid"].collidepoint(pos):
                    GameSettings.SHOW_GRID = not GameSettings.SHOW_GRID

        return None

    def draw(self):
        self.screen.fill(C_BG)
        if GameSettings.SHOW_GRID:
            draw_grid(self.screen, self.w, self.h)
        mouse = pg.mouse.get_pos()

        if self.state == "home":
            self._draw_home(mouse)
        elif self.state == "settings":
            self._draw_settings(mouse)
        elif self.state == "credits":
            self._draw_credits(mouse)

    # ── home ─────────────────────────────────────────────────────────────────

    def _draw_home(self, mouse):
        draw_text_centered(self.screen, "TOWER DEFENSE",
                           self.font_title, C_TITLE, self.cx, self.h // 2 - 140)
        draw_text_centered(self.screen, "D E F E N D  Y O U R  B A S E",
                           self.font_sub, C_SUBTITLE, self.cx, self.h // 2 - 96)
        for btn in self.home_btns:
            draw_button(self.screen, btn["rect"], btn["label"],
                        self.font_btn, btn["rect"].collidepoint(mouse))

    # ── settings ─────────────────────────────────────────────────────────────

    def _draw_settings(self, mouse):
        draw_text_centered(self.screen, "S E T T I N G S",
                           self.font_sub, C_SUBTITLE, self.cx, self.h // 2 - 120)
        
        rows = [
            ("SOUND", "ON" if GameSettings.SOUND_ON else "OFF", self.setting_rects["sound"]),
            ("MUSIC", "ON" if GameSettings.MUSIC_ON else "OFF", self.setting_rects["music"]),
            ("SHOW GRID", "ON" if GameSettings.SHOW_GRID else "OFF", self.setting_rects["grid"]),
        ]
        
        for label, val, rect in rows:
            pg.draw.rect(self.screen, C_BTN_BG,  rect, border_radius=4)
            pg.draw.rect(self.screen, C_BTN_BDR, rect, 1, border_radius=4)
            lbl   = self.font_label.render(label, True, C_TEXT)
            val_t = self.font_label.render(val,   True, C_TITLE)
            self.screen.blit(lbl,   (rect.x + 14, rect.centery - lbl.get_height() // 2))
            self.screen.blit(val_t, (rect.right - val_t.get_width() - 14,
                                     rect.centery - val_t.get_height() // 2))
        self._draw_back(mouse)

    # ── credits ───────────────────────────────────────────────────────────────

    def _draw_credits(self, mouse):
        draw_text_centered(self.screen, "T E A M",
                           self.font_sub, C_SUBTITLE, self.cx, self.h // 2 - 130)
        cw, ch = 280, 48
        cy = self.h // 2 - 90
        for name in MEMBERS:
            rect = pg.Rect(self.cx - cw // 2, cy, cw, ch)
            pg.draw.rect(self.screen, C_BTN_BG,  rect, border_radius=4)
            pg.draw.rect(self.screen, C_BTN_BDR, rect, 1, border_radius=4)
            # avatar
            av_rect = pg.Rect(rect.x + 12, rect.centery - 14, 28, 28)
            pg.draw.rect(self.screen, (20, 45, 77), av_rect, border_radius=14)
            pg.draw.rect(self.screen, C_BTN_BDR, av_rect, 1, border_radius=14)
            initials = name[:2].upper()
            av_t = self.font_label.render(initials, True, C_TITLE)
            self.screen.blit(av_t, av_t.get_rect(center=av_rect.center))
            # nama
            n_t = self.font_btn.render(name, True, C_TEXT)
            self.screen.blit(n_t, (rect.x + 52, rect.centery - n_t.get_height() // 2))
            # role
            r_t = self.font_label.render("DEVELOPER", True, C_DIM)
            self.screen.blit(r_t, (rect.right - r_t.get_width() - 14,
                                   rect.centery - r_t.get_height() // 2))
            cy += ch + 8
        self._draw_back(mouse)

    # ── back button ───────────────────────────────────────────────────────────

    def _draw_back(self, mouse):
        hov = self.back_btn.collidepoint(mouse)
        pg.draw.rect(self.screen, C_BTN_HOV if hov else (0, 0, 0, 0),
                     self.back_btn, border_radius=4)
        pg.draw.rect(self.screen, C_BTN_BDR, self.back_btn, 1, border_radius=4)
        t = self.font_label.render("< BACK", True, C_TEXT_HOV if hov else C_DIM)
        self.screen.blit(t, t.get_rect(center=self.back_btn.center))


# ── standalone run ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    screen = pg.display.set_mode((1068, 768))
    pg.display.set_caption("Tower Defense")
    clock = pg.time.Clock()
    menu  = MainMenu(screen)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            result = menu.handle_event(event)
            if result:
                print(f"Action: {result}")  

        menu.draw()
        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()
