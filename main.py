"""Kwin's Great Adventure - run this file:  python main.py"""
import sys

if sys.platform == "win32":
    # Stop Windows display scaling (125%, 150%...) from enlarging and cropping the game window.
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from game import Game


if __name__ == "__main__":
    Game().run()
