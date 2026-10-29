"""Drag-and-drop sorting scene (Mixed-up Farm)."""
import math
import random
import pygame
from settings import COLS_NAMED, NAVY, NODES, W
from helpers import draw_item, draw_page, draw_stages, fit_text, text


SORT_ROUNDS = [
    ("Sort the apples by COLOR!", ["RED APPLES", "GREEN APPLES"], lambda g: ("apple", [COLS_NAMED["red"], (90, 190, 70)][g], 26)),
    ("Sort the pumpkins by SIZE!", ["BIG PUMPKINS", "SMALL PUMPKINS"], lambda g: ("pumpkin", None, [40, 22][g])),
    ("Apples or carrots? Sort them!", ["APPLES", "CARROTS"], lambda g: (["apple", "carrot"][g], COLS_NAMED["red"], 28)),
]


class Sorting:
    def __init__(self, game, level):
        self.g, self.level = game, level
        self.round = 0
        self.mistakes = 0
        self.finished = False
        self.msg, self.msg_col, self.msg_t = "", NAVY, 0.0
        self.good_t = 0.0
        self.drag = None
        self.baskets = [pygame.Rect(150, 395, 300, 110), pygame.Rect(510, 395, 300, 110)]
        self._setup()

    def _setup(self):
        _, _, mk = SORT_ROUNDS[self.round]
        self.items = []
        groups = [0, 0, 0, 1, 1, 1]
        random.shuffle(groups)
        for i, grp in enumerate(groups):
            kind, col, size = mk(grp)
            self.items.append(dict(kind=kind, color=col, size=size, group=grp, placed=False,
                                   home=(150 + i * 132, 285), pos=[150 + i * 132, 285]))
        self.slots = [0, 0]

    @property
    def stage(self):
        return 3 if (self.good_t > 0 or self.msg_t > 0) else 2

    def event(self, e):
        if self.good_t > 0:
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for it in reversed(self.items):
                if not it["placed"] and math.hypot(e.pos[0] - it["pos"][0], e.pos[1] - it["pos"][1]) < max(it["size"], 30) + 14:
                    self.drag = it
                    self.g.sfx.play("pick")
                    break
        elif e.type == pygame.MOUSEMOTION and self.drag:
            self.drag["pos"] = [e.pos[0], e.pos[1]]
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.drag:
            it, self.drag = self.drag, None
            for b, rc in enumerate(self.baskets):
                if rc.inflate(40, 60).collidepoint(e.pos):
                    if b == it["group"]:
                        it["placed"] = True
                        k = self.slots[b]
                        self.slots[b] += 1
                        it["pos"] = [rc.x + 55 + (k % 3) * 95, rc.y + 22 + (k // 3) * 8]
                        self.g.sfx.play("good")
                        self.msg, self.msg_col, self.msg_t = random.choice(["Nice sorting!", "That's right!", "Perfect!"]), (30, 150, 70), 1.0
                        if all(i["placed"] for i in self.items):
                            self.good_t = 1.4
                    else:
                        self.mistakes += 1
                        self.g.sfx.play("bad")
                        self.msg = "Oops, wrong basket!" + ("  Check the label." if self.g.save["hints"] else "")
                        self.msg_col, self.msg_t = (200, 70, 60), 2.0
                        it["pos"] = list(it["home"])
                    return
            it["pos"] = list(it["home"])

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)
        if self.good_t > 0:
            self.good_t -= dt
            if self.good_t <= 0:
                self.round += 1
                self.msg = ""
                if self.round >= len(SORT_ROUNDS):
                    self.finished = True
                else:
                    self._setup()

    def draw(self, s):
        node = NODES[self.level - 1]
        draw_page(s, f"KWIN - Level {self.level}: {node['name']}", node["skill"])
        draw_stages(s, self.stage, 98)
        fit_text(s, SORT_ROUNDS[min(self.round, 2)][0], 46, 880, NAVY, (W // 2, 172))
        text(s, "Drag each item into the correct basket", 26, (110, 110, 125), (W // 2, 205), bold=False)
        labels = SORT_ROUNDS[min(self.round, 2)][1]
        for b, rc in enumerate(self.baskets):
            pygame.draw.rect(s, (170, 115, 62), rc, border_radius=10)
            for y in range(rc.y + 12, rc.bottom, 14):
                pygame.draw.line(s, (140, 90, 48), (rc.x + 4, y), (rc.right - 4, y), 3)
            pygame.draw.rect(s, (90, 56, 30), rc, 5, border_radius=10)
            text(s, labels[b], 30, NAVY, (rc.centerx, rc.bottom + 24))
        for it in self.items:
            if it["placed"]:
                draw_item(s, it, int(it["pos"][0]), int(it["pos"][1]))
        for it in self.items:
            if not it["placed"]:
                draw_item(s, it, int(it["pos"][0]), int(it["pos"][1]))
        if self.drag:
            draw_item(s, self.drag, int(self.drag["pos"][0]), int(self.drag["pos"][1]) - 4)
        if self.msg:
            fit_text(s, self.msg, 34, 900, self.msg_col, (W // 2, 575))
        for k in range(len(SORT_ROUNDS)):
            col = (60, 170, 90) if k < self.round else ((255, 200, 80) if k == self.round else (215, 215, 225))
            pygame.draw.circle(s, col, (W // 2 + (k - 1) * 30, 612), 9)
