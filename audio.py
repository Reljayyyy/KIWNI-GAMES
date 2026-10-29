"""Sound: generated sound effects and looping background music (no sound files needed).

To use your own audio, drop files into  assets/sounds/  named:
  effects: click, good, bad, win, step, enter, star, pick, blip, hit, roar   (.wav or .ogg)
  music:   music_world, music_quiz, music_boss                                (.ogg, .wav or .mp3)
Anything you don't provide is generated automatically.
"""
import array
import math
import os

import pygame

from settings import ASSETS

RATE = 22050
SOUND_DIR = os.path.join(ASSETS, "sounds")
MASTER = 0.55  # overall headroom for the generated audio


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def _wave(kind, phase):
    x = phase % 1.0
    if kind == "sq":
        return 1.0 if x < 0.5 else -1.0
    if kind == "tri":
        return 4.0 * abs(x - 0.5) - 1.0
    return math.sin(2 * math.pi * x)


def _render(voices, seconds, rate, channels):
    """voices: list of (start_s, dur_s, freq_hz, volume, wave_kind) -> pygame Sound."""
    n = max(1, int(seconds * rate))
    mix = [0.0] * n
    for start, dur, freq, vol, kind in voices:
        s0, cnt = int(start * rate), max(1, int(dur * rate))
        att = max(1, int(0.006 * rate))
        for i in range(cnt):
            j = s0 + i
            if j >= n:
                break
            env = min(1.0, i / att) * (1.0 - i / cnt) ** 0.7
            mix[j] += vol * env * _wave(kind, i * freq / rate)
    buf = array.array("h")
    for v in mix:
        x = int(max(-1.0, min(1.0, v)) * 32767 * MASTER)
        for _ in range(channels):
            buf.append(x)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _sequence(notes):
    """notes: list of (freq_hz, seconds, wave_kind, volume) played one after another."""
    voices, t = [], 0.0
    for f, d, kind, vol in notes:
        voices.append((t, d, f, vol, kind))
        t += d
    return voices, t


def _line(notes, beat, vol, kind, gate=0.92):
    """notes: list of (midi or None, beats) -> voices, total_seconds."""
    voices, t = [], 0.0
    for m, b in notes:
        if m is not None:
            voices.append((t, b * beat * gate, hz(m), vol, kind))
        t += b * beat
    return voices, t


EFFECTS = {
    "click": [(660, 0.05, "sq", 0.45)],
    "pick": [(520, 0.045, "sq", 0.35)],
    "blip": [(780, 0.02, "sq", 0.18)],
    "step": [(120, 0.06, "sin", 0.9)],
    "good": [(523, 0.09, "tri", 0.8), (659, 0.09, "tri", 0.8), (784, 0.18, "tri", 0.8)],
    "bad": [(240, 0.12, "sq", 0.45), (180, 0.22, "sq", 0.45)],
    "enter": [(392, 0.07, "tri", 0.8), (523, 0.07, "tri", 0.8), (659, 0.07, "tri", 0.8), (784, 0.16, "tri", 0.8)],
    "star": [(880, 0.08, "sin", 0.7), (1320, 0.2, "sin", 0.7)],
    "hit": [(220, 0.05, "sq", 0.6), (140, 0.12, "sq", 0.6), (880, 0.08, "tri", 0.5)],
    "roar": [(110, 0.18, "sq", 0.5), (82, 0.3, "sq", 0.5), (65, 0.3, "sq", 0.5)],
    "win": [(523, 0.12, "tri", 0.8), (659, 0.12, "tri", 0.8), (784, 0.12, "tri", 0.8),
            (1046, 0.14, "tri", 0.8), (784, 0.1, "tri", 0.8), (1046, 0.5, "tri", 0.8)],
}


