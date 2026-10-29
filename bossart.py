"""The Muddle King, drawn in code (final boss), plus portrait surfaces for dialogue."""
import math
import pygame
from helpers import draw_shape

WHITE = (255, 255, 255)
BODY = (126, 72, 190)
BODY_D = (60, 30, 100)
BELLY = (180, 136, 228)
GOLD = (255, 206, 60)
GOLD_D = (150, 100, 20)
MOUTH = (50, 20, 60)


def draw_muddle_king(s, cx, cy, h, t=0.0, mood="angry"):
    """Draw the Muddle King centred on (cx, cy), h pixels tall.
    mood: angry, hurt, defeated, sad, happy."""
    k = h / 200.0

    def X(x):
        return int(cx + (x - 100) * k)

    def Y(y):
        return int(cy + (y - 100) * k)

    def L(v):
        return max(1, int(v * k))

    def ell(x, y, w, hh, col, border=4):
        r = pygame.Rect(X(x - w / 2), Y(y - hh / 2), L(w), L(hh))
        pygame.draw.ellipse(s, col, r)
        if border:
            pygame.draw.ellipse(s, BODY_D, r, max(2, L(border)))

    def line(p, q, w, col=BODY_D):
        pygame.draw.line(s, col, (X(p[0]), Y(p[1])), (X(q[0]), Y(q[1])), L(w))

    def pts(lst):
        return [(X(x), Y(y)) for x, y in lst]

    def eye(x, y, r=18):
        pygame.draw.circle(s, WHITE, (X(x), Y(y)), L(r))
        pygame.draw.circle(s, BODY_D, (X(x), Y(y)), L(r), max(2, L(3)))

    def pupil(x, y, r=8):
        pygame.draw.circle(s, (20, 10, 30), (X(x), Y(y)), L(r))

    # jumbled shapes circling behind him
    if mood != "defeated":
        for i, (nm, col) in enumerate((("circle", (255, 120, 120)), ("triangle", (250, 210, 60)),
                                       ("square", (90, 170, 255)), ("star", (120, 230, 150)))):
            a = t * 1.6 + i * math.pi / 2
            draw_shape(s, nm, col, X(100 + math.cos(a) * 92), Y(70 + math.sin(a) * 42), L(11))

    arm_y = 105 if mood == "hurt" else 128
    ell(60, 186, 52, 26, BODY_D, 0)
    ell(140, 186, 52, 26, BODY_D, 0)
    ell(22, arm_y, 36, 64, BODY)
    ell(178, arm_y, 36, 64, BODY)
    ell(100, 125, 150, 140, BODY)
    ell(100, 145, 90, 70, BELLY, 3)

    if mood == "angry":
        eye(70, 100)
        eye(130, 100)
        pupil(72, 104)
        pupil(128, 104)
        line((44, 78), (90, 94), 7)
        line((156, 78), (110, 94), 7)
        ell(100, 152, 66, 32, MOUTH, 3)
        pygame.draw.polygon(s, WHITE, pts([(80, 140), (92, 140), (86, 152)]))
        pygame.draw.polygon(s, WHITE, pts([(108, 140), (120, 140), (114, 152)]))
    elif mood == "sad":
        eye(70, 100)
        eye(130, 100)
        pupil(70, 108)
        pupil(130, 108)
        line((46, 90), (88, 78), 6)
        line((154, 90), (112, 78), 6)
        pygame.draw.arc(s, BODY_D, pygame.Rect(X(74), Y(146), L(52), L(36)), 0, math.pi, max(2, L(5)))
        ell(56, 126, 10, 16, (120, 190, 255), 0)
    elif mood == "hurt":
        pygame.draw.lines(s, BODY_D, False, pts([(52, 88), (84, 102), (52, 116)]), max(2, L(6)))
        pygame.draw.lines(s, BODY_D, False, pts([(148, 88), (116, 102), (148, 116)]), max(2, L(6)))
        ell(100, 152, 34, 40, MOUTH, 3)
    elif mood == "defeated":
        line((56, 88), (84, 116), 6)
        line((84, 88), (56, 116), 6)
        line((116, 88), (144, 116), 6)
        line((144, 88), (116, 116), 6)
        pygame.draw.lines(s, BODY_D, False, pts([(76, 152), (88, 146), (100, 152), (112, 146), (124, 152)]), max(2, L(5)))
    else:  # happy
        pygame.draw.arc(s, BODY_D, pygame.Rect(X(52), Y(90), L(36), L(30)), 0, math.pi, max(2, L(5)))
        pygame.draw.arc(s, BODY_D, pygame.Rect(X(112), Y(90), L(36), L(30)), 0, math.pi, max(2, L(5)))
        pygame.draw.arc(s, BODY_D, pygame.Rect(X(70), Y(122), L(60), L(44)), math.pi, 2 * math.pi, max(2, L(5)))
        ell(46, 128, 22, 14, (255, 150, 170), 0)
        ell(154, 128, 22, 14, (255, 150, 170), 0)

    dx, dy = (12, 14) if mood == "defeated" else (0, 0)
    crown = pts([(64 + dx, 52 + dy), (70 + dx, 22 + dy), (86 + dx, 42 + dy), (100 + dx, 14 + dy),
                 (114 + dx, 42 + dy), (130 + dx, 22 + dy), (136 + dx, 52 + dy)])
    pygame.draw.polygon(s, GOLD, crown)
    pygame.draw.polygon(s, GOLD_D, crown, max(2, L(3)))
    for gx, gy, col in ((70, 28, (230, 60, 60)), (100, 20, (80, 150, 255)), (130, 28, (80, 220, 120))):
        pygame.draw.circle(s, col, (X(gx + dx), Y(gy + dy)), L(5))


def boss_surface(mood, h=200):
    """A square transparent image of the Muddle King (used as a dialogue portrait)."""
    s = pygame.Surface((h, h), pygame.SRCALPHA)
    draw_muddle_king(s, h // 2, h // 2, h, 0.0, mood)
    return s
