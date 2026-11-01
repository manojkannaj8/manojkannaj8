"""Shared toolkit for the profile's SVG assets.

Every word in the artwork is converted to outlines with fontTools, so the
SVGs render identically on GitHub (images there cannot load web fonts).
Fonts are static instances of Archivo and Martian Mono (SIL OFL 1.1).
"""
from __future__ import annotations

import math
import random
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"

# ── Earth-MKJ palette ────────────────────────────────────────────────
# Night-city ink, a spray-can red, and the two misregistration inks
# (cyan + magenta) that fringe everything in a mis-printed comic.
INK = "#07060D"
NIGHT = "#130A2E"
DEEP = "#22104F"
VIOLET = "#5B2BE0"
RED = "#FF2A4D"
CYAN = "#1FE3F0"
MAGENTA = "#FF3DA8"
YELLOW = "#FFE14A"
PAPER = "#F6F0E4"
MUTED = "#A79CCB"

DISPLAY = "Archivo-ExpandedBlack.ttf"
CONDENSED = "Archivo-CondensedBold.ttf"
BODY = "Archivo-SemiBold.ttf"
MONO = "MartianMono-Medium.ttf"

# Motion: the film animates "on twos", so loops jump between poses
# with steps() rather than easing. Reduced-motion users get stills.
BASE_CSS = """
@media (prefers-reduced-motion: reduce){*{animation:none!important}}
"""


def num(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


@lru_cache(maxsize=None)
def _font(name: str) -> TTFont:
    return TTFont(FONTS / name)


def measure(text: str, font: str, size: float, ls: float = 0) -> float:
    f = _font(font)
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    scale = size / f["head"].unitsPerEm
    w = sum(hmtx[cmap.get(ord(c), cmap[ord("?")])][0] for c in text) * scale
    return w + ls * max(len(text) - 1, 0)


def text_d(text: str, font: str, size: float, x: float, y: float,
           anchor: str = "start", ls: float = 0) -> str:
    """Outline `text` as a single path `d`, baseline at y."""
    f = _font(font)
    cmap, hmtx, gs = f.getBestCmap(), f["hmtx"], f.getGlyphSet()
    scale = size / f["head"].unitsPerEm
    width = measure(text, font, size, ls)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    pen = SVGPathPen(gs, ntos=num)
    cursor = x
    for c in text:
        g = cmap.get(ord(c), cmap[ord("?")])
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, y)))
        cursor += hmtx[g][0] * scale + ls
    return pen.getCommands()


# Glyphs are defined once per document (in font units) and placed with <use>,
# which keeps paragraphs of outlined text small. svg_doc() flushes the registry.
_GLYPHS: dict[str, str] = {}
_RUNS: list[str] = []
_FONT_KEY = {DISPLAY: "a", CONDENSED: "c", BODY: "b", MONO: "m"}


def _glyph(font: str, g: str) -> str:
    gid = f"{_FONT_KEY[font]}{_font(font).getGlyphID(g)}"
    if gid not in _GLYPHS:
        pen = SVGPathPen(_font(font).getGlyphSet(), ntos=lambda v: str(round(v)))
        _font(font).getGlyphSet()[g].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
        _GLYPHS[gid] = pen.getCommands()
    return gid


def _run(t: str, font: str, size: float, x: float, y: float, anchor: str, ls: float) -> str:
    f = _font(font)
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    upm = f["head"].unitsPerEm
    scale = size / upm
    width = measure(t, font, size, ls)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    uses, cursor = [], 0.0
    for c in t:
        if ord(c) not in cmap:
            print(f"  ! {font} has no glyph for {c!r} in {t!r}")
        g = cmap.get(ord(c), cmap[ord("?")])
        if c != " ":
            gid = _glyph(font, g)
            uses.append(f'<use href="#{gid}" x="{round(cursor)}"/>' if cursor else f'<use href="#{gid}"/>')
        cursor += hmtx[g][0] + ls / scale
    return f'transform="translate({num(x)} {num(y)}) scale({scale:.4g})"', "".join(uses)


