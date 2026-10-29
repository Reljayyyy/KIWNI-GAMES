"""Main Game class: menus, hero choice, world walking, level flow, boss fight, cutscenes."""
import math
import os

import pygame

from settings import (
    ASSETS, BORDER, CREAM, CREATOR, DARK, FPS, GEM_NAMES, H, NAVY, NODES, TILE, W, WHITE, YELLOW,
)
from story import STORY, PROLOGUE, BOSS_INTRO, VICTORY, ENDING, tell
from sprites import IMG, HERO, CHARACTERS, character_preview, set_hero
from helpers import F, draw_gem_row, draw_shape, draw_stages, draw_star, fit_text, text, wrap, darker
from menu_ui import BTN_COLORS, OUTLINE, backdrop, draw_button, outlined, panel, title_block
from bossart import draw_muddle_king
from audio import Sfx
from storage import load_save, write_save
from world import World
from quiz import Quiz
from sorting import Sorting
from boss import BossBattle
from cutscene import Cutscene


class Game:
    MENU = [("Start the Game", "play"), ("About the Game", "book"), ("Settings", "gear"),
            ("Credits", "star"), ("Quit", "quit")]
    GO_RECT = pygame.Rect(350, 532, 260, 60)

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Kwin's Great Adventure")
        try:  # window icon (must be set before the window is created)
            pygame.display.set_icon(pygame.image.load(os.path.join(ASSETS, "icon.png")))
        except Exception:
            pass
        try:  # SCALED + RESIZABLE: the game fits any screen, can be maximised, and F11 = full screen
            self.screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
        except Exception:
            self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.sfx = Sfx()
        self.save = load_save()
        self.sfx.on = self.save["sound"]
        self.sfx.music_on = self.save["music"]
        self.hero_sel = self.save["hero"] if 0 <= self.save["hero"] < len(CHARACTERS) else 0
        set_hero(self.hero_sel)
        self.world = World()
        self.px, self.py = 6 * TILE, 18 * TILE + 20
        self.walk_t = 0.0
        self.state = "menu"
        self.sel = 0
        self.t = 0.0
        self.level = 1
        self.scene = None
        self.cut = None
        self.cut_done = None
        self.snapshot = None
        self.talk_i = 0
        self.talk_chars = 0.0
        self.stars_got = 0
        self.reset_confirm = False
        self.running = True
        self.near = None
        self.prev_near = None
        self.step_t = 0.0

    # progress ----------------------------------------------------------
    def done(self, lv):
        return str(lv) in self.save["done"]

    def unlocked(self, lv):
        return lv == 1 or self.done(lv - 1)

    def total_stars(self):
        return sum(self.save["done"].values())

    # flow --------------------------------------------------------------
    def go_world(self):
        self.state = "world"

    def start_cutscene(self, panels, bg, cast, done, music="quiz"):
        self.cut = Cutscene(self, panels, bg, cast, music)
        self.cut_done = done
        self.state = "cutscene"

    def confirm_hero(self):
        self.save["hero"] = self.hero_sel
        set_hero(self.hero_sel)
        self.sfx.play("enter")
        if not self.save["done"] and not self.save["prologue"]:
            self.save["prologue"] = True
            write_save(self.save)
            self.start_cutscene(PROLOGUE, "village", ("hero",), self.go_world, "world")
        else:
            write_save(self.save)
            self.go_world()

    def start_level(self, lv):
        self.level = lv
        self.snapshot = self.screen.copy()
        self.state = "intro"
        self.sfx.play("enter")

    def begin_dialogue(self):
        self.state, self.talk_i, self.talk_chars = "dialogue", 0, 0.0

    def begin_challenge(self):
        if self.level == 8:
            self.scene = BossBattle(self)
        elif self.level == 4:
            self.scene = Sorting(self, self.level)
        else:
            self.scene = Quiz(self, self.level)
        self.state = "challenge"

    def finish_level(self):
        m = self.scene.mistakes
        if self.level == 8:  # the boss fight is harder, so it is a little more forgiving
            stars = 3 if m <= 1 else (2 if m <= 4 else 1)
        else:
            stars = 3 if m == 0 else (2 if m <= 2 else 1)
        self.stars_got = stars
        old = self.save["done"].get(str(self.level), 0)
        self.save["done"][str(self.level)] = max(old, stars)
        write_save(self.save)
        self.sfx.play("win")
        self.t = 0.0
        if self.level == 8:
            self.save["ending"] = True
            write_save(self.save)
            self.start_cutscene(VICTORY, "hall", ("hero", "boss"), self.start_ending, "quiz")
        else:
            self.state = "result"

    def start_ending(self):
        self.start_cutscene(ENDING, "sunrise", ("hero", "boss"), self.go_world, "world")

    # events ------------------------------------------------------------
    def confirm_key(self, e):
        return e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e)

    def handle(self, e):
        if e.type == pygame.QUIT:
            self.running = False
            return
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
            try:
                pygame.display.toggle_fullscreen()
            except Exception:
                pass
            return
        st = self.state
        if st in ("menu", "settings"):
            self.menu_event(e)
        elif st == "choose":
            self.choose_event(e)
        elif st in ("about", "credits"):
            if e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.KEYDOWN:
                self.state = "menu"
                self.sfx.play("click")
        elif st == "world":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state, self.sel = "menu", 0
            elif self.confirm_key(e) and self.near and self.unlocked(self.near["id"]):
                self.start_level(self.near["id"])
        elif st == "intro":
            if self.confirm_key(e) or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                if self.level == 8:
                    self.start_cutscene(BOSS_INTRO, "hall", ("hero", "boss"), self.begin_challenge, "boss")
                else:
                    self.begin_dialogue()
        elif st == "dialogue":
            if self.confirm_key(e) or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                talk = STORY[self.level]["talk"]
                line = tell(talk[self.talk_i])
                if self.talk_chars < len(line):
                    self.talk_chars = len(line)
                elif self.talk_i + 1 < len(talk):
                    self.talk_i += 1
                    self.talk_chars = 0
                    self.sfx.play("click")
                else:
                    self.begin_challenge()
        elif st == "cutscene":
            if self.cut.event(e):
                self.cut_done()
        elif st == "challenge":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "world"
            else:
                self.scene.event(e)
        elif st == "result":
            if self.t > 0.6 and (self.confirm_key(e) or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1)):
                self.state = "world"
                self.sfx.play("click")

    # menu --------------------------------------------------------------
    def menu_items(self):
        if self.state == "menu":
            return self.MENU
        return [(f"Sound: {'ON' if self.save['sound'] else 'OFF'}", "sound"),
                (f"Music: {'ON' if self.save['music'] else 'OFF'}", "music"),
                (f"Hints: {'ON' if self.save['hints'] else 'OFF'}", "hint"),
                ("Press again to confirm reset" if self.reset_confirm else "Reset Progress", "reset"),
                ("Back", "back")]

    def button_rects(self):
        return [pygame.Rect(280, 240 + i * 66, 400, 54) for i in range(len(self.menu_items()))]

    def menu_event(self, e):
        n = len(self.menu_items())
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % n
                self.sfx.play("click")
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % n
                self.sfx.play("click")
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate(self.sel)
            elif e.key == pygame.K_ESCAPE and self.state == "settings":
                self.state, self.sel = "menu", 2
                self.reset_confirm = False
        elif e.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.button_rects()):
                if r.collidepoint(e.pos):
                    self.sel = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.button_rects()):
                if r.collidepoint(e.pos):
                    self.sel = i
                    self.activate(i)

    def activate(self, i):
        self.sfx.play("click")
        if self.state == "menu":
            if i == 0:
                self.hero_sel = self.save["hero"] if 0 <= self.save["hero"] < len(CHARACTERS) else 0
                self.state = "choose"
            elif i == 1:
                self.state = "about"
            elif i == 2:
                self.state, self.sel = "settings", 0
            elif i == 3:
                self.state = "credits"
            else:
                self.running = False
        else:
            if i == 0:
                self.save["sound"] = not self.save["sound"]
                self.sfx.on = self.save["sound"]
            elif i == 1:
                self.save["music"] = not self.save["music"]
                self.sfx.music_on = self.save["music"]
            elif i == 2:
                self.save["hints"] = not self.save["hints"]
            elif i == 3:
                if self.reset_confirm:
                    self.save["done"] = {}
                    self.save["prologue"] = False
                    self.save["ending"] = False
                    self.reset_confirm = False
                else:
                    self.reset_confirm = True
                    return
            else:
                self.state, self.sel = "menu", 2
                self.reset_confirm = False
            write_save(self.save)

    # hero choice ---------------------------------------------------------
    def card_rects(self):
        n = len(CHARACTERS)
        x0 = (W - (n * 200 + (n - 1) * 24)) // 2
        return [pygame.Rect(x0 + i * 224, 175, 200, 320) for i in range(n)]

    def choose_event(self, e):
        n = len(CHARACTERS)
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_a):
                self.hero_sel = (self.hero_sel - 1) % n
                self.sfx.play("pick")
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.hero_sel = (self.hero_sel + 1) % n
                self.sfx.play("pick")
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.confirm_hero()
            elif e.key == pygame.K_ESCAPE:
                self.state = "menu"
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.GO_RECT.collidepoint(e.pos):
                self.confirm_hero()
                return
            for i, r in enumerate(self.card_rects()):
                if r.collidepoint(e.pos):
                    if i == self.hero_sel:
                        self.confirm_hero()
                    else:
                        self.hero_sel = i
                        self.sfx.play("pick")

    # update ------------------------------------------------------------
    def music_track(self):
        st = self.state
        if st in ("intro", "dialogue", "challenge"):
            return "boss" if self.level == 8 else "quiz"
        if st == "cutscene":
            return self.cut.music
        if st == "result":
            return None  # the win jingle plays here
        return "world"

    def update(self, dt):
        self.t += dt
        self.sfx.music(self.music_track())
        st = self.state
        if st == "world":
            self.update_world(dt)
        elif st == "dialogue":
            line = tell(STORY[self.level]["talk"][self.talk_i])
            before = int(self.talk_chars)
            self.talk_chars += 45 * dt
            after = int(self.talk_chars)
            if after // 3 > before // 3 and after < len(line):
                self.sfx.play("blip")  # little talking sound while the hero speaks
        elif st == "cutscene":
            self.cut.update(dt)
        elif st == "challenge":
            self.scene.update(dt)
            if self.scene.finished:
                self.finish_level()

    def update_world(self, dt):
        k = pygame.key.get_pressed()
        vx = (k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])
        vy = (k[pygame.K_DOWN] or k[pygame.K_s]) - (k[pygame.K_UP] or k[pygame.K_w])
        if vx or vy:
            n = math.hypot(vx, vy)
            sp = 170 * dt
            for dx, dy in ((vx / n * sp, 0), (0, vy / n * sp)):
                nx, ny = self.px + dx, self.py + dy
                if not self.world.hits(pygame.Rect(int(nx) - 8, int(ny) - 10, 16, 10)):
                    self.px, self.py = nx, ny
            self.walk_t += dt
            self.step_t -= dt
            if self.step_t <= 0:
                self.sfx.play("step")
                self.step_t = 0.28
        else:
            self.step_t = 0.0
        self.near = None
        for n in NODES:
            c = World.node_center(n)
            if math.hypot(self.px - c[0], self.py - c[1]) < 46:
                self.near = n
        near_id = self.near["id"] if self.near else None
        if near_id != self.prev_near and near_id and self.unlocked(near_id):
            self.sfx.play("star")  # ding when you reach an open level
        self.prev_near = near_id

    # drawing -----------------------------------------------------------
    def draw(self):
        s = self.screen
        st = self.state
        if st in ("menu", "settings", "about", "credits"):
            self.draw_menu_family(s)
        elif st == "choose":
            self.draw_choose(s)
        elif st == "world":
            self.draw_world(s)
        elif st == "intro":
            self.draw_intro(s)
        elif st == "dialogue":
            self.draw_dialogue(s)
        elif st == "cutscene":
            self.cut.draw(s)
        elif st == "challenge":
            self.scene.draw(s)
        elif st == "result":
            self.draw_result(s)

    def draw_menu_family(self, s):
        backdrop(s, self.t)
        st = self.state
        if st in ("menu", "settings"):
            title_block(s, self.t)
            for i, ((lab, icon), r) in enumerate(zip(self.menu_items(), self.button_rects())):
                draw_button(s, r, lab, i == self.sel, BTN_COLORS[i % len(BTN_COLORS)], self.t, icon)
            outlined(s, "Arrows + Enter, or use the mouse", 24, WHITE, OUTLINE, (W // 2, 606), thick=2)
            bob = int(math.sin(self.t * 4) * 3)
            hero = IMG["big"]
            shadow = pygame.Surface((70, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
            s.blit(shadow, (150 - 35, 586))
            s.blit(hero, hero.get_rect(midbottom=(150, 594 + bob)))
            if st == "menu":
                draw_muddle_king(s, 815, 505, 150, self.t, "angry")
                if self.total_stars():
                    chip = pygame.Rect(W - 190, 14, 176, 42)
                    panel(s, chip)
                    draw_star(s, chip.x + 26, chip.centery, 14)
                    text(s, f"{self.total_stars()} / 24", 30, NAVY, (chip.x + 52, chip.centery), "midleft")
                    if self.save["ending"]:
                        outlined(s, "CHAMPION!", 24, YELLOW, OUTLINE, (chip.centerx, chip.bottom + 22), thick=2)
        else:
            if st == "about":
                title = "ABOUT THE GAME"
                lines = ["Kwin's Great Adventure is a 2D learning adventure",
                         "for young and early learners.",
                         "",
                         "The Muddle King mixed up the world and hid 7 Rainbow Gems.",
                         "Choose your hero, visit 8 worlds and win the gems back,",
                         "then face the Muddle King in the final boss battle!",
                         "",
                         "You will practice shapes, colors, numbers, sorting,",
                         "directions, patterns and telling time.",
                         "",
                         "Walk: arrows or WASD     Talk / Enter: SPACE",
                         "Answer: mouse or keys 1-4     Menu: ESC     Full screen: F11"]
            else:
                title = "CREDITS"
                lines = ["Game design and story:", "Kwin's Great Adventure proposal", "",
                         "Programming: Python + pygame",
                         "Pixel art and music: drawn and generated in code",
                         "(add your own assets/player.png and assets/sounds)", "",
                         f"Made by: {"QUNIE BAGACAY"}", "", "Thank you for playing!"]
            outlined(s, title, 70, YELLOW, OUTLINE, (W // 2, 66), thick=4)
            pr = pygame.Rect(90, 125, 780, 440)
            panel(s, pr)
            for i, line in enumerate(lines):
                fit_text(s, line, 28, 740, NAVY, (W // 2, 160 + i * 34))
            outlined(s, "Press any key to go back", 26, WHITE, OUTLINE, (W // 2, 604), thick=2)

    def draw_choose(self, s):
        backdrop(s, self.t)
        outlined(s, "CHOOSE YOUR HERO", 76, YELLOW, OUTLINE, (W // 2, 62), thick=4)
        outlined(s, "Who will go on the Great Adventure?", 30, WHITE, OUTLINE, (W // 2, 118), thick=2)
        bob = int(abs(math.sin(self.t * 5)) * 4)
        for i, r in enumerate(self.card_rects()):
            ch = CHARACTERS[i]
            sel = i == self.hero_sel
            rr = r.move(0, -12 - bob) if sel else r
            pygame.draw.rect(s, darker(ch["color"], 100), rr.move(0, 8), border_radius=22)
            pygame.draw.rect(s, CREAM, rr, border_radius=22)
            pygame.draw.rect(s, ch["color"] if sel else OUTLINE, rr, 8 if sel else 4, border_radius=22)
            band = pygame.Rect(rr.x + 14, rr.y + 14, rr.w - 28, 190)
            tint = tuple(int(c * 0.35 + 255 * 0.65) for c in ch["color"])
            pygame.draw.rect(s, tint, band, border_radius=14)
            img = character_preview(i, 170)
            s.blit(img, img.get_rect(midbottom=(rr.centerx, band.bottom - 8 - (bob if sel else 0))))
            text(s, ch["name"], 40, NAVY, (rr.centerx, rr.y + 232))
            for k, ln in enumerate(wrap(ch["tag"], F(22, False), rr.w - 24)):
                text(s, ln, 22, (110, 100, 130), (rr.centerx, rr.y + 268 + k * 24), bold=False)
            if sel:
                for k in range(3):
                    a = self.t * 2 + k * 2.1
                    draw_star(s, int(rr.centerx + math.cos(a) * 95), int(rr.y + 100 + math.sin(a) * 60), 8)
        draw_button(s, self.GO_RECT, "Let's go!", True, BTN_COLORS[0], self.t, "play")
        outlined(s, "Left / Right to choose     Enter to start     Esc to go back", 22, WHITE, OUTLINE,
                 (W // 2, 614), thick=2)

    def draw_world(self, s):
        w = self.world
        s.blit(w.ground, (0, 0))
        for n in NODES:
            cx, cy = World.node_center(n)
            lv = n["id"]
            if self.done(lv):
                pygame.draw.circle(s, (60, 180, 90), (cx, cy), 20)
                pygame.draw.circle(s, WHITE, (cx, cy), 20, 3)
                text(s, str(lv), 26, WHITE, (cx, cy))
                for k in range(self.save["done"][str(lv)]):
                    draw_star(s, cx - 14 + k * 14, cy - 30, 7)
            elif self.unlocked(lv):
                r = 20 + int(math.sin(self.t * 5) * 3)
                pygame.draw.circle(s, YELLOW, (cx, cy), r)
                pygame.draw.circle(s, DARK, (cx, cy), r, 3)
                text(s, str(lv), 26, DARK, (cx, cy))
            else:
                pygame.draw.circle(s, (150, 150, 160), (cx, cy), 18)
                pygame.draw.circle(s, (100, 100, 110), (cx, cy), 18, 3)
                text(s, str(lv), 24, (90, 90, 100), (cx, cy))
        pimg = IMG["player"]
        drawn = False
        for yb, surf, pos in w.objs:
            if not drawn and yb > self.py:
                self.draw_player(s, pimg)
                drawn = True
            s.blit(surf, pos)
        if not drawn:
            self.draw_player(s, pimg)
        # HUD
        hud = pygame.Rect(10, 8, 300, 62)
        pygame.draw.rect(s, (255, 247, 232), hud, border_radius=10)
        pygame.draw.rect(s, BORDER, hud, 3, border_radius=10)
        text(s, "KWIN'S GREAT ADVENTURE", 22, NAVY, (hud.x + 12, hud.y + 18), "midleft")
        text(s, f"Stars {self.total_stars()}/24", 24, DARK, (hud.x + 12, hud.y + 44), "midleft")
        draw_gem_row(s, hud.x + 222, hud.y + 44, [self.done(i) for i in range(1, 8)], r=7, gap=15)
        nxt = next((n for n in NODES if not self.done(n["id"])), None)
        if nxt:
            text(s, f"Next: {nxt['id']}. {nxt['name']}", 24, DARK, (W - 14, 20), "midright", shadow=(255, 255, 255))
        text(s, "Arrows/WASD walk   SPACE enter   ESC menu", 22, WHITE, (W // 2, H - 14), shadow=DARK)
        if self.near:
            n = self.near
            ok = self.unlocked(n["id"])
            box = pygame.Rect(0, 0, 420, 70)
            box.midtop = (W // 2, 78)
            pygame.draw.rect(s, CREAM, box, border_radius=12)
            pygame.draw.rect(s, n["color"] if ok else (150, 150, 160), box, 5, border_radius=12)
            title = f"{n['id']}. {n['name']}" + ("  (FINAL BOSS)" if n["id"] == 8 else "")
            text(s, title, 30, NAVY, (box.centerx, box.y + 22))
            text(s, (n["skill"] + "   -   press SPACE") if ok else "Locked: finish the previous world first",
                 22, (100, 100, 115), (box.centerx, box.y + 49), bold=False)

    def draw_player(self, s, img):
        keys = pygame.key.get_pressed()
        moving = any(keys[k] for k in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                                       pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s))
        bob = int(abs(math.sin(self.walk_t * 12)) * 3) if moving else 0
        shadow = pygame.Surface((24, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
        s.blit(shadow, (self.px - 12, self.py - 5))
        s.blit(img, img.get_rect(midbottom=(int(self.px), int(self.py) - bob)))

    def dim_snapshot(self, s, alpha=140):
        s.blit(self.snapshot, (0, 0))
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, alpha))
        s.blit(ov, (0, 0))

    def draw_intro(self, s):
        self.dim_snapshot(s)
        draw_stages(s, 0, 30)
        node = NODES[self.level - 1]
        card = pygame.Rect(130, 100, 700, 450)
        pygame.draw.rect(s, node["color"], card, border_radius=20)
        pygame.draw.rect(s, WHITE, card, 6, border_radius=20)
        fg = NAVY if node["dark"] else WHITE
        label = f"LEVEL 0{self.level}" + ("  -  FINAL BOSS" if self.level == 8 else "")
        text(s, label, 34, fg, (card.centerx, card.y + 50))
        fit_text(s, node["name"].upper(), 66, 620, fg, (card.centerx, card.y + 115))
        text(s, node["skill"], 32, fg, (card.centerx, card.y + 170), bold=False)
        for i, line in enumerate(wrap(tell(STORY[self.level]["intro"]), F(34), 600)):
            text(s, line, 34, fg, (card.centerx, card.y + 235 + i * 38), bold=False)
        if int(self.t * 2) % 2 == 0:
            text(s, "Press SPACE to continue", 28, fg, (card.centerx, card.bottom - 36))

    def draw_dialogue(self, s):
        self.dim_snapshot(s)
        draw_stages(s, 1, 30)
        box = pygame.Rect(40, 395, 880, 215)
        pygame.draw.rect(s, CREAM, box, border_radius=16)
        pygame.draw.rect(s, BORDER, box, 6, border_radius=16)
        s.blit(IMG["big"], IMG["big"].get_rect(bottomleft=(70, box.bottom - 10)))
        name = pygame.Rect(box.x + 170, box.y - 18, max(110, F(28).size(HERO["name"].upper())[0] + 40), 36)
        pygame.draw.rect(s, (255, 200, 80), name, border_radius=10)
        pygame.draw.rect(s, BORDER, name, 3, border_radius=10)
        text(s, HERO["name"].upper(), 28, NAVY, name.center)
        line = tell(STORY[self.level]["talk"][self.talk_i])
        shown = line[:int(self.talk_chars)]
        for i, ln in enumerate(wrap(shown, F(40), 620)):
            text(s, ln, 40, NAVY, (box.x + 190, box.y + 70 + i * 44), "midleft", bold=False)
        if self.talk_chars >= len(line) and int(self.t * 2) % 2 == 0:
            pygame.draw.polygon(s, DARK, [(box.right - 50, box.bottom - 40), (box.right - 30, box.bottom - 40),
                                          (box.right - 40, box.bottom - 26)])

    def draw_result(self, s):
        node = NODES[self.level - 1]
        s.fill(node["color"])
        fg = NAVY if node["dark"] else WHITE
        draw_stages(s, 4, 30)
        fit_text(s, "LEVEL COMPLETE!", 80, 860, fg, (W // 2, 140))
        text(s, node["name"], 38, fg, (W // 2, 195), bold=False)
        for k in range(3):
            pop = min(1.0, max(0.0, (self.t - 0.2 - k * 0.3) * 4))
            if pop > 0:
                draw_star(s, W // 2 + (k - 1) * 120, 290, int(46 * pop), k < self.stars_got)
        # the Rainbow Gem you just won
        gp = min(1.0, max(0.0, (self.t - 1.1) * 3))
        if gp > 0 and self.level <= 7:
            gx, gy = W // 2 + 290, 282
            draw_shape(s, "diamond", (255, 255, 255), gx, gy, int(40 * gp) + 4)
            draw_shape(s, "diamond", node["color"], gx, gy, int(34 * gp))
            text(s, GEM_NAMES[self.level - 1], 24, fg, (gx, gy + 56))
        msg = {3: "Perfect! No mistakes!", 2: "Great work! Almost perfect!", 1: "Good try! Practice makes perfect!"}[self.stars_got]
        text(s, msg, 40, fg, (W // 2, 375))
        s.blit(IMG["mid"], IMG["mid"].get_rect(bottomleft=(120, 590)))
        box = pygame.Rect(280, 410, 560, 120)
        pygame.draw.rect(s, CREAM, box, border_radius=14)
        pygame.draw.rect(s, WHITE, box, 4, border_radius=14)
        for i, ln in enumerate(wrap(STORY[self.level]["win"], F(32), 520)):
            text(s, ln, 32, NAVY, (box.centerx, box.y + 32 + i * 34), bold=False)
        if self.level < 8:
            nn = NODES[self.level]
            text(s, f"Next stop: {nn['name']}", 30, fg, (W // 2 + 60, 560))
        if self.t > 0.6 and int(self.t * 2) % 2 == 0:
            text(s, "Press SPACE to continue", 26, fg, (W // 2 + 60, 600))

    # main loop ---------------------------------------------------------
    def frame(self, dt):
        self.update(dt)
        self.draw()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for e in pygame.event.get():
                self.handle(e)
            self.frame(dt)
            pygame.display.flip()
        pygame.quit()
