"""Hero sprites (4 playable characters), optional assets/player.png loader, shared image cache (IMG)."""
import os
import pygame
from settings import ASSETS


IMG = {}  # scaled images of the chosen hero, filled in by set_hero()
HERO = {"index": 0, "name": "Kwin"}  # the currently chosen hero


KWIN_ROWS = [
    "....DDDDDDDD....",
    "...DHHhHHHHHD...",
    "..DHhHHHHHHHHD..",
    ".DHHHHHHHHHHHHD.",
    ".DHHSSSSSSSSHHD.",
    ".DHSSSSSSSSSSHD.",
    ".DHSESSSSSSESHD.",
    ".DHSESSSSSSESHD.",
    ".DHSSSSSRSSSSHD.",
    ".DHHSSSSSSSSHHD.",
    "..DHHSSSSSSHHD..",
    "...DDHSSSSHDD...",
    "....DDOOOODD....",
    "...DOOOOOOOOD...",
    "..DSOOOooOOOSD..",
    "..DSOOOOOOOOSD..",
    "..DSSBBBBBBSSD..",
    "...DDBBBbbBBDD..",
    "....DBBBBBBBD...",
    "....DDBBBBBDD...",
    ".....DSSDDSSD...",
    ".....DWWD.DWWD..",
    ".....DFFD.DFFD..",
    "....DFFFD.DFFFD.",
]


KWIN_PAL = {
    "D": (70, 36, 24), "H": (170, 84, 40), "h": (205, 115, 62), "S": (248, 198, 152),
    "E": (60, 30, 24), "R": (214, 110, 100), "O": (214, 92, 50), "o": (182, 70, 40),
    "B": (62, 80, 104), "b": (44, 58, 80), "W": (240, 230, 220), "F": (110, 60, 36),
}

# The four heroes you can choose from (same pixel body, different colours).
CHARACTERS = [
    dict(name="Kwin", tag="Curious and cheerful", color=(255, 160, 60), pal={}),
    dict(name="Kai", tag="Brave and friendly", color=(60, 170, 190),
         pal={"H": (38, 32, 58), "h": (70, 62, 100), "O": (40, 150, 170), "o": (30, 116, 134),
              "B": (60, 64, 86), "b": (44, 48, 66)}),
    dict(name="Mira", tag="Kind and creative", color=(190, 110, 220),
         pal={"H": (232, 188, 80), "h": (250, 220, 120), "O": (170, 90, 200), "o": (138, 66, 166),
              "B": (236, 120, 160), "b": (200, 90, 130)}),
    dict(name="Leo", tag="Bold and adventurous", color=(100, 180, 80),
         pal={"H": (58, 40, 30), "h": (92, 64, 46), "S": (224, 170, 120), "O": (90, 170, 70),
              "o": (66, 132, 52), "B": (190, 150, 90), "b": (156, 120, 70)}),
]

_PREVIEWS = {}


def kwin_surface(pal=None):
    colours = dict(KWIN_PAL)
    if pal:
        colours.update(pal)
    s = pygame.Surface((16, 24), pygame.SRCALPHA)
    for y, row in enumerate(KWIN_ROWS):
        for x, ch in enumerate(row):
            if ch in colours:
                s.set_at((x, y), colours[ch])
    return s


def load_player_image():
    """assets/player.png if you added one, otherwise the built-in pixel Kwin."""
    p = os.path.join(ASSETS, "player.png")
    if os.path.exists(p):
        try:
            img = pygame.image.load(p)
            if img.get_masks()[3] == 0:  # no alpha channel -> use corner colour as transparent
                img = img.convert()
                img.set_colorkey(img.get_at((0, 0)))
            else:
                img = img.convert_alpha()
            return img
        except Exception:
            pass
    return kwin_surface()


def scaled(img, height):
    r = img.get_bounding_rect()
    if r.w > 0 and r.h > 0:
        img = img.subsurface(r).copy()
    w = max(1, round(img.get_width() * height / img.get_height()))
    return pygame.transform.scale(img, (w, height))


def hero_image(index):
    if index == 0:
        return load_player_image()  # Kwin can be replaced by assets/player.png
    return kwin_surface(CHARACTERS[index]["pal"])


def character_preview(index, height=170):
    key = (index, height)
    if key not in _PREVIEWS:
        _PREVIEWS[key] = scaled(hero_image(index), height)
    return _PREVIEWS[key]


def set_hero(index):
    """Choose the hero used everywhere in the game (map, dialogue, menus)."""
    index = index if 0 <= index < len(CHARACTERS) else 0
    HERO["index"] = index
    HERO["name"] = CHARACTERS[index]["name"]
    base = hero_image(index)
    IMG["tiny"] = scaled(base, 36)
    IMG["player"] = scaled(base, 44)
    IMG["menu"] = scaled(base, 96)
    IMG["mid"] = scaled(base, 140)
    IMG["big"] = scaled(base, 190)
