import pygame
from turret import ArcherTower, CannonTower
import level_data

# ── Warna ────────────────────────────────────────────────────────────────────
C_PANEL_BG    = (15,  18,  28)
C_PANEL_DARK  = (10,  12,  20)
C_BTN         = (50,  60,  80)
C_BTN_HOVER   = (70,  90, 120)
C_BTN_ACTIVE  = (60, 120,  60)
C_BTN_DISABLED= (40,  40,  40)
C_TEXT        = (220, 220, 220)
C_TEXT_DIM    = (120, 120, 120)
C_GOLD        = (255, 210,  50)
C_HP          = (220,  60,  60)
C_BORDER      = (50,  60,  80)
C_SEP         = (40,  50,  65)
C_SELECTED    = (80, 140,  80)


class HUD:
    """Panel HUD di sisi KANAN layar (lebar HUD_WIDTH px)."""

    def __init__(self, screen_w: int, screen_h: int, hud_width: int = 300):
        self.screen_w  = screen_w
        self.screen_h  = screen_h
        self.hud_width = hud_width
        self.hud_x     = screen_w - hud_width   # x awal panel kanan

        self.font    = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_s  = pygame.font.SysFont("Arial", 14)
        self.font_xs = pygame.font.SysFont("Arial", 12)

        self.selected_turret_type = None

        W  = hud_width
        X  = self.hud_x

        # ── Tombol PAUSE & SPEED ─────────────────────────────────────────────
        self.btn_pause = pygame.Rect(X + 10, 10, (W - 30) // 2, 36)
        self.btn_speed = pygame.Rect(X + 10 + (W - 30) // 2 + 10,
                                     10, (W - 30) // 2, 36)

        # ── Shop buttons (Archer, Cannon) ────────────────────────────────────
        btn_w = (W - 30) // 2
        self.shop_buttons: list[dict] = [
            {
                "rect":        pygame.Rect(X + 10, 200, btn_w, 70),
                "turret_type": ArcherTower,
                "cost":        ArcherTower.cost,
                "label":       "Archer",
                "desc":        ["Cepat, single", "target, murah"],
                "cost_str":    str(ArcherTower.cost),
            },
            {
                "rect":        pygame.Rect(X + 10 + btn_w + 10, 200, btn_w, 70),
                "turret_type": CannonTower,
                "cost":        CannonTower.cost,
                "label":       "Cannon",
                "desc":        ["Lambat, AoE,", "mahal"],
                "cost_str":    str(CannonTower.cost),
            },
        ]

        # ── Tombol UPGRADE ───────────────────────────────────────────────────
        self.btn_upgrade = pygame.Rect(X + 10, 290, W - 20, 36)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, state, speed_ctrl,
        hovered_cell=None, selected_cell=None):
        mouse = pygame.mouse.get_pos()
        X     = self.hud_x
        W     = self.hud_width
        H     = self.screen_h

        # ── Background panel kanan ────────────────────────────────────────────
        pygame.draw.rect(surface, C_PANEL_BG, (X, 0, W, H))
        pygame.draw.line(surface, C_BORDER, (X, 0), (X, H), 2)

        # ── PAUSE / SPEED ─────────────────────────────────────────────────────
        paused    = speed_ctrl.paused
        spd_label = f"x{speed_ctrl.speed:.0f} SPD"
        self._btn(surface, self.btn_pause, "RESUME" if paused else "PAUSE", mouse, active=paused)
        self._btn(surface, self.btn_speed, spd_label, mouse)

        self._sep(surface, X, W, 56)

        # ── STATS: Lives / Gold / Wave ────────────────────────────────────────
        self._label(surface, "LIVES",   X + 10,  68, C_TEXT_DIM)
        self._label(surface, f"{state.lives}",
                    X + 10, 84, C_HP, self.font)

        self._label(surface, "GOLD",    X + W//2, 68, C_TEXT_DIM)
        self._label(surface, f"{state.gold}g",
                    X + W//2, 84, C_GOLD, self.font)

        self._label(surface, f"Wave  {state.wave}",
                    X + 10, 112, C_TEXT, self.font_s)

        self._sep(surface, X, W, 134)

        # ── SHOP ──────────────────────────────────────────────────────────────
        self._label(surface, "SHOP", X + 10, 146, C_TEXT_DIM)

        for btn in self.shop_buttons:
            affordable = state.gold >= btn["cost"]
            selected   = (self.selected_turret_type is btn["turret_type"])
            self._shop_btn(surface, btn, mouse, affordable, selected)

        # ── UPGRADE ───────────────────────────────────────────────────────────
        can_upg = state.can_upgrade_turret(selected_cell)
        self._btn(surface, self.btn_upgrade, "UPGRADE", mouse, disabled=not can_upg, active=False)

        # Tooltip level turret yang dipilih
        if selected_cell and selected_cell.is_occupied():
            t = state.get_turret_at(selected_cell)
            if t:
                lv = f"Lv.{t.level}/{level_data.MAX_LEVEL}  |  dmg:{t.damage}  rng:{int(t.range)}"
                self._label(surface, lv, X + 10, 332, C_TEXT_DIM, self.font_xs)
                
                cost = state.get_upgrade_cost(type(t).__name__, t.level)
                if cost:
                    c_col = C_GOLD if state.gold >= cost else C_HP
                    self._label(surface, f"Cost: {cost}g", X + W - 80, 332, c_col, self.font_xs)

        self._sep(surface, X, W, 350)

        # ── INFO cell yang dihover ────────────────────────────────────────────
        self._label(surface, "CELL INFO", X + 10, 360, C_TEXT_DIM)
        if hovered_cell:
            tile = ("Spawn" if hovered_cell._tileType == 2 else
                    "Base"  if hovered_cell._tileType == 3 else
                    "Path"  if hovered_cell._tileType == 1 else "Empty")
            occ  = " [Turret]" if hovered_cell.is_occupied() else ""
            self._label(surface, f"({hovered_cell.col},{hovered_cell.row}) {tile}{occ}",
                        X + 10, 376, C_TEXT, self.font_xs)

        self._sep(surface, X, W, 396)

        # ── Enemy count ───────────────────────────────────────────────────────
        self._label(surface, f"Enemies : {len(state.enemies)}",
                    X + 10, 406, C_TEXT, self.font_xs)
        self._label(surface, f"Turrets : {len(state.turrets)}",
                    X + 10, 422, C_TEXT, self.font_xs)

    # ── Handle Click ──────────────────────────────────────────────────────────

    def handle_click(self, pos: tuple[int, int], state, speed_ctrl, grid) -> str | None:
        # Abaikan klik di luar panel kanan
        if pos[0] < self.hud_x:
            # Klik di area grid — place turret jika ada yang dipilih
            if self.selected_turret_type and grid:
                cell = grid.cell_at_pos(*pos)
                if cell:
                    if state.buy_and_place_turret(self.selected_turret_type, cell):
                        self.selected_turret_type = None
                        return "placed"
            return None

        # ── Klik di panel kanan ───────────────────────────────────────────────
        if self.btn_pause.collidepoint(pos):
            speed_ctrl.toggle_pause()
            return "paused"

        if self.btn_speed.collidepoint(pos):
            speed_ctrl.cycle_speed()
            return "speed"

        for btn in self.shop_buttons:
            if btn["rect"].collidepoint(pos):
                if state.gold >= btn["cost"]:
                    self.selected_turret_type = (
                        None if self.selected_turret_type is btn["turret_type"]
                        else btn["turret_type"]
                    )
                return None

        if self.btn_upgrade.collidepoint(pos):
            sel = getattr(state, "selected_cell", None)
            if sel:
                if state.upgrade_turret(sel):
                    return "upgraded"
            return None

        return None

    # ── Private helpers ───────────────────────────────────────────────────────

    def _label(self, surface, text, x, y, color=C_TEXT, font=None):
        f    = font or self.font_s
        surf = f.render(str(text), True, color)
        surface.blit(surf, (x, y))

    def _sep(self, surface, x, w, y):
        pygame.draw.line(surface, C_SEP, (x + 8, y), (x + w - 8, y), 1)

    def _btn(self, surface, rect, label, mouse, active=False, disabled=False):
        if disabled:
            col = C_BTN_DISABLED
        elif active:
            col = C_BTN_ACTIVE
        elif rect.collidepoint(mouse):
            col = C_BTN_HOVER
        else:
            col = C_BTN
        pygame.draw.rect(surface, col, rect, border_radius=6)
        pygame.draw.rect(surface, C_BORDER, rect, 1, border_radius=6)
        txt_col = C_TEXT_DIM if disabled else C_TEXT
        t = self.font_s.render(label, True, txt_col)
        surface.blit(t, (rect.centerx - t.get_width()  // 2,
                         rect.centery - t.get_height() // 2))

    def _shop_btn(self, surface, btn, mouse, affordable, selected):
        rect = btn["rect"]
        if selected:
            col = C_SELECTED
        elif not affordable:
            col = C_BTN_DISABLED
        elif rect.collidepoint(mouse):
            col = C_BTN_HOVER
        else:
            col = C_BTN

        pygame.draw.rect(surface, col, rect, border_radius=6)
        border_col = C_GOLD if selected else C_BORDER

        pygame.draw.rect(surface, border_col, rect, 2 if selected else 1, border_radius=6)
        tc = C_TEXT if affordable else C_TEXT_DIM

        self._label(surface, btn["label"], rect.x + 8, rect.y + 6,  tc, self.font)

        for i, line in enumerate(btn["desc"]):
            self._label(surface, line, rect.x + 8, rect.y + 24 + i * 14, C_TEXT_DIM, self.font_xs)
        gc = C_GOLD if affordable else (130, 90, 30)

        self._label(surface, btn["cost_str"],
                    rect.x + 8, rect.y + 52, gc, self.font_xs)
