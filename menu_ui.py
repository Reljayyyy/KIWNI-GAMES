"""Look of the title screen: animated backdrop, outlined text, candy buttons, panels, icons."""
import math
import random

import pygame

from settings import W, H, WHITE, YELLOW, NAVY, CREAM
from helpers import F, fit_text, text, darker, draw_shape, draw_star
from world import make_castle, make_tree

BTN_COLORS = [(76, 175, 80), (66, 133, 244), (255, 152, 0), (171, 71, 188), (229, 57, 53)]
OUTLINE = (52, 30, 64)
_cache = {}


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _lighten(c, n):
    return tuple(min(255, v + n) for v in c)


# ------------------------------------------------------------ outlined text
def outlined_surface(msg, size, col, edge, thick):
    key = (msg, size, col, edge, thick)
    if key in _cache:
        return _cache[key]
    f = F(size)
    base = f.render(msg, True, col)
    shade = f.render(msg, True, edge)
    w, h = base.get_size()
    pad = thick + 2
    surf = pygame.Surface((w + 2 * pad, h + 2 * pad + 4), pygame.SRCALPHA)
    for dx in range(-thick, thick + 1):
        for dy in range(-thick, thick + 1):
            if dx * dx + dy * dy <= thick * thick + 1:
                surf.blit(shade, (pad + dx, pad + dy + 3))
    surf.blit(base, (pad, pad))
    _cache[key] = surf
    return surf


def outlined(s, msg, size, col, edge, pos, anchor="center", thick=3):
    surf = outlined_surface(msg, size, col, edge, thick)
    r = surf.get_rect()
    setattr(r, anchor, pos)
    s.blit(surf, r)
    return r


# ----------------------------------------------------------------- backdrop
def _build_backdrop(top, bottom, sun_pos, sun_col):
    bg = pygame.Surface((W, H))
    for y in range(H):
        pygame.draw.line(bg, _lerp(top, bottom, min(1.0, y / (H * 0.7))), (0, y), (W, y))
    glow = pygame.Surface((300, 300), pygame.SRCALPHA)
    for r in range(150, 0, -10):
        pygame.draw.circle(glow, (sun_col[0], sun_col[1], sun_col[2], int(70 * (1 - r / 150)) + 8), (150, 150), r)
    bg.blit(glow, (sun_pos[0] - 150, sun_pos[1] - 150))
    pygame.draw.circle(bg, sun_col, sun_pos, 46)
    # far hills + castle
    pygame.draw.ellipse(bg, (126, 196, 160), (-260, 340, 900, 420))
    pygame.draw.ellipse(bg, (140, 206, 164), (380, 330, 900, 420))
    bg.blit(pygame.transform.scale(make_castle(), (170, 170)), (630, 215))
    # near hills and ground
    pygame.draw.ellipse(bg, (104, 190, 76), (-200, 440, 820, 360))
    pygame.draw.ellipse(bg, (92, 178, 66), (300, 460, 900, 360))
    pygame.draw.rect(bg, (80, 170, 60), (0, 560, W, H - 560))
    # winding dirt road
    for i in range(16):
        k = i / 15.0
        x = 480 + math.sin(k * 3.2) * 70 * (1 - k)
        y = H - k * 150
        rw = 70 * (1 - k) + 10
        rh = 20 * (1 - k) + 6
        pygame.draw.ellipse(bg, (240, 206, 120), (int(x - rw), int(y - rh / 2), int(2 * rw), int(rh)))
    # trees
    tree = pygame.transform.scale(make_tree(), (96, 144))
    for pos in ((6, 395), (100, 440), (858, 390), (790, 445)):
        bg.blit(tree, pos)
    # flowers in the grass
    rnd = random.Random(5)
    for _ in range(140):
        x, y = rnd.randrange(W), rnd.randrange(560, H)
        c = rnd.choice([(255, 255, 255), (255, 170, 200), (255, 230, 90), (150, 190, 255)])
        pygame.draw.rect(bg, c, (x, y, 4, 4))
        pygame.draw.rect(bg, (255, 220, 60), (x + 1, y + 1, 2, 2))
    return bg


def scene_bg(kind):
    """Static (non-animated) outdoor backgrounds: 'village' (day) and 'sunrise'. Others live in cutscene.py."""
    if kind not in _cache:
        if kind == "sunrise":
            _cache[kind] = _build_backdrop((255, 150, 100), (255, 226, 160), (480, 330), (255, 228, 150))
        else:
            _cache[kind] = _build_backdrop((84, 166, 250), (255, 232, 186), (800, 110), (255, 236, 130))
    return _cache[kind]


CLOUDS = [(70, 14, 1.0), (150, 9, 1.4), (110, 20, 0.8), (190, 12, 1.1)]
FLOATERS = [("circle", (255, 110, 110), 70, 150), ("triangle", (250, 210, 60), 170, 250),
            ("star", (255, 200, 60), 890, 215), ("square", (90, 170, 255), 880, 320),
            ("heart", (255, 120, 170), 60, 330)]


def _cloud(s, x, y, k):
    for dx, dy, r in ((0, 0, 26), (26, -12, 32), (58, 0, 26), (30, 8, 28)):
        pygame.draw.circle(s, (255, 255, 255), (int(x + dx * k), int(y + dy * k)), int(r * k))


def backdrop(s, t):
    s.blit(scene_bg("village"), (0, 0))
    for i, (y, sp, k) in enumerate(CLOUDS):
        _cloud(s, (i * 290 + t * sp) % (W + 260) - 130, y, k)
    for i, (nm, col, x, y) in enumerate(FLOATERS):
        draw_shape(s, nm, col, x, int(y + math.sin(t * 1.6 + i * 1.7) * 10), 16)


