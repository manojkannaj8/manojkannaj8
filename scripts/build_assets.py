"""Builds every static SVG in assets/. Run: python scripts/build_assets.py"""
from __future__ import annotations

import math
import random

from svgkit import (CONDENSED, CYAN, DISPLAY, INK, MAGENTA, MONO, NIGHT, PAPER, RED, VIOLET,
                    YELLOW, dots_pattern, halftone_field, hatch_pattern, measure, num, save,
                    skyline, splatter, svg_doc, text, text_d, web, zigzag)

W = 1200

GLITCH_CSS = """
.gl1{animation:gl1 5s steps(1) infinite}.gl2{animation:gl2 5s steps(1) infinite}
@keyframes gl1{0%,7%,100%{transform:translate(0,0);opacity:0}1%{transform:translate(-14px,0);opacity:1}3%{transform:translate(9px,0);opacity:1}5%{transform:translate(-5px,0);opacity:1}
54%{transform:translate(12px,0);opacity:1}56%{transform:translate(0,0);opacity:0}}
@keyframes gl2{0%,8%,100%{transform:translate(0,0);opacity:0}2%{transform:translate(16px,0);opacity:1}4%{transform:translate(-10px,0);opacity:1}
55%{transform:translate(-12px,0);opacity:1}57%{transform:translate(0,0);opacity:0}}
"""


def glitch_slices(ref: str, bands: list[tuple[float, float]], cid: str) -> tuple[str, str]:
    """Copies of a path clipped to horizontal bands that jump sideways now and then."""
    defs, body = "", ""
    for i, (y, h) in enumerate(bands):
        defs += f'<clipPath id="{cid}{i}"><rect x="0" y="{num(y)}" width="{W}" height="{num(h)}"/></clipPath>'
        col = CYAN if i % 2 else RED
        body += (f'<g clip-path="url(#{cid}{i})"><g class="gl{i % 2 + 1}">'
                 f'<use href="{ref}" fill="{col}"/><use href="{ref}" fill="{PAPER}" transform="translate(4 0)"/></g></g>')
    return defs, body