def text(t: str, font: str, size: float, x: float, y: float, fill: str = PAPER,
         anchor: str = "start", ls: float = 0, extra: str = "") -> str:
    tr, uses = _run(t, font, size, x, y, anchor, ls)
    return f'<g fill="{fill}" {tr}{extra}>{uses}</g>'


def misprint(t: str, font: str, size: float, x: float, y: float, fill: str = PAPER,
             anchor: str = "start", ls: float = 0, off: float = 3, cls: str = "") -> str:
    """Text with cyan / red registration fringes, like an off-register print."""
    tr, uses = _run(t, font, size, x, y, anchor, ls)
    rid = f"r{len(_RUNS)}"
    _RUNS.append(f'<g id="{rid}" {tr}>{uses}</g>')
    c = f' class="{cls}"' if cls else ""
    fringe = (f'<use href="#{rid}" fill="{CYAN}" transform="translate({num(-off)} {num(off * .4)})"/>'
              f'<use href="#{rid}" fill="{RED}" transform="translate({num(off)} {num(-off * .4)})"/>') if off else ""
    return f'<g{c}>{fringe}<use href="#{rid}" fill="{fill}"/></g>'


def wrap(t: str, font: str, size: float, max_w: float) -> list[str]:
    lines, cur = [], ""
    for word in t.split():
        trial = f"{cur} {word}".strip()
        if cur and measure(trial, font, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur] if cur else lines


def paragraph(t: str, font: str, size: float, x: float, y: float, max_w: float,
              lh: float, fill: str = PAPER) -> tuple[str, float]:
    out = []
    lines = wrap(t, font, size, max_w)
    for i, line in enumerate(lines):
        out.append(text(line, font, size, x, y + i * lh, fill))
    return "".join(out), y + (len(lines) - 1) * lh


def chip(label: str, x: float, y: float, size: float = 15, kind: str = "solid",
         color: str = CYAN, fg: str = INK, pad: float = 10, h: float = 30) -> tuple[str, float]:
    """A skill chip. kind: solid (shipped) · half (work/research) · outline (familiar)."""
    w = measure(label, MONO, size) + pad * 2
    r = f'x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{h}"'
    ty = y + h / 2 + size * .36
    if kind == "solid":
        body = f'<rect {r} fill="{color}"/>' + text(label, MONO, size, x + pad, ty, fg)
    elif kind == "half":
        body = (f'<rect {r} fill="none" stroke="{color}" stroke-width="2"/>'
                f'<path d="M{num(x)} {num(y + h)}h{num(w)}L{num(x + w)} {num(y + h - 6)}H{num(x)}z" fill="{color}"/>'
                + text(label, MONO, size, x + pad, ty, PAPER))
    else:
        body = (f'<rect {r} fill="none" stroke="{color}" stroke-width="1.5" stroke-dasharray="4 3" opacity=".8"/>'
                + text(label, MONO, size, x + pad, ty, MUTED))
    return body, w


def dots_pattern(pid: str, color: str = PAPER, step: float = 8, r: float = 1.6, angle: float = 0) -> str:
    rot = f' patternTransform="rotate({angle})"' if angle else ""
    return (f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse"{rot}>'
            f'<circle cx="{step / 2}" cy="{step / 2}" r="{r}" fill="{color}"/></pattern>')


def hatch_pattern(pid: str, color: str = PAPER, step: float = 7, w: float = 1.2, angle: float = 45) -> str:
    return (f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse" patternTransform="rotate({angle})">'
            f'<line x1="0" y1="0" x2="0" y2="{step}" stroke="{color}" stroke-width="{w}"/></pattern>')


