"""Question generators for the multiple-choice levels."""
import random
import pygame
from settings import COLS_NAMED, NAVY, ROUTINE
from sprites import IMG
from helpers import (
    darker,
    draw_apple,
    draw_arrow,
    draw_clock,
    draw_flower,
    draw_shape,
    text,
)


SHAPES = ["circle", "square", "triangle", "rectangle", "star", "diamond", "heart"]


def num_options(ans, lo=0, hi=20):
    pool = {ans}
    for d in (1, -1, 2, -2, 3, -3):
        if lo <= ans + d <= hi and len(pool) < 4:
            pool.add(ans + d)
    while len(pool) < 4:
        pool.add(random.randint(lo, hi))
    opts = list(pool)
    random.shuffle(opts)
    return [str(o) for o in opts], opts.index(ans)


def q_shape():
    names = random.sample(SHAPES, 4)
    cols = random.sample(list(COLS_NAMED.values()), 4)
    opts = [(lambda s, r, n=n, c=c: draw_shape(s, n, c, r.centerx, r.centery, 34)) for n, c in zip(names, cols)]
    props = [("Which shape is round with no corners?", "circle"),
             ("Which shape has 3 sides?", "triangle"),
             ("Which shape has 5 points?", "star")]
    random.shuffle(props)
    for prompt, tgt in props:
        if random.random() < 0.5 and tgt in names:
            return dict(prompt=prompt, visual=None, options=opts, answer=names.index(tgt),
                        hint="Look closely at the sides and corners.")
    tgt = random.choice(names)
    return dict(prompt=f"Hop on the {tgt.upper()} stone!", visual=None, options=opts,
                answer=names.index(tgt), hint="Look at the outline of each stone.")


def q_color():
    names = random.sample(list(COLS_NAMED), 4)
    tgt = random.choice(names)
    if random.random() < 0.5:
        opts = [(lambda s, r, n=n: draw_flower(s, COLS_NAMED[n], r.centerx, r.centery - 12, 24)) for n in names]
        return dict(prompt=f"Find the {tgt.upper()} flower!", visual=None, options=opts,
                    answer=names.index(tgt), hint="Mittens hides next to the right color.")

    def vis(s, r, c=COLS_NAMED[tgt]):
        pygame.draw.circle(s, c, r.center, 58)
        pygame.draw.circle(s, darker(c), r.center, 58, 4)
    return dict(prompt="What color is this?", visual=vis, options=[n.upper() for n in names],
                answer=names.index(tgt), hint="Think of things that are this color.")


def q_count():
    if random.random() < 0.6:
        n = random.randint(1, 9)

        def vis(s, r, n=n):
            cols = min(n, 5)
            rows = 1 if n <= 5 else 2
            for i in range(n):
                row, col = divmod(i, 5)
                cnt = cols if row == 0 else n - 5
                x = r.centerx + (col - (cnt - 1) / 2) * 62
                y = r.centery + (row - (rows - 1) / 2) * 62
                draw_apple(s, int(x), int(y), 22, COLS_NAMED["red"])
        opts, ans = num_options(n, 1, 10)
        return dict(prompt="How many apples can you count?", visual=vis, options=opts, answer=ans,
                    hint="Touch each apple once and count out loud.", sig=("count", n))
    start, step = random.randint(1, 8), random.choice([1, 2, 3, 5])
    seq = [start + step * k for k in range(4)]
    nxt = start + step * 4

    def vis(s, r, seq=seq):
        text(s, ",  ".join(map(str, seq)) + ",  ?", 76, NAVY, r.center)
    opts, ans = num_options(nxt, 1, 30)
    return dict(prompt="What number comes next?", visual=vis, options=opts, answer=ans,
                hint="Each number goes up by the same amount.", sig=("seq", tuple(seq)))


