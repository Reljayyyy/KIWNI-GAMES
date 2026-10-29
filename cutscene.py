"""Story scenes: dialogue panels with portraits, plus the animated THE END screen."""
import math
import random

import pygame

from settings import W, H, NAVY, WHITE, YELLOW, CREAM, CREATOR, NODES
from sprites import HERO, character_preview
from helpers import F, text, wrap, draw_gem_row, darker
from bossart import boss_surface
from menu_ui import scene_bg, outlined, OUTLINE, panel
from story import tell

_cache = {}
BOX = pygame.Rect(40, 432, 880, 190)


def _hall():
    s = pygame.Surface((W, H))
    s.fill((38, 24, 62))
    for row in range(0, 440, 40):
        off = 0 if (row // 40) % 2 == 0 else 40
        for x in range(-off, W, 80):
            pygame.draw.rect(s, (50, 34, 80), (x + 2, row + 2, 76, 36), border_radius=3)
    for wx in (150, 480, 810):
        win = pygame.Rect(wx - 34, 90, 68, 150)
        pygame.draw.rect(s, (24, 16, 48), win, border_top_left_radius=34, border_top_right_radius=34)
        pygame.draw.rect(s, (120, 90, 200), win, 4, border_top_left_radius=34, border_top_right_radius=34)
        pygame.draw.circle(s, (250, 240, 200), (wx + 8, 140), 16)
        pygame.draw.circle(s, (24, 16, 48), (wx + 16, 134), 14)
    pygame.draw.rect(s, (66, 44, 96), (0, 430, W, 210))
    for r in range(5):
        for c in range(0, W, 80):
            if (r + c // 80) % 2 == 0:
                pygame.draw.rect(s, (74, 50, 106), (c, 430 + r * 42, 80, 42))
    pygame.draw.polygon(s, (170, 40, 70), [(380, 640), (580, 640), (545, 430), (415, 430)])
    for tx in (60, 900):
        pygame.draw.rect(s, (110, 70, 40), (tx - 5, 290, 10, 60))
        pygame.draw.circle(s, (255, 150, 40), (tx, 276), 17)
        pygame.draw.circle(s, (255, 220, 90), (tx, 280), 9)
    return s


def bg_surface(kind):
    if kind == "hall":
        if "hall" not in _cache:
            _cache["hall"] = _hall()
        return _cache["hall"]
    return scene_bg(kind)


def boss_portrait(mood, h):
    key = (mood, h)
    if key not in _cache:
        _cache[key] = boss_surface(mood, h)
    return _cache[key]


def dimmed(img):
    d = img.copy()
    d.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return d


class Cutscene:
    def __init__(self, game, panels, bg, cast=("hero",), music="quiz"):
        self.g = game
        self.bg, self.cast, self.music = bg, cast, music
        self.panels = []
        for p in panels:
            self.panels.append(dict(who=p[0], text=tell(p[1]), mood=p[2] if len(p) > 2 else None))
        # the boss keeps the mood of his nearest line while the hero is talking
        last = "angry"
        for p in self.panels:
            if p["who"] == "boss" and p["mood"]:
                last = p["mood"]
        nxt = last
        for p in reversed(self.panels):
            if p["who"] == "boss":
                nxt = p["mood"] or "angry"
            elif p["mood"] is None:
                p["mood"] = nxt
        prev = None
        for p in self.panels:
            if p["who"] == "boss":
                prev = p["mood"]
            elif prev:
                p["mood"] = prev
        self.i = 0
        self.chars = 0.0
        self.t = 0.0
        self.panel_t = 0.0
        colors = [(255, 90, 140), (255, 200, 60), (90, 200, 120), (90, 170, 255), (190, 110, 230)]
        self.confetti = [[random.random() * W, random.random() * H, random.random() * 6.28,
                          random.choice(colors), 40 + random.random() * 60] for _ in range(70)]

    @property
    def cur(self):
        return self.panels[self.i]

    # ------------------------------------------------------------ events
    def event(self, e):
        """Returns True when the scene is over."""
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            return True
        if self.g.confirm_key(e) or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
            p = self.cur
            if p["who"] == "end":
                return self.panel_t > 0.8
            if self.chars < len(p["text"]):
                self.chars = len(p["text"])
            elif self.i + 1 < len(self.panels):
                self.i += 1
                self.chars = 0.0
                self.panel_t = 0.0
                self.g.sfx.play("click")
                if self.cur["who"] == "boss" and self.cur["mood"] == "angry":
                    self.g.sfx.play("roar")
            else:
                return True
        return False

    def update(self, dt):
        self.t += dt
        self.panel_t += dt
        p = self.cur
        if p["who"] == "end":
            for c in self.confetti:
                c[1] += c[4] * dt
                c[0] += math.sin(self.t * 2 + c[2]) * 30 * dt
                if c[1] > H + 10:
                    c[1] = -10
            return
        before = int(self.chars)
        self.chars += 45 * dt
        after = int(self.chars)
        if after // 3 > before // 3 and after < len(p["text"]):
            self.g.sfx.play("blip")

    # ------------------------------------------------------------- drawing
    def draw(self, s):
        p = self.cur
        if p["who"] == "end":
            self.draw_end(s)
            return
        s.blit(bg_surface(self.bg), (0, 0))
        bob = int(math.sin(self.t * 3) * 3)
        if "hero" in self.cast:
            img = character_preview(HERO["index"], 240)
            talking = p["who"] == "hero"
            s.blit(img if talking else dimmed(img), img.get_rect(bottomleft=(70, 440 + (bob if talking else 0))))
        if "boss" in self.cast:
            img = boss_portrait(p["mood"] or "angry", 280)
            talking = p["who"] == "boss"
            s.blit(img if talking else dimmed(img), img.get_rect(midbottom=(790, 450 + (bob if talking else 0))))
        edge = {"hero": (255, 170, 40), "boss": (150, 80, 210)}.get(p["who"], (120, 110, 150))
        panel(s, BOX, CREAM, edge)
        if p["who"] in ("hero", "boss"):
            name = HERO["name"] if p["who"] == "hero" else "MUDDLE KING"
            tag = pygame.Rect(0, 0, max(150, F(30).size(name.upper())[0] + 40), 40)
            if p["who"] == "hero":
                tag.topleft = (BOX.x + 30, BOX.y - 22)
            else:
                tag.topright = (BOX.right - 30, BOX.y - 22)
            pygame.draw.rect(s, edge, tag, border_radius=12)
            pygame.draw.rect(s, OUTLINE, tag, 3, border_radius=12)
            text(s, name.upper(), 30, WHITE, tag.center, shadow=OUTLINE)
        shown = p["text"][:int(self.chars)]
        lines = wrap(shown, F(32, False), BOX.w - 70)
        for k, ln in enumerate(lines):
            text(s, ln, 32, NAVY, (BOX.x + 36, BOX.y + 40 + k * 38), "midleft", bold=False)
        if self.chars >= len(p["text"]) and int(self.t * 2) % 2 == 0:
            ax, ay = BOX.right - 46, BOX.bottom - 36
            pygame.draw.polygon(s, OUTLINE, [(ax - 10, ay - 8), (ax + 10, ay - 8), (ax, ay + 8)])
        text(s, "ESC: skip", 20, WHITE, (W - 14, 14), "topright", shadow=OUTLINE)

    def draw_end(self, s):
        s.blit(bg_surface("sunrise"), (0, 0))
        for x, y, ph, col, _ in self.confetti:
            pygame.draw.rect(s, col, (int(x), int(y), 8, 5))
        outlined(s, "THE END", 130, YELLOW, OUTLINE, (W // 2, 92), thick=6)
        outlined(s, f"Thank you for playing, {HERO['name']}!", 38, WHITE, OUTLINE, (W // 2, 185), thick=3)
        bob = int(abs(math.sin(self.t * 4)) * 8)
        hero = character_preview(HERO["index"], 200)
        s.blit(hero, hero.get_rect(midbottom=(W // 2 - 150, 478 - bob)))
        boss = boss_portrait("happy", 230)
        s.blit(boss, boss.get_rect(midbottom=(W // 2 + 150, 484 - (8 - bob))))
        box = pygame.Rect(150, 486, 660, 150)
        panel(s, box)
        stars = sum(self.g.save["done"].values())
        text(s, f"Stars collected: {stars} / 24", 34, NAVY, (W // 2, box.y + 30))
        flags = [str(i) in self.g.save["done"] for i in range(1, 8)]
        draw_gem_row(s, W // 2, box.y + 70, flags, r=14, gap=44)
        text(s, f"Game made by {CREATOR}", 24, (110, 100, 130), (W // 2, box.y + 104), bold=False)
        if self.panel_t > 0.8 and int(self.t * 2) % 2 == 0:
            text(s, "Press SPACE to return to the village", 26, NAVY, (W // 2, box.y + 132))
