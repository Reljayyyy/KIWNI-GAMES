"""Level 8 final boss battle: the Muddle King.

Answer riddles from every world. A right answer damages the boss, a wrong answer costs a heart.
When the hearts run out the hero's friends cheer and the hearts come back, so nobody is ever stuck.
"""
import math
import random

import pygame

from settings import W, NAVY, WHITE, YELLOW
from sprites import HERO, character_preview
from helpers import F, text, fit_text, wrap, draw_shape, draw_star
from bossart import draw_muddle_king
from cutscene import bg_surface
from menu_ui import OUTLINE, panel
from quiz import Quiz
from story import BOSS_PHASES, tell
import questions as Q

PHASE_GENS = [[Q.q_shape, Q.q_color], [Q.q_count, Q.q_count], [Q.q_direction, Q.q_pattern], [Q.q_clock, Q.q_clock]]
BANNER_TIME = 2.8


class BossBattle(Quiz):
    def __init__(self, game, level=8):
        self.g, self.level = game, level
        self.qs, self.phase_of = [], []
        seen = set()
        for pi, gens in enumerate(PHASE_GENS):
            for gen in gens:
                q = gen()
                for _ in range(40):
                    q = gen()
                    if (q.get("sig") or (q["prompt"], q["answer"])) not in seen:
                        break
                seen.add(q.get("sig") or (q["prompt"], q["answer"]))
                q["gen"] = gen
                self.qs.append(q)
                self.phase_of.append(pi)
        self.i = 0
        self.mistakes = 0
        self.wrong = set()
        self.msg, self.msg_col, self.msg_t = "", NAVY, 0.0
        self.good_t = 0.0
        self.finished = False
        self.t = 0.0
        self.max_hp = len(self.qs)
        self.hp = self.max_hp
        self.hearts = 3
        self.hit_t = 0.0
        self.hurt_t = 0.0
        self.banner_t = BANNER_TIME
        self.banner_text = BOSS_PHASES[0][1]
        self._layout()
        self.g.sfx.play("roar")

    # ------------------------------------------------------------- logic
    def choose(self, k):
        if self.banner_t > 0 or self.good_t > 0 or k in self.wrong:
            return
        correct = k == self.qs[self.i]["answer"]
        before = self.mistakes
        super().choose(k)
        if correct:
            self.hp -= 1
            self.hit_t = 0.7
            self.g.sfx.play("hit")
            self.msg = random.choice(["Direct hit!", "The Muddle King wobbles!", "Take that, muddle!", "Super smart!"])
        elif self.mistakes > before:
            self.hearts -= 1
            self.hurt_t = 0.6
            if self.hearts <= 0:
                self.hearts = 3
                self.msg = f"Don't give up, {HERO['name']}! Your friends cheer you on. Hearts are back!"
                self.msg_col, self.msg_t = (30, 150, 70), 3.5
                self.g.sfx.play("star")

    def event(self, e):
        if self.banner_t > 0:
            if e.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.banner_t = min(self.banner_t, 0.05)
            return
        super().event(e)

    def update(self, dt):
        self.t += dt
        self.hit_t = max(0.0, self.hit_t - dt)
        self.hurt_t = max(0.0, self.hurt_t - dt)
        if self.banner_t > 0:
            self.banner_t -= dt
            return
        prev = self.i
        super().update(dt)
        if not self.finished and self.i != prev and self.phase_of[self.i] != self.phase_of[prev]:
            self.banner_text = BOSS_PHASES[self.phase_of[self.i]][1]
            self.banner_t = BANNER_TIME
            self.g.sfx.play("roar")

    # ----------------------------------------------------------- drawing
    def draw(self, s):
        s.blit(bg_surface("hall"), (0, 0))
        phase = self.phase_of[min(self.i, len(self.qs) - 1)]
        # hero (left) and boss (right)
        shake = random.randint(-5, 5) if self.hurt_t > 0 else 0
        hero = character_preview(HERO["index"], 120)
        s.blit(hero, hero.get_rect(bottomleft=(50 + shake, 146)))
        bx = 810 + (random.randint(-6, 6) if self.hit_t > 0 else 0)
        mood = "hurt" if self.hit_t > 0 else "angry"
        draw_muddle_king(s, bx, 80, 150, self.t, mood)
        if self.hit_t > 0:
            for k in range(5):
                a = self.hit_t * 9 + k * 1.26
                draw_star(s, int(bx + math.cos(a) * 78), int(80 + math.sin(a) * 50), 10)
        # boss health bar
        text(s, "THE MUDDLE KING", 28, WHITE, (W // 2, 22), shadow=OUTLINE)
        bar = pygame.Rect(240, 40, 480, 28)
        pygame.draw.rect(s, (30, 14, 40), bar, border_radius=14)
        frac = max(0.0, self.hp / float(self.max_hp))
        if frac > 0:
            fill = pygame.Rect(bar.x + 3, bar.y + 3, int((bar.w - 6) * frac), bar.h - 6)
            pygame.draw.rect(s, (235, 70, 80), fill, border_radius=11)
            pygame.draw.rect(s, (255, 150, 150), (fill.x + 6, fill.y + 3, max(0, fill.w - 12), 4), border_radius=2)
        pygame.draw.rect(s, WHITE, bar, 3, border_radius=14)
        # hearts
        text(s, HERO["name"], 24, WHITE, (W // 2 - 90, 90), "midright", shadow=OUTLINE)
        for k in range(3):
            on = k < self.hearts
            draw_shape(s, "heart", (235, 60, 90) if on else (110, 100, 120), W // 2 - 66 + k * 34, 88, 12)
        text(s, f"Phase {phase + 1}/4: {BOSS_PHASES[phase][0]}", 26, YELLOW, (W // 2, 122), shadow=OUTLINE)
        if self.banner_t > 0:
            self.draw_banner(s)
            return
        self.draw_body(s)

    def draw_banner(self, s):
        box = pygame.Rect(130, 250, 700, 180)
        panel(s, box, (255, 247, 232), (150, 80, 210))
        tag = pygame.Rect(box.x + 24, box.y - 20, 210, 40)
        pygame.draw.rect(s, (150, 80, 210), tag, border_radius=12)
        pygame.draw.rect(s, OUTLINE, tag, 3, border_radius=12)
        text(s, "MUDDLE KING", 28, WHITE, tag.center, shadow=OUTLINE)
        for k, ln in enumerate(wrap(self.banner_text, F(40, False), box.w - 60)):
            text(s, ln, 40, NAVY, (box.centerx, box.y + 64 + k * 44), bold=False)
        text(s, "Get ready...", 28, (110, 100, 130), (box.centerx, box.bottom - 28), bold=False)
