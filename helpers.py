"""Text and drawing helpers (shapes, flowers, apples, clock, page + stage bar)."""
import math
import pygame
from settings import CREAM, NAVY, NODES, W, WHITE, YELLOW


_fonts = {}


def F(size, bold=True):
    k = (size, bold)
    if k not in _fonts:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        _fonts[k] = f
    return _fonts[k]


def text(surf, s, size, color, pos, anchor="center", shadow=None, bold=True):
    img = F(size, bold).render(s, True, color)
    r = img.get_rect()
    setattr(r, anchor, pos)
    if shadow:
        surf.blit(F(size, bold).render(s, True, shadow), r.move(2, 2))
    surf.blit(img, r)
    return r


def fit_text(surf, s, size, maxw, color, pos, anchor="center", shadow=None):
    while size > 12 and F(size).size(s)[0] > maxw:
        size -= 2
    return text(surf, s, size, color, pos, anchor, shadow)


def wrap(s, font, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.size(t)[0] <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def darker(c, n=70):
    return tuple(max(0, v - n) for v in c)


def poly(s, col, pts, width=3):
    pygame.draw.polygon(s, col, pts)
    pygame.draw.polygon(s, darker(col), pts, width)


def draw_shape(s, name, col, cx, cy, r):
    if name == "circle":
        pygame.draw.circle(s, col, (cx, cy), r)
        pygame.draw.circle(s, darker(col), (cx, cy), r, 3)
    elif name == "square":
        rc = pygame.Rect(cx - r, cy - r, 2 * r, 2 * r)
        pygame.draw.rect(s, col, rc)
        pygame.draw.rect(s, darker(col), rc, 3)
    elif name == "rectangle":
        rc = pygame.Rect(cx - int(r * 1.35), cy - int(r * 0.8), int(r * 2.7), int(r * 1.6))
        pygame.draw.rect(s, col, rc)
        pygame.draw.rect(s, darker(col), rc, 3)
    elif name == "triangle":
        poly(s, col, [(cx, cy - r), (cx - r, cy + int(r * 0.8)), (cx + r, cy + int(r * 0.8))])
    elif name == "diamond":
        poly(s, col, [(cx, cy - r), (cx + int(r * 0.8), cy), (cx, cy + r), (cx - int(r * 0.8), cy)])
    elif name == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        poly(s, col, pts)
    elif name == "heart":
        rr = int(r * 0.55)
        pygame.draw.circle(s, col, (cx - rr, cy - rr // 2), rr)
        pygame.draw.circle(s, col, (cx + rr, cy - rr // 2), rr)
        pygame.draw.polygon(s, col, [(cx - r + 2, cy - rr // 3), (cx + r - 2, cy - rr // 3), (cx, cy + r)])


def draw_star(s, cx, cy, r, on=True):
    draw_shape(s, "star", YELLOW if on else (205, 205, 215), cx, cy, r)


def draw_flower(s, col, cx, cy, r=18):
    pygame.draw.line(s, (50, 140, 60), (cx, cy), (cx, cy + r + 18), 4)
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        pygame.draw.circle(s, col, (int(cx + math.cos(a) * r * 0.8), int(cy + math.sin(a) * r * 0.8)), int(r * 0.55))
        pygame.draw.circle(s, darker(col, 50), (int(cx + math.cos(a) * r * 0.8), int(cy + math.sin(a) * r * 0.8)), int(r * 0.55), 2)
    pygame.draw.circle(s, (255, 230, 80), (cx, cy), int(r * 0.45))


def draw_apple(s, cx, cy, r, col):
    pygame.draw.circle(s, col, (cx, cy), r)
    pygame.draw.circle(s, darker(col, 60), (cx, cy), r, 3)
    pygame.draw.rect(s, (255, 255, 255), (cx - r // 2, cy - r // 2, max(3, r // 4), max(3, r // 4)))
    pygame.draw.line(s, (110, 70, 40), (cx, cy - r), (cx + 2, cy - r - r // 3), 3)
    pygame.draw.ellipse(s, (60, 170, 70), (cx + 2, cy - r - r // 4, r // 2 + 2, r // 3 + 2))


def draw_pumpkin(s, cx, cy, r):
    rc = pygame.Rect(cx - r, cy - int(r * 0.8), 2 * r, int(r * 1.6))
    pygame.draw.ellipse(s, (240, 130, 30), rc)
    pygame.draw.ellipse(s, (170, 80, 20), rc, 3)
    pygame.draw.line(s, (200, 100, 20), (cx, rc.top + 3), (cx, rc.bottom - 3), 2)
    pygame.draw.line(s, (200, 100, 20), (cx - r // 2, rc.top + 6), (cx - r // 2, rc.bottom - 6), 2)
    pygame.draw.line(s, (200, 100, 20), (cx + r // 2, rc.top + 6), (cx + r // 2, rc.bottom - 6), 2)
    pygame.draw.rect(s, (70, 140, 60), (cx - 3, rc.top - 7, 6, 9))


def draw_carrot(s, cx, cy, r):
    poly(s, (245, 135, 30), [(cx - int(r * 0.55), cy - r), (cx + int(r * 0.55), cy - r), (cx, cy + int(r * 1.3))], 2)
    for dx in (-6, 0, 6):
        pygame.draw.line(s, (70, 170, 70), (cx + dx // 2, cy - r), (cx + dx, cy - r - 14), 4)


def draw_item(s, it, cx, cy):
    if it["kind"] == "apple":
        draw_apple(s, cx, cy, it["size"], it["color"])
    elif it["kind"] == "pumpkin":
        draw_pumpkin(s, cx, cy, it["size"])
    else:
        draw_carrot(s, cx, cy, it["size"])


def draw_arrow(s, d, cx, cy, sz, col=(60, 110, 230)):
    dx, dy = d
    base = [(-sz, -sz / 3), (0, -sz / 3), (0, -sz * 0.8), (sz, 0), (0, sz * 0.8), (0, sz / 3), (-sz, sz / 3)]
    pts = [(cx + px * dx - py * dy, cy + px * dy + py * dx) for px, py in base]
    poly(s, col, pts)


def draw_clock(s, cx, cy, r, h, m):
    pygame.draw.circle(s, WHITE, (cx, cy), r)
    pygame.draw.circle(s, NAVY, (cx, cy), r, 5)
    for i in range(12):
        a = i * math.pi / 6
        p1 = (cx + math.sin(a) * (r - 6), cy - math.cos(a) * (r - 6))
        p2 = (cx + math.sin(a) * (r - 14), cy - math.cos(a) * (r - 14))
        pygame.draw.line(s, NAVY, p1, p2, 3)
    for n, ang in ((12, 0), (3, 90), (6, 180), (9, 270)):
        a = math.radians(ang)
        text(s, str(n), 22, NAVY, (cx + math.sin(a) * (r - 26), cy - math.cos(a) * (r - 26)))
    ha = math.radians(((h % 12) + m / 60) * 30)
    ma = math.radians(m * 6)
    pygame.draw.line(s, NAVY, (cx, cy), (cx + math.sin(ha) * r * 0.5, cy - math.cos(ha) * r * 0.5), 7)
    pygame.draw.line(s, (220, 60, 60), (cx, cy), (cx + math.sin(ma) * r * 0.75, cy - math.cos(ma) * r * 0.75), 4)
    pygame.draw.circle(s, NAVY, (cx, cy), 6)


def draw_page(s, title, sub=None):
    s.fill(CREAM)
    pygame.draw.rect(s, (255, 200, 80), (0, 0, W, 8))
    text(s, title, 40, NAVY, (40, 42), "midleft")
    if sub:
        text(s, sub, 24, (110, 110, 125), (40, 74), "midleft", bold=False)


STAGES = ["STORY INTRO", "DIALOGUE", "LEARNING CHALLENGE", "FEEDBACK", "STORY PROGRESSION"]


def draw_stages(s, idx, y):
    pw, gap = 152, 12
    x0 = (W - (5 * pw + 4 * gap)) // 2
    for i, name in enumerate(STAGES):
        r = pygame.Rect(x0 + i * (pw + gap), y, pw, 30)
        on = i == idx
        pygame.draw.rect(s, (255, 200, 80) if on else WHITE, r, border_radius=15)
        pygame.draw.rect(s, (230, 190, 100), r, 2, border_radius=15)
        text(s, name, 18, NAVY, r.center)


def draw_gem_row(s, cx, cy, flags, r=14, gap=44):
    """Row of Rainbow Gems; flags[i] is True once gem i+1 has been won."""
    x0 = cx - (len(flags) - 1) * gap / 2.0
    for i, got in enumerate(flags):
        col = NODES[i]["color"] if got else (170, 170, 182)
        draw_shape(s, "diamond", col, int(x0 + i * gap), cy, r)