def halftone_field(x0: float, y0: float, w: float, h: float, step: float, color: str,
                   rmax: float, falloff, seed: int = 1) -> str:
    """Real halftone: dot radius follows `falloff(u, v)` in 0..1 (u, v normalised).

    Dots are zero-length round-capped strokes, bucketed into a few sizes, which
    keeps thousands of dots down to a few kilobytes.
    """
    buckets: dict[int, list[str]] = {}
    levels = 6
    rows = int(h // step) + 1
    cols = int(w // step) + 1
    for j in range(rows):
        for i in range(cols):
            cx = x0 + i * step + (step / 2 if j % 2 else 0)
            cy = y0 + j * step
            k = round(levels * min(1, falloff((cx - x0) / w, (cy - y0) / h)))
            if k > 0:
                buckets.setdefault(k, []).append(f"M{num(cx)} {num(cy)}h0")
    return "".join(f'<path d="{"".join(v)}" stroke="{color}" stroke-width="{num(2 * rmax * k / levels)}" '
                   f'stroke-linecap="round"/>' for k, v in sorted(buckets.items()))


def splatter(cx: float, cy: float, spread: float, color: str, seed: int, n: int = 60,
             drips: int = 4, rmax: float = 9) -> str:
    """Spray-paint burst: a dense core, flecks thrown outward and a few drips."""
    rnd = random.Random(seed)
    parts = []
    for _ in range(n):
        a = rnd.random() * math.tau
        d = spread * (rnd.random() ** 1.8)
        r = max(.6, rmax * (1 - d / spread) * rnd.uniform(.25, 1))
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d * .7
        parts.append(f"M{num(x - r)} {num(y)}a{num(r)} {num(r)} 0 1 0 {num(2 * r)} 0a{num(r)} {num(r)} 0 1 0 {num(-2 * r)} 0")
    for _ in range(drips):
        x = cx + rnd.uniform(-spread * .45, spread * .45)
        y = cy + rnd.uniform(-4, 6)
        L = rnd.uniform(18, 60)
        w = rnd.uniform(2, 4.2)
        parts.append(f"M{num(x - w / 2)} {num(y)}v{num(L)}a{num(w / 2)} {num(w / 2)} 0 0 0 {num(w)} 0v{num(-L)}z")
    return f'<path d="{"".join(parts)}" fill="{color}"/>'


def web(cx: float, cy: float, radius: float, spokes: int, rings: int, color: str,
        start: float = 0, sweep: float = 360, sag: float = .12, width: float = 1.2,
        opacity: float = 1) -> tuple[str, list[tuple[float, float]]]:
    """A spider web; returns the svg and its ring/spoke junctions (graph nodes)."""
    angs = [math.radians(start + sweep * i / (spokes - (0 if sweep == 360 else 1))) for i in range(spokes)]
    d, nodes = [], []
    for a in angs:
        d.append(f"M{num(cx)} {num(cy)}L{num(cx + math.cos(a) * radius)} {num(cy + math.sin(a) * radius)}")
    pairs = list(zip(angs, angs[1:] + ([angs[0]] if sweep == 360 else [])))
    for k in range(1, rings + 1):
        r = radius * k / (rings + .4)
        for a1, a2 in pairs:
            x1, y1 = cx + math.cos(a1) * r, cy + math.sin(a1) * r
            x2, y2 = cx + math.cos(a2) * r, cy + math.sin(a2) * r
            am = (a1 + a2) / 2
            rm = r * (1 - sag)
            d.append(f"M{num(x1)} {num(y1)}Q{num(cx + math.cos(am) * rm)} {num(cy + math.sin(am) * rm)} {num(x2)} {num(y2)}")
        nodes += [(cx + math.cos(a) * r, cy + math.sin(a) * r) for a in angs]
    svg = (f'<path d="{"".join(d)}" fill="none" stroke="{color}" stroke-width="{width}" '
           f'stroke-linecap="round" opacity="{opacity}"/>')
    return svg, nodes


def burst(cx: float, cy: float, r1: float, r2: float, points: int, fill: str,
          stroke: str = INK, seed: int = 3, rot: float = 0) -> str:
    """Comic starburst balloon."""
    rnd = random.Random(seed)
    pts = []
    for i in range(points * 2):
        a = math.radians(rot) + math.pi * i / points
        r = (r2 if i % 2 == 0 else r1) * rnd.uniform(.9, 1.08)
        pts.append(f"{num(cx + math.cos(a) * r)},{num(cy + math.sin(a) * r * .8)}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="4" stroke-linejoin="round"/>'


def zigzag(x: float, y: float, length: float, angle: float, amp: float = 5, seg: float = 8) -> str:
    """One spider-sense squiggle."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    n = int(length // seg)
    pts = [f"M{num(x)} {num(y)}"]
    for i in range(1, n + 1):
        s = amp if i % 2 else -amp
        pts.append(f"L{num(x + ux * seg * i + px * s)} {num(y + uy * seg * i + py * s)}")
    return "".join(pts)


def skyline(x0: float, width: float, base: float, hmin: float, hmax: float, seed: int,
            fill: str, invert: bool = False, windows: str | None = None, profile=None,
            towers: int = 0, win_density: float = .16, rim: str | None = None) -> str:
    """City silhouette. invert=True hangs buildings from `base` downward (the leap of faith)."""
    rnd = random.Random(seed)
    sgn = 1 if invert else -1
    bodies, lights, x = [], [], x0
    tower_at = set(rnd.sample(range(6, 30), towers)) if towers else set()
    idx = 0
    while x < x0 + width:
        w = rnd.uniform(26, 74)
        k = profile((x - x0) / width) if profile else 1
        h = rnd.uniform(hmin, hmax) * k
        top = base + sgn * h
        y = min(base, top)
        bodies.append(f"M{num(x)} {num(y)}h{num(w)}v{num(h)}h{num(-w)}z")
        if rnd.random() < .3:  # stepped crown
            cw = w * rnd.uniform(.3, .6)
            ch = rnd.uniform(8, 22)
            cxp = x + (w - cw) / 2
            bodies.append(f"M{num(cxp)} {num(top if invert else top - ch)}h{num(cw)}v{num(ch)}h{num(-cw)}z")
            if rnd.random() < .5:
                ax = x + w / 2
                tip = top + sgn * (ch + rnd.uniform(14, 30))
                bodies.append(f"M{num(ax - 1)} {num(min(top, tip))}h2v{num(abs(tip - top))}h-2z")
        if idx in tower_at:  # Brooklyn water tower on the roof
            tx = x + w * .5 - 9
            if invert:
                bodies.append(f"M{num(tx)} {num(top)}h18v14h-18zM{num(tx - 2)} {num(top + 14)}h22l-11 10z"
                              f"M{num(tx + 2)} {num(top - 8)}h2v8h-2zM{num(tx + 14)} {num(top - 8)}h2v8h-2z")
            else:
                bodies.append(f"M{num(tx)} {num(top - 22)}h18v14h-18zM{num(tx - 2)} {num(top - 22)}h22l-11 -10z"
                              f"M{num(tx + 2)} {num(top - 8)}h2v8h-2zM{num(tx + 14)} {num(top - 8)}h2v8h-2z")
        if windows:
            for wy in range(int(y) + 8, int(y + h) - 6, 9):
                for wx in range(int(x) + 5, int(x + w) - 6, 8):
                    if rnd.random() < win_density:
                        lights.append(f"M{wx} {wy}h3v4h-3z")
        x += w + rnd.uniform(-4, 3)
        idx += 1
    stroke = f' stroke="{rim}" stroke-width="1.2" stroke-opacity=".55"' if rim else ""
    out = f'<path d="{"".join(bodies)}" fill="{fill}"{stroke}/>'
    if windows:
        out += f'<path d="{"".join(lights)}" fill="{windows}"/>'
    return out


def svg_doc(w: int, h: int, body: str, title: str, desc: str = "", css: str = "", defs: str = "") -> str:
    defs += "".join(f'<path id="{k}" d="{v}"/>' for k, v in _GLYPHS.items()) + "".join(_RUNS)
    _GLYPHS.clear()
    _RUNS.clear()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title><desc id="d">{escape(desc or title)}</desc>'
            f'<style>{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>')


def save(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"{rel:38s} {len(content.encode()) / 1024:6.1f} KB")
