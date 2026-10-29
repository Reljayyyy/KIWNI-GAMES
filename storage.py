"""Save file (progress, sound, music and hint settings)."""
import json
import os
from settings import SAVE


def load_save():
    d = {"done": {}, "sound": True, "music": True, "hints": True,
         "hero": 0, "prologue": False, "ending": False}
    try:
        with open(SAVE) as f:
            d.update(json.load(f))
    except Exception:
        pass
    return d


def write_save(d):
    try:
        os.makedirs(os.path.dirname(SAVE), exist_ok=True)
        with open(SAVE, "w") as f:
            json.dump(d, f)
    except OSError:
        pass