def _music_world(rate, ch):
    beat = 0.4  # cheerful village tune, 24 beats
    mel = [(76, 1), (79, 1), (76, 1), (72, 1), (74, 1), (76, 1), (74, 1), (67, 1),
           (76, 1), (79, 1), (81, 1), (79, 1), (76, 2), (74, 1), (72, 1),
           (69, 1), (72, 1), (74, 1), (76, 1), (79, 2), (76, 2)]
    bass = []
    for r in (48, 43, 48, 41, 45, 43):
        bass += [(r, 2), (r + 7, 2)]
    v1, total = _line(mel, beat, 0.45, "tri")
    v2, _ = _line(bass, beat, 0.32, "sq", 0.8)
    v2 = [(s, d, f, vol * 0.55, k) for s, d, f, vol, k in v2]
    return _render(v1 + v2, total, rate, ch)


def _music_quiz(rate, ch):
    beat = 0.5  # calm thinking music, 16 beats
    mel = [(72, 1), (76, 1), (79, 1), (76, 1), (74, 1), (77, 1), (81, 1), (77, 1),
           (76, 1), (79, 1), (84, 1), (79, 1), (74, 1), (71, 1), (72, 2)]
    bass = []
    for r in (48, 50, 48, 43):
        bass += [(r, 2), (r + 7, 2)]
    v1, total = _line(mel, beat, 0.4, "tri")
    v2, _ = _line(bass, beat, 0.3, "tri", 0.85)
    return _render(v1 + v2, max(total, 8.0), rate, ch)


def _music_boss(rate, ch):
    beat = 0.3  # driving boss-fight tune in A minor, 16 beats
    mel = [(69, 1), (72, 1), (76, 1), (72, 1), (69, 1), (72, 1), (77, 2),
           (76, 1), (74, 1), (72, 1), (74, 1), (76, 2), (69, 2)]
    bass = []
    for r in (45, 45, 41, 43):
        bass += [(r, 1)] * 4
    v1, total = _line(mel, beat, 0.38, "tri")
    v2, _ = _line(bass, beat, 0.2, "sq", 0.7)
    return _render(v1 + v2, total, rate, ch)


def _load_file(stem, exts):
    for ext in exts:
        p = os.path.join(SOUND_DIR, stem + ext)
        if os.path.exists(p):
            try:
                return pygame.mixer.Sound(p)
            except Exception:
                pass
    return None


class Sfx:
    def __init__(self):
        self.on = True          # sound effects
        self.music_on = True    # background music
        self.ok = False
        self.sounds = {}
        self.tracks = {}
        self.current = None
        self.ch = None
        try:
            self._init_mixer()
            rate, fmt, channels = pygame.mixer.get_init()
            if fmt != -16:
                raise RuntimeError("unsupported audio format")
            pygame.mixer.set_num_channels(12)
            pygame.mixer.set_reserved(1)       # channel 0 is kept for the music
            self.ch = pygame.mixer.Channel(0)
            for name, notes in EFFECTS.items():
                snd = _load_file(name, (".wav", ".ogg"))
                if snd is None:
                    voices, total = _sequence(notes)
                    snd = _render(voices, total + 0.02, rate, channels)
                snd.set_volume(0.7)
                self.sounds[name] = snd
            builders = {"world": _music_world, "quiz": _music_quiz, "boss": _music_boss}
            for name, build in builders.items():
                snd = _load_file("music_" + name, (".ogg", ".wav", ".mp3")) or build(rate, channels)
                snd.set_volume(0.3)
                self.tracks[name] = snd
            self.ok = True
        except Exception:
            self.ok = False

    @staticmethod
    def _init_mixer():
        info = pygame.mixer.get_init()
        if info and info[0] == RATE and info[1] == -16 and info[2] == 1:
            return
        if info:
            pygame.mixer.quit()
        try:
            pygame.mixer.init(RATE, -16, 1, 512, allowedchanges=0)
        except TypeError:
            pygame.mixer.init(RATE, -16, 1, 512)

    def play(self, name):
        if self.ok and self.on and name in self.sounds:
            self.sounds[name].play()

    def music(self, name):
        """Start the named track (looping), or silence with None. Cheap to call every frame."""
        if not self.ok:
            return
        if not name or not self.music_on or name not in self.tracks:
            if self.current is not None:
                self.ch.fadeout(300)
                self.current = None
            return
        if name == self.current and self.ch.get_busy():
            return
        self.ch.play(self.tracks[name], loops=-1, fade_ms=500)
        self.current = name
