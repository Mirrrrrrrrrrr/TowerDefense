import pygame as pg
import sys

pg.init()

C_BG        = (10,  22,  40)
C_GRID      = (255, 255, 255, 8)
C_TITLE     = (232, 216, 122)
C_SUBTITLE  = (90, 122, 154)
C_BTN_BG    = (13,  31,  56)
C_BTN_BDR   = (30,  58,  95)
C_BTN_HOV   = (20,  45,  77)
C_BTN_HOV_BDR = (232, 216, 122)
C_TEXT      = (168, 196, 224)
C_TEXT_HOV  = (232, 216, 122)
C_DIM       = (58,  90, 122)

MEMBERS = ["Arya", "Mirza", "Galang", "Reynaldi"]
LEVELS  = ["Forest", "Desert", "Tundra", "Volcano", "Abyss"]


def draw_text_centered(surface, text, font, color, cx, y):
    t = font.render(text, True, color)
    surface.blit(t, (cx - t.get_width() // 2, y))
    return t.get_height()


def draw_button(surface, rect, label, font, hovered):
    bg  = C_BTN_HOV   if hovered else C_BTN_BG
    bdr = C_BTN_HOV_BDR if hovered else C_BTN_BDR
    tc  = C_TEXT_HOV  if hovered else C_TEXT
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

        self.font_title  = pg.font.SysFont("monospace", 34, bold=True)
        self.font_sub    = pg.font.SysFont("monospace", 11)
        self.font_btn    = pg.font.SysFont("monospace", 13)
        self.font_label  = pg.font.SysFont("monospace", 11)

        # state: "home" | "levels" | "settings" | "credits"
        self.state = "home"

        # Tombol home
        bw, bh, gap = 240, 44, 10
        bx = self.cx - bw // 2
        by = self.h // 2 - 20
        self.home_btns = [
            {"label": "PLAY",     "rect": pg.Rect(bx, by,             bw, bh), "action": "levels"},
            {"label": "SETTINGS", "rect": pg.Rect(bx, by + bh + gap,  bw, bh), "action": "settings"},
            {"label": "CREDITS",  "rect": pg.Rect(bx, by + (bh+gap)*2, bw, bh), "action": "credits"},
        ]

        # Level buttons (3×2 grid)
        lw, lh = 88, 72
        lgap = 8
        cols = 3
        total_w = cols * lw + (cols - 1) * lgap
        lx0 = self.cx - total_w // 2
        ly0 = self.h // 2 - 90
        self.level_btns = []
        for i, name in enumerate(LEVELS):
            c, r = i % cols, i // cols
            rect = pg.Rect(lx0 + c * (lw + lgap), ly0 + r * (lh + lgap), lw, lh)
            self.level_btns.append({"label": name, "num": i + 1, "rect": rect})

        # Back button
        self.back_btn = pg.Rect(self.cx - 60, self.h - 80, 120, 36)

    def handle_event(self, event) -> str | None:
        """Return 'level_N' saat level dipilih, None otherwise."""
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return None
        pos = event.pos

        if self.state == "home":
            for btn in self.home_btns:
                if btn["rect"].collidepoint(pos):
                    self.state = btn["action"]

        elif self.state == "levels":
            for btn in self.level_btns:
                if btn["rect"].collidepoint(pos):
                    return f"level_{btn['num']}"
            if self.back_btn.collidepoint(pos):
                self.state = "home"

        elif self.state in ("settings", "credits"):
            if self.back_btn.collidepoint(pos):
                self.state = "home"

        return None

    def draw(self):
        self.screen.fill(C_BG)
        draw_grid(self.screen, self.w, self.h)
        mouse = pg.mouse.get_pos()

        if self.state == "home":
            self._draw_home(mouse)
        elif self.state == "levels":
            self._draw_levels(mouse)
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

    # ── levels ────────────────────────────────────────────────────────────────

    def _draw_levels(self, mouse):
        draw_text_centered(self.screen, "S E L E C T  L E V E L",
                           self.font_sub, C_SUBTITLE, self.cx, self.h // 2 - 120)
        for btn in self.level_btns:
            hov = btn["rect"].collidepoint(mouse)
            bg  = C_BTN_HOV   if hov else C_BTN_BG
            bdr = C_BTN_HOV_BDR if hov else C_BTN_BDR
            tc  = C_TEXT_HOV  if hov else C_TEXT
            pg.draw.rect(self.screen, bg,  btn["rect"], border_radius=4)
            pg.draw.rect(self.screen, bdr, btn["rect"], 1, border_radius=4)
            # nomor level
            num_t = self.font_btn.render(f"{btn['num']:02d}", True, tc)
            self.screen.blit(num_t, num_t.get_rect(
                centerx=btn["rect"].centerx,
                y=btn["rect"].y + 14))
            # nama level
            name_t = self.font_label.render(btn["label"].upper(), True,
                                            C_DIM if not hov else (160, 136, 64))
            self.screen.blit(name_t, name_t.get_rect(
                centerx=btn["rect"].centerx,
                y=btn["rect"].y + 38))
        self._draw_back(mouse)

    # ── settings ─────────────────────────────────────────────────────────────

    def _draw_settings(self, mouse):
        draw_text_centered(self.screen, "S E T T I N G S",
                           self.font_sub, C_SUBTITLE, self.cx, self.h // 2 - 120)
        rows = [("SOUND", "ON"), ("MUSIC", "ON"), ("SHOW GRID", "ON"), ("FPS LIMIT", "60")]
        rw, rh = 280, 40
        ry = self.h // 2 - 80
        for label, val in rows:
            rect = pg.Rect(self.cx - rw // 2, ry, rw, rh)
            pg.draw.rect(self.screen, C_BTN_BG,  rect, border_radius=4)
            pg.draw.rect(self.screen, C_BTN_BDR, rect, 1, border_radius=4)
            lbl = self.font_label.render(label, True, C_TEXT)
            val_t = self.font_label.render(val, True, C_TITLE)
            self.screen.blit(lbl, (rect.x + 14, rect.centery - lbl.get_height() // 2))
            self.screen.blit(val_t, (rect.right - val_t.get_width() - 14,
                                     rect.centery - val_t.get_height() // 2))
            ry += rh + 8
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
        t = self.font_label.render("< BACK", True,
                                   C_TEXT_HOV if hov else C_DIM)
        self.screen.blit(t, t.get_rect(center=self.back_btn.center))


# ── standalone run ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    screen = pg.display.set_mode((1068, 768))
    pg.display.set_caption("Tower Defense")
    clock  = pg.time.Clock()
    menu   = MainMenu(screen)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            result = menu.handle_event(event)
            if result:
                print(f"Selected: {result}")  # ganti dengan load level

        menu.draw()
        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()