def q_direction():
    if random.random() < 0.5:
        d = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        names = {(-1, 0): "LEFT", (1, 0): "RIGHT", (0, -1): "UP", (0, 1): "DOWN"}

        def vis(s, r, d=d):
            cell = 44
            cx, cy = r.center
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    rc = pygame.Rect(cx + ax * cell - cell // 2, cy + ay * cell - cell // 2, cell, cell)
                    pygame.draw.rect(s, (236, 248, 232), rc)
                    pygame.draw.rect(s, (160, 190, 150), rc, 2)
            s.blit(IMG["tiny"], IMG["tiny"].get_rect(midbottom=(cx, cy + 20)))
            draw_flower(s, COLS_NAMED["pink"], cx + d[0] * cell, cy + d[1] * cell - 4, 9)
        order = list(names)
        random.shuffle(order)
        return dict(prompt="Where is the flower? Kwin is in the middle.", visual=vis,
                    options=[names[o] for o in order], answer=order.index(d),
                    hint="Left is the side of your left hand.")
    d = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
    names = {(-1, 0): "LEFT", (1, 0): "RIGHT", (0, -1): "UP", (0, 1): "DOWN"}
    order = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    random.shuffle(order)
    opts = [(lambda s, r, o=o: draw_arrow(s, o, r.centerx, r.centery, 36)) for o in order]
    return dict(prompt=f"Which arrow points {names[d]}?", visual=None, options=opts,
                answer=order.index(d), hint="Follow the tip of the arrow.")


def q_pattern():
    pool = [("circle", COLS_NAMED["red"]), ("circle", COLS_NAMED["blue"]), ("square", COLS_NAMED["yellow"]),
            ("triangle", COLS_NAMED["green"]), ("star", COLS_NAMED["purple"]), ("heart", COLS_NAMED["pink"])]
    A, B, C = random.sample(pool, 3)
    base = random.choice([[A, B], [A, A, B], [A, B, B], [A, B, C]])
    seq = [base[i % len(base)] for i in range(6)]
    ans_item = base[6 % len(base)]
    others = [p for p in pool if p != ans_item]
    items = [ans_item] + random.sample(others, 3)
    random.shuffle(items)

    def vis(s, r, seq=seq):
        x0 = r.centerx - 3.5 * 66
        for i, (n, c) in enumerate(seq):
            draw_shape(s, n, c, int(x0 + i * 66), r.centery, 22)
        q = pygame.Rect(int(x0 + 6 * 66) - 24, r.centery - 24, 48, 48)
        pygame.draw.rect(s, (235, 235, 245), q, border_radius=8)
        pygame.draw.rect(s, (150, 150, 180), q, 3, border_radius=8)
        text(s, "?", 44, NAVY, q.center)
    opts = [(lambda s, r, it=it: draw_shape(s, it[0], it[1], r.centerx, r.centery, 34)) for it in items]
    return dict(prompt="What comes next in the pattern?", visual=vis, options=opts,
                answer=items.index(ans_item), hint="Find the part that repeats.",
                sig=("pattern", tuple(seq), ans_item))


def q_clock():
    if random.random() < 0.6:
        h, m = random.randint(1, 12), random.choice([0, 30])
        label = lambda hh, mm: f"{hh}:{mm:02d}"
        right = label(h, m)
        wrong = set()
        while len(wrong) < 3:
            hh = random.randint(1, 12)
            mm = random.choice([0, 30])
            if label(hh, mm) != right:
                wrong.add(label(hh, mm))
        opts = [right] + list(wrong)
        random.shuffle(opts)

        def vis(s, r, h=h, m=m):
            draw_clock(s, r.centerx, r.centery, 64, h, m)
        return dict(prompt="What time is it?", visual=vis, options=opts, answer=opts.index(right),
                    hint="The short hand shows the hour. The long hand shows the minutes.",
                    sig=("time", h, m))
    i = random.randint(1, len(ROUTINE) - 2)
    shown = ROUTINE[max(0, i - 1):i + 1]
    right = ROUTINE[i + 1]
    wrong = random.sample([r for r in ROUTINE if r != right and r not in shown], 3)
    opts = [right] + wrong
    random.shuffle(opts)

    def vis(s, r, shown=shown):
        text(s, "  >  ".join(shown) + "  >  ?", 38, NAVY, r.center)
    return dict(prompt="What happens next in Kwin's day?", visual=vis, options=opts,
                answer=opts.index(right), hint="Think about what you do first, then next.",
                sig=("routine", tuple(shown)))


GENERATORS = {1: q_shape, 2: q_color, 3: q_count, 5: q_direction, 6: q_pattern, 7: q_clock}


MIXED = [q_shape, q_color, q_count, q_direction, q_pattern, q_clock]


def make_questions(level):
    n = 6 if level == 8 else 5
    qs, seen = [], set()
    tries = 0
    while len(qs) < n and tries < 80:
        tries += 1
        gen = random.choice(MIXED) if level == 8 else GENERATORS[level]
        if level == 8 and len(qs) >= 1 and gen == qs[-1].get("gen"):
            continue
        q = gen()
        key = q.get("sig") or (q["prompt"], q["answer"], len(q["options"]))
        if key in seen:
            continue
        seen.add(key)
        q["gen"] = gen
        qs.append(q)
    return qs
