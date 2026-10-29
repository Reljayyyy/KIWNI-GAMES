"""Multiple-choice challenge scene."""
import math
import random
import pygame
from settings import NAVY, NODES, W, WHITE
from sprites import IMG
from helpers import F, draw_page, draw_stages, draw_star, fit_text, text, wrap
from questions import make_questions


class Quiz:
    def __init__(self, game, level):
        self.g, self.level = game, level
        self.qs = make_questions(level)
        self.i = 0
        self.mistakes = 0
        self.wrong = set()
        self.msg, self.msg_col, self.msg_t = "", NAVY, 0.0
        self.good_t = 0.0
        self.finished = False
        self._layout()

    def _layout(self):
        n = len(self.qs[self.i]["options"])
        cw, ch, gap = 190, 130, 24
        x0 = (W - (n * cw + (n - 1) * gap)) // 2
        self.rects = [pygame.Rect(x0 + k * (cw + gap), 385, cw, ch) for k in range(n)]

    @property
    def stage(self):
        return 3 if (self.good_t > 0 or self.msg_t > 0) else 2

    def choose(self, k):
        if self.good_t > 0 or k in self.wrong:
            return
        q = self.qs[self.i]
        if k == q["answer"]:
            self.g.sfx.play("good")
            self.good_t = 1.2
            self.msg, self.msg_col = random.choice(["Great job!", "Awesome!", "You got it!", "Super smart!"]), (30, 150, 70)
        else:
            self.g.sfx.play("bad")
            self.wrong.add(k)
            self.mistakes += 1
            self.msg = "Not quite, try again!"
            if self.g.save["hints"]:
                self.msg += "  Hint: " + q["hint"]
            self.msg_col, self.msg_t = (200, 70, 60), 3.0

    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for k, r in enumerate(self.rects):
                if r.collidepoint(e.pos):
                    self.choose(k)
        elif e.type == pygame.KEYDOWN and pygame.K_1 <= e.key <= pygame.K_4:
            k = e.key - pygame.K_1
            if k < len(self.rects):
                self.choose(k)

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)
        if self.good_t > 0:
            self.good_t -= dt
            if self.good_t <= 0:
                self.i += 1
                self.wrong.clear()
                self.msg = ""
                if self.i >= len(self.qs):
                    self.finished = True
                else:
                    self._layout()

    def draw(self, s):
        node = NODES[self.level - 1]
        draw_page(s, f"KWIN - Level {self.level}: {node['name']}", node["skill"])
        draw_stages(s, self.stage, 98)
        self.draw_body(s)

    def draw_body(self, s):
        q = self.qs[min(self.i, len(self.qs) - 1)]
        fit_text(s, q["prompt"], 46, 880, NAVY, (W // 2, 172))
        vr = pygame.Rect(180, 205, 600, 160)
        pygame.draw.rect(s, WHITE, vr, border_radius=16)
        pygame.draw.rect(s, (230, 190, 100), vr, 3, border_radius=16)
        if q["visual"]:
            q["visual"](s, vr)
        else:
            s.blit(IMG["mid"], IMG["mid"].get_rect(midbottom=(vr.centerx, vr.bottom - 6)))
        mouse = pygame.mouse.get_pos()
        for k, r in enumerate(self.rects):
            bad = k in self.wrong
            right = self.good_t > 0 and k == q["answer"]
            bg = (225, 225, 230) if bad else ((255, 245, 200) if r.collidepoint(mouse) else WHITE)
            pygame.draw.rect(s, bg, r, border_radius=14)
            pygame.draw.rect(s, (40, 170, 80) if right else ((200, 70, 60) if bad else (230, 190, 100)), r, 5 if right or bad else 3, border_radius=14)
            o = q["options"][k]
            if callable(o):
                o(s, r)
            else:
                lines = wrap(o, F(36), r.w - 20)
                for li, line in enumerate(lines):
                    text(s, line, 36, NAVY, (r.centerx, r.centery + (li - (len(lines) - 1) / 2) * 34))
            text(s, str(k + 1), 20, (150, 150, 165), (r.x + 12, r.y + 12), "topleft")
        if self.msg:
            fit_text(s, self.msg, 34, 900, self.msg_col, (W // 2, 560))
        for k in range(len(self.qs)):
            col = (60, 170, 90) if k < self.i else ((255, 200, 80) if k == self.i else (215, 215, 225))
            pygame.draw.circle(s, col, (W // 2 + (k - (len(self.qs) - 1) / 2) * 30, 608), 9)
        if self.good_t > 0:
            for k in range(5):
                a = self.good_t * 4 + k * 1.26
                draw_star(s, int(W // 2 + math.cos(a) * 120), int(300 + math.sin(a) * 40 - (1.2 - self.good_t) * 30), 14)