# ------------------------------------------------------------------- title
def title_block(s, t):
    bob = int(math.sin(t * 2.2) * 4)
    outlined(s, "KWIN'S", 128, YELLOW, OUTLINE, (W // 2, 76 + bob), thick=5)
    outlined(s, "GREAT ADVENTURE", 66, WHITE, OUTLINE, (W // 2, 150 + bob // 2), thick=4)
    rb = pygame.Rect(0, 0, 440, 36)
    rb.center = (W // 2, 203)
    pygame.draw.rect(s, (229, 57, 53), rb, border_radius=18)
    pygame.draw.rect(s, OUTLINE, rb, 3, border_radius=18)
    for dx, word in ((-135, "Learn"), (0, "Play"), (135, "Explore")):
        text(s, word, 26, WHITE, (rb.centerx + dx, rb.centery), shadow=OUTLINE)
    for dx in (-68, 68):
        draw_star(s, rb.centerx + dx, rb.centery, 8)


# ----------------------------------------------------------- buttons, icons
def draw_icon(s, kind, cx, cy, col):
    if kind == "play":
        pygame.draw.polygon(s, col, [(cx - 6, cy - 10), (cx - 6, cy + 10), (cx + 10, cy)])
    elif kind == "book":
        pygame.draw.rect(s, col, (cx - 10, cy - 8, 20, 16), border_radius=2)
        pygame.draw.line(s, WHITE, (cx, cy - 8), (cx, cy + 8), 2)
    elif kind == "gear":
        pygame.draw.circle(s, col, (cx, cy), 8)
        for i in range(8):
            a = i * math.pi / 4
            pygame.draw.line(s, col, (cx + math.cos(a) * 7, cy + math.sin(a) * 7),
                             (cx + math.cos(a) * 12, cy + math.sin(a) * 12), 4)
        pygame.draw.circle(s, WHITE, (cx, cy), 3)
    elif kind == "star":
        draw_shape(s, "star", col, cx, cy, 12)
    elif kind == "quit":
        pygame.draw.line(s, col, (cx - 8, cy - 8), (cx + 8, cy + 8), 5)
        pygame.draw.line(s, col, (cx + 8, cy - 8), (cx - 8, cy + 8), 5)
    elif kind == "sound":
        pygame.draw.polygon(s, col, [(cx - 10, cy - 4), (cx - 4, cy - 4), (cx + 2, cy - 10), (cx + 2, cy + 10),
                                     (cx - 4, cy + 4), (cx - 10, cy + 4)])
        pygame.draw.arc(s, col, (cx - 2, cy - 7, 14, 14), -1.0, 1.0, 3)
    elif kind == "music":
        pygame.draw.circle(s, col, (cx - 4, cy + 6), 5)
        pygame.draw.line(s, col, (cx + 1, cy + 5), (cx + 1, cy - 9), 3)
        pygame.draw.line(s, col, (cx + 1, cy - 9), (cx + 8, cy - 6), 3)
    elif kind == "hint":
        text(s, "?", 30, col, (cx, cy))
    elif kind == "reset":
        pygame.draw.arc(s, col, (cx - 9, cy - 9, 18, 18), 0.6, 5.6, 4)
        pygame.draw.polygon(s, col, [(cx + 9, cy - 11), (cx + 11, cy - 1), (cx + 2, cy - 4)])
    elif kind == "back":
        pygame.draw.polygon(s, col, [(cx - 11, cy), (cx + 1, cy - 10), (cx + 1, cy - 4), (cx + 11, cy - 4),
                                     (cx + 11, cy + 4), (cx + 1, cy + 4), (cx + 1, cy + 10)])
    else:
        pygame.draw.circle(s, col, (cx, cy), 7)


def draw_button(s, rect, label, selected, color, t=0.0, icon=None):
    r = rect.copy()
    if selected:
        r.inflate_ip(16, 6)
        r.y -= 2 + int(abs(math.sin(t * 6)) * 2)
    fill = _lighten(color, 45) if selected else color
    pygame.draw.rect(s, darker(color, 100), r.move(0, 7), border_radius=18)
    pygame.draw.rect(s, fill, r, border_radius=18)
    pygame.draw.rect(s, OUTLINE, r, 4, border_radius=18)
    pygame.draw.rect(s, _lighten(fill, 60), (r.x + 16, r.y + 7, r.w - 32, 6), border_radius=3)
    left = 0
    if icon:
        c = (r.x + 36, r.centery + 1)
        pygame.draw.circle(s, WHITE, c, 19)
        pygame.draw.circle(s, OUTLINE, c, 19, 3)
        draw_icon(s, icon, c[0], c[1], darker(color, 40))
        left = 30
    fit_text(s, label, 34, r.w - 70 - left, WHITE, (r.centerx + left // 2, r.centery + 2), shadow=OUTLINE)
    if selected:
        ax = r.x - 20
        tri = [(ax - 4, r.centery - 13), (ax - 4, r.centery + 13), (ax + 14, r.centery)]
        pygame.draw.polygon(s, YELLOW, tri)
        pygame.draw.polygon(s, OUTLINE, tri, 3)


def panel(s, rect, fill=CREAM, edge=OUTLINE):
    pygame.draw.rect(s, darker(fill, 60), rect.move(0, 8), border_radius=24)
    pygame.draw.rect(s, fill, rect, border_radius=24)
    pygame.draw.rect(s, edge, rect, 5, border_radius=24)
