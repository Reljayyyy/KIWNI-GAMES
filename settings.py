"""Constants, colours, level list (NODES) and story text."""
import os
import sys


W, H = 960, 640


TILE = 32


COLS, ROWS = W // TILE, H // TILE  # 30 x 20


FPS = 60


FROZEN = getattr(sys, "frozen", False)  # True inside the packaged .exe / app
# packaged: bundled files are unpacked to sys._MEIPASS; plain python: next to this file
HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


ASSETS = os.path.join(HERE, "assets")




def _save_dir():
    """Progress must live in a folder that survives restarts. In the packaged app that is the user's
    own app-data folder (the unpack folder is deleted every time the app closes)."""
    if not FROZEN:
        return os.path.dirname(os.path.abspath(__file__))
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, "KwinsGreatAdventure")


SAVE = os.path.join(_save_dir(), "save.json")


CREATOR = "Your Name Here"  # <- change this for the credits screen


GRASS = (76, 172, 58)


GRASS2 = (84, 180, 64)


PATH = (240, 206, 120)


PATH2 = (222, 184, 96)


DARK = (68, 40, 48)


ORANGE = (241, 170, 88)


BORDER = (176, 104, 72)


BTN = (70, 74, 120)


BTN_HI = (98, 102, 154)


BTN_EDGE = (80, 44, 52)


YELLOW = (255, 210, 60)


CREAM = (255, 247, 232)


NAVY = (24, 32, 64)


WHITE = (255, 255, 255)


COLS_NAMED = {
    "red": (230, 60, 60), "blue": (60, 110, 230), "green": (60, 170, 90),
    "yellow": (250, 200, 40), "purple": (150, 80, 200), "orange": (245, 140, 30),
    "pink": (250, 120, 170), "brown": (140, 90, 50),
}


NODES = [
    dict(id=1, name="Shape Road", skill="Shape recognition", pos=(5, 16), color=(255, 90, 140), dark=False),
    dict(id=2, name="Grandma's Missing Cat", skill="Color recognition", pos=(5, 9), color=(255, 200, 90), dark=True),
    dict(id=3, name="Number Forest", skill="Counting & sequences", pos=(11, 4), color=(72, 180, 110), dark=False),
    dict(id=4, name="Mixed-up Farm", skill="Sorting", pos=(13, 11), color=(90, 200, 220), dark=True),
    dict(id=5, name="Mysterious Bridge", skill="Directions", pos=(19, 14), color=(62, 110, 230), dark=False),
    dict(id=6, name="Pattern Garden", skill="Patterns", pos=(24, 16), color=(236, 232, 252), dark=True),
    dict(id=7, name="Clock Tower", skill="Sequencing & time", pos=(24, 9), color=(240, 70, 110), dark=False),
    dict(id=8, name="Great Adventure", skill="Combined skills", pos=(22, 3), color=(24, 32, 64), dark=False),
]


ROUTINE = ["Wake up", "Brush teeth", "Eat breakfast", "Go to school", "Eat lunch", "Do homework", "Eat dinner", "Go to sleep"]


GEM_NAMES = ["Shape Gem", "Color Gem", "Number Gem", "Sorting Gem", "Direction Gem", "Pattern Gem", "Time Gem"]
