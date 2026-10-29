"""Village map: paths, river, bridge, buildings, trees and collision."""
import random
import pygame
from settings import (
    COLS,
    COLS_NAMED,
    DARK,
    GRASS,
    GRASS2,
    H,
    NODES,
    PATH,
    PATH2,
    ROWS,
    TILE,
    W,
    WHITE,
)
from helpers import darker, draw_clock, draw_flower, draw_shape


def make_tree():
    s = pygame.Surface((32, 48), pygame.SRCALPHA)
    pygame.draw.rect(s, (110, 70, 40), (13, 38, 6, 10))
    for pts, c in (([(16, 2), (7, 16), (25, 16)], (42, 140, 72)),
                   ([(16, 9), (4, 27), (28, 27)], (34, 122, 62)),
                   ([(16, 18), (1, 39), (31, 39)], (28, 106, 54))):
        pygame.draw.polygon(s, c, pts)
        pygame.draw.polygon(s, (16, 70, 38), pts, 2)
    return s


def make_house(wt, ht, wall, roof, barn=False):
    w, h = wt * TILE, ht * TILE
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    rh = int(h * 0.45)
    body = pygame.Rect(6, rh - 4, w - 12, h - rh + 2)
    pygame.draw.rect(s, wall, body)
    pygame.draw.rect(s, DARK, body, 3)
    pts = [(2, rh), (int(w * 0.2), 4), (int(w * 0.8), 4), (w - 2, rh)]
    pygame.draw.polygon(s, roof, pts)
    pygame.draw.polygon(s, DARK, pts, 3)
    for i in range(1, 4):
        y = 4 + i * (rh - 4) // 4
        pygame.draw.line(s, darker(roof, 40), (6 + i * 2, y), (w - 6 - i * 2, y), 2)
    door = pygame.Rect(w // 2 - 11, h - 34, 22, 32)
    pygame.draw.rect(s, (150, 90, 50), door)
    pygame.draw.rect(s, DARK, door, 3)
    if barn:
        pygame.draw.line(s, WHITE, door.topleft, door.bottomright, 3)
        pygame.draw.line(s, WHITE, door.topright, door.bottomleft, 3)
    else:
        for x in (14, w - 14 - 14):
            wr = pygame.Rect(x, h - 48, 14, 14)
            pygame.draw.rect(s, (170, 220, 245), wr)
            pygame.draw.rect(s, DARK, wr, 2)
    return s


def make_clock_tower():
    w, h = 64, 128
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    body = pygame.Rect(8, 36, w - 16, h - 36)
    pygame.draw.rect(s, (200, 195, 190), body)
    pygame.draw.rect(s, DARK, body, 3)
    for y in range(44, h, 14):
        pygame.draw.line(s, (170, 165, 160), (8, y), (w - 8, y), 2)
    pygame.draw.polygon(s, (214, 70, 60), [(2, 36), (w // 2, 0), (w - 2, 36)])
    pygame.draw.polygon(s, DARK, [(2, 36), (w // 2, 0), (w - 2, 36)], 3)
    draw_clock(s, w // 2, 62, 20, 10, 10)
    pygame.draw.rect(s, (150, 90, 50), (w // 2 - 9, h - 28, 18, 28))
    pygame.draw.rect(s, DARK, (w // 2 - 9, h - 28, 18, 28), 3)
    return s


def make_castle():
    w, h = 96, 96
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    stone, line = (190, 190, 205), (140, 140, 160)

    def tower(x, top, tw):
        rc = pygame.Rect(x, top, tw, h - top)
        pygame.draw.rect(s, stone, rc)
        pygame.draw.rect(s, DARK, rc, 3)
        for bx in range(x, x + tw - 5, 10):
            pygame.draw.rect(s, stone, (bx, top - 7, 7, 8))
            pygame.draw.rect(s, DARK, (bx, top - 7, 7, 8), 2)
        for y in range(top + 10, h, 12):
            pygame.draw.line(s, line, (x + 2, y), (x + tw - 3, y), 2)

    tower(4, 18, 26)
    tower(w - 30, 18, 26)
    tower(26, 36, 44)
    for fx in (17, w - 17):
        pygame.draw.line(s, DARK, (fx, 2), (fx, 14), 3)
        pygame.draw.polygon(s, (255, 90, 140), [(fx, 2), (fx + 12, 6), (fx, 10)])
    pygame.draw.rect(s, (110, 70, 40), (w // 2 - 11, h - 32, 22, 32), border_top_left_radius=11, border_top_right_radius=11)
    pygame.draw.rect(s, DARK, (w // 2 - 11, h - 32, 22, 32), 3, border_top_left_radius=11, border_top_right_radius=11)
    return s


class World:
    PATH_WAY = [(5, 18), (5, 16), (5, 9), (11, 9), (11, 4), (13, 4), (13, 11), (13, 14), (24, 14), (24, 3), (22, 3)]
    SPUR = [(24, 14), (24, 16)]
    BRIDGE_ROWS = (13, 14, 15)
    RIVER_COLS = (18, 19, 20)

    def __init__(self):
        self.blocked = set()
        self.objs = []  # (ybase, surface, (x, y))
        self.path = set()
        self._carve(self.PATH_WAY)
        self._carve(self.SPUR)
        self.ground = pygame.Surface((W, H))
        self._build()

    # path tiles --------------------------------------------------------
    def _carve(self, way):
        for (x0, y0), (x1, y1) in zip(way, way[1:]):
            if y0 == y1:  # horizontal
                for x in range(min(x0, x1), max(x0, x1) + 1):
                    self.path.update({(x, y0), (x, y0 + 1)})
            else:
                for y in range(min(y0, y1), max(y0, y1) + 1):
                    self.path.update({(x0, y), (x0 + 1, y)})

    @staticmethod
    def node_center(n):
        return ((n["pos"][0] + 1) * TILE, (n["pos"][1] + 1) * TILE)

    def _build(self):
        rnd = random.Random(11)
        g = self.ground
        for ty in range(ROWS):
            for tx in range(COLS):
                pygame.draw.rect(g, GRASS if (tx + ty) % 2 == 0 else GRASS2, (tx * TILE, ty * TILE, TILE, TILE))
        for _ in range(320):
            x, y = rnd.randrange(W - 6), rnd.randrange(H - 6)
            if rnd.random() < 0.6:
                pygame.draw.rect(g, (58, 148, 48), (x, y, 2, 4))
                pygame.draw.rect(g, (58, 148, 48), (x + 4, y + 1, 2, 3))
            else:
                c = rnd.choice([(255, 255, 255), (255, 170, 200), (255, 230, 90), (150, 190, 255)])
                pygame.draw.rect(g, c, (x, y, 3, 3))
                pygame.draw.rect(g, (255, 220, 60), (x + 1, y + 1, 1, 1))
        # dirt path
        for tx, ty in self.path:
            pygame.draw.rect(g, PATH, (tx * TILE, ty * TILE, TILE, TILE))
            for _ in range(4):
                pygame.draw.rect(g, PATH2, (tx * TILE + rnd.randrange(28), ty * TILE + rnd.randrange(28), 3, 2))
            for dx, dy, rx, ry, rw, rh in ((-1, 0, 0, 0, 3, TILE), (1, 0, TILE - 3, 0, 3, TILE),
                                           (0, -1, 0, 0, TILE, 3), (0, 1, 0, TILE - 3, TILE, 3)):
                if (tx + dx, ty + dy) not in self.path:
                    pygame.draw.rect(g, (205, 160, 80), (tx * TILE + rx, ty * TILE + ry, rw, rh))
        # river + bridge
        for ty in range(ROWS):
            for tx in self.RIVER_COLS:
                if ty in self.BRIDGE_ROWS:
                    continue
                pygame.draw.rect(g, (70, 150, 230), (tx * TILE, ty * TILE, TILE, TILE))
                for _ in range(3):
                    wx, wy = tx * TILE + rnd.randrange(24), ty * TILE + rnd.randrange(28)
                    pygame.draw.rect(g, (170, 215, 250), (wx, wy, 8, 2))
                self.blocked.add((tx, ty))
        bx, by = self.RIVER_COLS[0] * TILE, self.BRIDGE_ROWS[0] * TILE
        for i in range(0, 3 * TILE, 8):
            pygame.draw.rect(g, (170, 110, 60) if (i // 8) % 2 == 0 else (150, 96, 52), (bx + i, by, 8, 3 * TILE))
        pygame.draw.rect(g, DARK, (bx, by, 3 * TILE, 5))
        pygame.draw.rect(g, DARK, (bx, by + 3 * TILE - 5, 3 * TILE, 5))
        for px in (bx, bx + 3 * TILE - 8):
            pygame.draw.rect(g, (120, 74, 40), (px, by - 4, 8, 12))
            pygame.draw.rect(g, (120, 74, 40), (px, by + 3 * TILE - 8, 8, 12))
        # pond with stone rim (top-left)
        pond = pygame.Rect(1 * TILE, 2 * TILE, 3 * TILE, 3 * TILE)
        pygame.draw.rect(g, (150, 150, 160), pond.inflate(6, 6), border_radius=8)
        pygame.draw.rect(g, (70, 150, 230), pond.inflate(-10, -10), border_radius=6)
        pygame.draw.rect(g, (170, 215, 250), (pond.x + 16, pond.y + 22, 20, 3))
        pygame.draw.rect(g, (170, 215, 250), (pond.x + 40, pond.y + 52, 24, 3))
        for tx in range(1, 4):
            for ty in range(2, 5):
                self.blocked.add((tx, ty))
        # stepping stones on Shape Road
        sx = 6 * TILE + 16
        for i, (nm, col) in enumerate((("circle", (230, 60, 60)), ("triangle", (250, 200, 40)),
                                       ("square", (60, 110, 230)), ("diamond", (250, 120, 170)))):
            draw_shape(g, nm, col, sx - (i % 2) * 28, 13 * TILE + i * 24 - 30, 9)
        # farm crops
        for r in range(2):
            for c in range(3):
                rc = pygame.Rect((15 + c) * TILE + 2, (11 + r) * TILE + 6, TILE - 4, TILE - 10)
                pygame.draw.rect(g, (120, 80, 50), rc, border_radius=4)
                for k in range(3):
                    pygame.draw.rect(g, (80, 190, 70), (rc.x + 4 + k * 9, rc.y + 5, 4, 8))
        for x in range(15 * TILE, 18 * TILE, 16):
            pygame.draw.rect(g, (160, 110, 60), (x, 10 * TILE + 18, 4, 14))
        pygame.draw.rect(g, (160, 110, 60), (15 * TILE, 10 * TILE + 22, 3 * TILE, 3))
        # flower beds (Pattern Garden)
        beds = pygame.Rect(26 * TILE, 15 * TILE, 3 * TILE, 3 * TILE)
        pygame.draw.rect(g, (120, 80, 50), beds, border_radius=6)
        pygame.draw.rect(g, (80, 50, 30), beds, 3, border_radius=6)
        pat = [COLS_NAMED["red"], COLS_NAMED["yellow"], COLS_NAMED["pink"]]
        for r in range(3):
            for c in range(3):
                draw_flower(g, pat[(r + c) % 3], beds.x + 16 + c * TILE, beds.y + 12 + r * TILE, 8)
        for tx in range(26, 29):
            for ty in range(15, 18):
                self.blocked.add((tx, ty))

        reserved = set()
        for (tx, ty) in self.path:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    reserved.add((tx + dx, ty + dy))

        def add_obj(surf, tx, ty, block_rows, wt):
            self.objs.append(((ty + surf.get_height() // TILE) * TILE, surf, (tx * TILE, ty * TILE)))
            ht = surf.get_height() // TILE
            for r in range(ht - block_rows, ht):
                for c in range(wt):
                    self.blocked.add((tx + c, ty + r))
            for r in range(-1, ht + 1):
                for c in range(-1, wt + 1):
                    reserved.add((tx + c, ty + r))

        add_obj(make_house(3, 3, (245, 235, 205), (205, 70, 45)), 7, 6, 2, 3)      # Grandma's house
        add_obj(make_house(3, 3, (200, 70, 60), (120, 40, 40), barn=True), 15, 7, 2, 3)  # barn
        add_obj(make_clock_tower(), 27, 5, 3, 2)
        add_obj(make_castle(), 21, 0, 2, 3)
        for tx in range(15, 18):
            for ty in (10, 11, 12):
                reserved.add((tx, ty))
        for tx in range(0, 5):
            for ty in range(1, 6):
                reserved.add((tx, ty))
        for tx in range(17, 22):
            for ty in range(ROWS):
                reserved.add((tx, ty))
        for tx in range(25, 30):
            for ty in range(14, 19):
                reserved.add((tx, ty))
        for n in NODES:
            cx, cy = n["pos"]
            for dx in range(-2, 4):
                for dy in range(-2, 4):
                    reserved.add((cx + dx, cy + dy))

        tree = make_tree()

        def put_tree(tx, ty):
            self.blocked.add((tx, ty))
            self.objs.append((ty * TILE + TILE, tree, (tx * TILE, ty * TILE - 16)))

        for tx in range(COLS):
            for ty in range(ROWS):
                border = tx in (0, COLS - 1) or ty in (0, ROWS - 1)
                if border:
                    if 21 <= tx <= 23 and ty == 0:
                        self.blocked.add((tx, ty))
                        continue
                    put_tree(tx, ty)
                    continue
                if (tx, ty) in reserved or (tx, ty) in self.blocked:
                    continue
                forest = (7 <= tx <= 10 or 15 <= tx <= 17) and 1 <= ty <= 6
                if rnd.random() < (0.45 if forest else 0.06):
                    put_tree(tx, ty)
        self.objs.sort(key=lambda o: o[0])

    # collision ---------------------------------------------------------
    def hits(self, rect):
        if rect.left < 0 or rect.top < 0 or rect.right > W or rect.bottom > H:
            return True
        for tx in range(rect.left // TILE, (rect.right - 1) // TILE + 1):
            for ty in range(rect.top // TILE, (rect.bottom - 1) // TILE + 1):
                if (tx, ty) in self.blocked:
                    return True
        return False