# ─────────────────────────────────────────────────────────────── hero
def hero() -> None:
    H = 540
    rnd = random.Random(7)
    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1263"/>'
        f'<stop offset=".5" stop-color="{NIGHT}"/><stop offset="1" stop-color="#0B0618"/></linearGradient>'
        f'<radialGradient id="glow" cx=".8" cy=".58" r=".55"><stop offset="0" stop-color="{MAGENTA}" stop-opacity=".5"/>'
        f'<stop offset=".45" stop-color="{VIOLET}" stop-opacity=".28"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="node"><stop offset="0" stop-color="{PAPER}"/><stop offset=".35" stop-color="{CYAN}"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="nodeR"><stop offset="0" stop-color="{PAPER}"/><stop offset=".35" stop-color="{RED}"/>'
        f'<stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
        + dots_pattern("dots", VIOLET, 7, 1.7)
        + hatch_pattern("hatch", "#3A1A7A", 6, 1, -30)
        + f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset=".25" stop-color="#fff" stop-opacity="0"/>'
          f'<stop offset="1" stop-color="#fff"/></linearGradient><mask id="fadeM"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>'
        + f'<clipPath id="frame"><rect width="{W}" height="{H}"/></clipPath>'
        + '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4"/>'
          '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
    )
    b = [f'<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="url(#bg)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/>']

    # hatch shading in the lower half, like an inked night sky
    b.append(f'<rect width="{W}" height="{H}" fill="url(#hatch)" mask="url(#fadeM)" opacity=".55"/>')

    # the city, upside down: the moment of falling into the frame
    prof = lambda u: .35 + .65 * max(0, math.sin(u * math.pi * 1.05 - .15)) ** .7
    b.append(skyline(-20, W + 40, 0, 40, 120, 11, "#170C3A", invert=True, profile=prof))
    b.append(skyline(-10, W + 20, 0, 22, 82, 5, "#0B0718", invert=True, windows=YELLOW,
                     profile=lambda u: .45 + .55 * u, towers=3, win_density=.12, rim=CYAN))
    # cyan rim light on the hanging rooftops
    b.append(f'<rect y="0" width="{W}" height="3" fill="{CYAN}" opacity=".9"/>')

    # halftone moon-glow behind the web
    b.append(halftone_field(640, 120, 560, 420, 12, MAGENTA, 3.6,
                            lambda u, v: max(0, 1 - math.hypot(u - .65, (v - .55) * 1.2) * 1.9), 2))

    # the web: a neural graph strung across the night
    wsvg, nodes = web(1015, 330, 360, 11, 6, "#8E7BFF", sag=.16, width=1.1, opacity=.55)
    b.append(wsvg)
    wsvg2, _ = web(1015, 330, 360, 11, 6, CYAN, sag=.16, width=.6, opacity=.35)
    b.append(f'<g transform="translate(-3 2)">{wsvg2}</g>')
    picks = rnd.sample(nodes, 26)
    hot = set(rnd.sample(range(26), 5))
    for i, (x, y) in enumerate(picks):
        if 0 < x < W and 0 < y < H:
            g = "nodeR" if i in hot else "node"
            r = 9 if i in hot else rnd.choice([5, 6, 7])
            b.append(f'<circle class="p{i % 3}" cx="{num(x)}" cy="{num(y)}" r="{r}" fill="url(#{g})"/>')
    # packets running along three spokes
    for k, ang in enumerate([200, 233, 167]):
        a = math.radians(ang)
        x2, y2 = 1015 + math.cos(a) * 360, 330 + math.sin(a) * 360
        b.append(f'<path class="pk pk{k}" d="M{num(x2)} {num(y2)}L1015 330" stroke="{PAPER if k else YELLOW}" stroke-width="3" '
                 f'stroke-dasharray="10 400" stroke-linecap="round" fill="none"/>')

    # spray-paint hits
    b.append(splatter(905, 455, 120, RED, 21, n=90, drips=6, rmax=11))
    b.append(splatter(1130, 120, 70, MAGENTA, 8, n=45, drips=3, rmax=7))

    # issue box, top-left — the comic-cover corner
    b.append(f'<g transform="translate(46 30)"><rect width="86" height="102" fill="{RED}" stroke="{INK}" stroke-width="4"/>'
             + text("ISSUE", MONO, 12, 43, 22, INK, "middle")
             + text("#01", DISPLAY, 34, 43, 60, PAPER, "middle")
             + f'<rect x="10" y="70" width="66" height="2" fill="{INK}"/>'
             + text("NOV 26", MONO, 11, 43, 89, INK, "middle") + '</g>')

    # eyebrow
    b.append(f'<rect x="60" y="174" width="12" height="12" fill="{RED}"/>')
    b.append(text("AI/ML & SOFTWARE ENGINEER  //  B.TECH CSE, SRM IST  //  CHENNAI", MONO, 15, 84, 186, CYAN, ls=.6))

    # the name, mis-registered, halftone-shaded, with glitch slices
    name_d = text_d("MANOJ", DISPLAY, 158, 54, 330, ls=-2)
    defs += f'<path id="nm" d="{name_d}"/><clipPath id="nameC"><use href="#nm"/></clipPath>'
    b.append(f'<use href="#nm" fill="{CYAN}" transform="translate(-8 3)"/><use href="#nm" fill="{RED}" transform="translate(8 -3)"/>'
             f'<use href="#nm" fill="{PAPER}"/>')
    b.append(f'<g clip-path="url(#nameC)">'
             + halftone_field(40, 200, 700, 140, 7, VIOLET, 3.4, lambda u, v: max(0, (v - .35) * 1.6), 5)
             + '</g>')
    gdefs, gbody = glitch_slices("#nm", [(222, 20), (276, 14), (304, 12)], "s")
    defs += gdefs
    b.append(gbody)

    defs += f'<path id="sur" d="{text_d("KANNA J", DISPLAY, 88, 58, 428, ls=1)}"/><clipPath id="surC"><use href="#sur"/></clipPath>'
    b.append(f'<use href="#sur" fill="{RED}" transform="translate(6 5)"/>'
             f'<use href="#sur" fill="{INK}" stroke="{PAPER}" stroke-width="2.5" stroke-linejoin="round"/>')
    b.append(f'<g clip-path="url(#surC)"><rect x="40" y="340" width="560" height="100" fill="url(#dots)" opacity=".9"/></g>')

    # spider-sense: something's coming
    sense = "".join(zigzag(742, 210, L, a, 4.5, 7) for L, a in [(52, -55), (60, -25), (48, 5)])
    b.append(f'<path class="sense" d="{sense}" fill="none" stroke="{PAPER}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/>')

    # narration caption, slightly off-axis
    cap = "AI agents. ML models. Full-stack apps."
    cw = measure(cap, CONDENSED, 27) + 34
    b.append(f'<g transform="rotate(-2 60 470)"><rect x="64" y="452" width="{num(cw)}" height="44" fill="{INK}"/>'
             f'<rect x="58" y="446" width="{num(cw)}" height="44" fill="{YELLOW}" stroke="{INK}" stroke-width="3"/>'
             + text(cap, CONDENSED, 27, 75, 477, INK) + '</g>')

    # ticker
    tick = "   //   ".join(["DELOITTE AI & DATA INTERN", "SENSORA 2.0 WINNER", "IEEE PUBLISHED", "TECHNICAL HEAD · LOGIC PLAY",
                         "CGPA 9.35", "TOP 10 / 300 · HACKBATTLE", "PATENTED ML APPLICATION"]) + "   //   "
    tw = measure(tick, MONO, 13)
    b.append(f'<rect y="{H - 30}" width="{W}" height="30" fill="{INK}"/><rect y="{H - 30}" width="{W}" height="2" fill="{RED}"/>')
    defs += f'<path id="tk" d="{text_d(tick, MONO, 13, 170, H - 10)}"/>'
    b.append(f'<g class="tick" style="--tw:-{num(tw)}px" fill="{PAPER}"><use href="#tk"/><use href="#tk" x="{num(tw)}"/></g>')
    b.append(f'<rect y="{H - 30}" width="158" height="30" fill="{RED}"/>' + text("NOW PLAYING", MONO, 13, 16, H - 10, INK)
             + f'<circle class="rec" cx="146" cy="{H - 15}" r="4" fill="{INK}"/>')

    # corner registration marks
    for x, y, sx, sy in [(1170, 30, 1, 1), (1170, H - 52, 1, -1)]:
        b.append(f'<path d="M{x} {y}h{12 * sx}M{x + 6 * sx} {y - 6 * sy}v{12 * sy}" stroke="{PAPER}" stroke-width="1.5"/>'
                 f'<circle cx="{x + 6 * sx}" cy="{y}" r="4" fill="none" stroke="{PAPER}" stroke-width="1.2"/>')

    b.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".06"/>')
    b.append('</g>')

    css = GLITCH_CSS + """
.p0{animation:pulse 2.4s steps(3) infinite}.p1{animation:pulse 3.1s steps(3) infinite .6s}.p2{opacity:.8}
@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}
.pk{animation:pk 3.2s steps(16) infinite}.pk1{animation-delay:1.1s}.pk2{animation-delay:2.2s}
@keyframes pk{0%{stroke-dashoffset:0}100%{stroke-dashoffset:-410}}
.sense{animation:sense 1.6s steps(1) infinite}.s2{animation-delay:.4s}
@keyframes sense{0%,40%{opacity:1}50%,60%{opacity:0}70%,100%{opacity:1}}
.tick{animation:tick 38s linear infinite}@keyframes tick{to{transform:translateX(var(--tw))}}
.rec{animation:sense 1.2s steps(1) infinite}
"""
    save("assets/hero.svg", svg_doc(W, H, "".join(b),
         "Manoj Kanna J — AI/ML & Software Engineer",
         "Comic-cover banner: an upside-down night city, a spider-web drawn as a neural network, and the name Manoj Kanna J "
         "printed off-register with the caption 'AI agents. ML models. Full-stack apps.'", css, defs))


if __name__ == "__main__":
    from panels import build_all
    hero()
    build_all()
