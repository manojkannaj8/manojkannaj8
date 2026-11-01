"""Section headers, panels, cards and the rest of the profile's artwork."""
from __future__ import annotations

import math
import random

from svgkit import (BODY, CONDENSED, CYAN, DEEP, DISPLAY, INK, MAGENTA, MONO, MUTED, NIGHT,
                    PAPER, RED, VIOLET, YELLOW, burst, chip, dots_pattern, halftone_field,
                    hatch_pattern, measure, misprint, num, paragraph, save, skyline, splatter,
                    svg_doc, text, text_d, web, wrap, zigzag)

W = 1200
PANEL = "#0E0A1F"
EDGE = "#2E1D66"

GLITCH = """
.gl{animation:gl 6s steps(1) infinite}
@keyframes gl{0%,6%,100%{transform:translate(0,0);opacity:0}1%{transform:translate(-12px,0);opacity:1}
3%{transform:translate(8px,0);opacity:1}5%{transform:translate(-4px,0);opacity:1}}
"""


def bg_defs() -> str:
    return (f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{INK}"/>'
            f'<stop offset="1" stop-color="{NIGHT}"/></linearGradient>'
            + hatch_pattern("hatch", "#24145A", 6, 1, -30) + dots_pattern("dots", VIOLET, 7, 1.5))


def autofit(t: str, font: str, size: float, max_w: float) -> float:
    return min(size, size * max_w / measure(t, font, size))


# ─────────────────────────────────────────────────────── section headers
SECTIONS = [
    ("01", "ORIGIN STORY", "// about me", "origin"),
    ("02", "THE ARSENAL", "// skills, traced to the code that proves them", "arsenal"),
    ("03", "TECH STACK", "// the gear, logo by logo", "stack"),
    ("04", "DIMENSIONS", "// featured projects: every build, its own universe", "dimensions"),
    ("05", "THE ROUTE", "// experience & leadership", "route"),
    ("06", "HEADLINES", "// hackathons, research, patents", "headlines"),
    ("07", "THE SIGNAL", "// live from github, refreshed daily", "signal"),
    ("08", "NEXT ISSUE", "// what i'm exploring now", "next"),
]


def section_header(n: str, title: str, sub: str, slug: str, idx: int) -> None:
    H = 140
    rnd = random.Random(idx)
    defs = bg_defs() + f'<clipPath id="c"><rect width="{W}" height="{H}"/></clipPath>'
    b = [f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#bg)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#hatch)" opacity=".5"/>']
    wsvg, _ = web(W + 10, H + 10, 230, 6, 5, VIOLET, start=180, sweep=90, width=1.2, opacity=.7)
    b.append(wsvg)
    b.append(halftone_field(820, 0, 380, H, 10, MAGENTA, 3, lambda u, v: max(0, u - .25) * (1 - v * .4), idx))
    # the red slash that carries the number
    b.append(f'<polygon points="0,0 236,0 196,{H} 0,{H}" fill="{RED}"/>')
    b.append(f'<g opacity=".35">' + halftone_field(0, 0, 236, H, 8, INK, 3.2, lambda u, v: max(0, 1 - u * 1.3 + v * .3), idx + 9) + '</g>')
    b.append(f'<polygon points="236,0 250,0 210,{H} 196,{H}" fill="{INK}"/>')
    nd = text_d(n, DISPLAY, 104, 22, 118)
    b.append(f'<path d="{nd}" fill="{PAPER}" transform="translate(5 4)"/><path d="{nd}" fill="{INK}"/>')
    # title with a glitch copy
    size = autofit(title, DISPLAY, 54, 760)
    b.append(misprint(title, DISPLAY, size, 262, 84, off=3.5))
    td = text_d(title, DISPLAY, size, 262, 84)
    defs += f'<clipPath id="g1"><rect x="0" y="52" width="{W}" height="12"/></clipPath>'
    b.append(f'<g clip-path="url(#g1)"><g class="gl" style="animation-delay:{idx * .7:.1f}s"><path d="{td}" fill="{CYAN}"/></g></g>')
    b.append(text(sub, MONO, 15, 265, 116, MUTED, ls=.3))
    b.append(text(f"EARTH-MKJ  ·  P.{n}", MONO, 13, 1176, 30, CYAN, "end", ls=.8))
    sense = "".join(zigzag(262 + measure(title, DISPLAY, size) + 14, 36, L, a, 3.5, 6) for L, a in [(26, -40), (30, -10)])
    b.append(f'<path class="sn" d="{sense}" fill="none" stroke="{YELLOW}" stroke-width="2.6" stroke-linejoin="round"/>')
    b.append(f'<rect y="{H - 4}" width="{W}" height="4" fill="{INK}"/><rect x="196" y="{H - 4}" width="{rnd.randint(260, 420)}" height="4" fill="{CYAN}"/>')
    b.append('</g>')
    css = GLITCH + ".sn{animation:sn 1.8s steps(1) infinite}@keyframes sn{0%,55%{opacity:1}60%,75%{opacity:0}80%{opacity:1}}"
    save(f"assets/sections/{n}-{slug}.svg", svg_doc(W, H, "".join(b), f"{n} — {title.title()}", sub.strip("/ "), css, defs))


# ───────────────────────────────────────────────────────────── dossier
def emblem(cx: float, cy: float, r: float) -> str:
    """Original monogram: MKJ caught in a web, half red, half ink."""
    out = [f'<clipPath id="em"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>',
           f'<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="{INK}" stroke="{PAPER}" stroke-width="3"/>',
           f'<g clip-path="url(#em)"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="{INK}"/>',
           f'<polygon points="{cx - r},{cy - r} {cx + r * .35},{cy - r} {cx - r * .35},{cy + r} {cx - r},{cy + r}" fill="{RED}"/>',
           halftone_field(cx - r, cy - r, 2 * r, 2 * r, 8, INK, 3, lambda u, v: max(0, .9 - u * 1.6), 3)]
    w, _ = web(cx, cy, r * 1.05, 12, 5, PAPER, sag=.18, width=1.1, opacity=.35)
    out.append(w + '</g>')
    out.append(misprint("MKJ", DISPLAY, r * .62, cx, cy + r * .22, anchor="middle", off=3))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CYAN}" stroke-width="2" stroke-dasharray="3 7" class="spin" style="transform-origin:{cx}px {cy}px"/>')
    return "".join(out)


def dossier() -> None:
    H = 420
    defs = bg_defs()
    b = [f'<rect width="{W}" height="{H}" fill="url(#bg)"/>', f'<rect width="{W}" height="{H}" fill="url(#hatch)" opacity=".4"/>',
         f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" fill="none" stroke="{EDGE}" stroke-width="3"/>']
    b.append(splatter(190, 330, 110, RED, 31, n=50, drips=3, rmax=8))
    b.append(emblem(190, 205, 125))
    # file tab
    b.append(f'<rect x="380" y="34" width="300" height="34" fill="{YELLOW}"/>' + text("IDENTITY FILE  //  #MKJ-26", MONO, 14, 394, 57, INK, ls=.4))
    b.append(text("CLEARANCE: PUBLIC", MONO, 13, 1166, 57, MUTED, "end", ls=.8))
    fields = [
        ("NAME", "Manoj Kanna J"), ("BASE", "Chennai, India"),
        ("ORIGIN", "B.Tech CSE · SRM IST Ramapuram"), ("CGPA", "9.35 / 10  (2024 – present)"),
        ("CURRENT POST", "Technical Head · Logic Play Club"), ("LAST MISSION", "AI & Data Intern · Deloitte, 2026"),
        ("POWERS", "Agentic AI · ML · Vision · Full-stack"), ("SIDE WORK", "Client websites · event posters"),
    ]
    for i, (k, v) in enumerate(fields):
        x = 380 + (i % 2) * 400
        y = 112 + (i // 2) * 62
        b.append(text(k, MONO, 12, x, y, CYAN, ls=1))
        b.append(text(v, BODY, 21, x, y + 28, PAPER))
        b.append(f'<rect x="{x}" y="{y + 40}" width="370" height="1" fill="{EDGE}"/>')
    # stamp
    b.append(f'<g transform="rotate(-4 1030 380)" opacity=".92"><rect x="895" y="356" width="270" height="48" fill="none" stroke="{RED}" stroke-width="4"/>'
             + text("PATENT · IEEE", CONDENSED, 28, 1030, 391, RED, "middle", ls=1) + '</g>')
    css = ".spin{animation:spin 24s steps(48) infinite}@keyframes spin{to{transform:rotate(360deg)}}"
    save("assets/dossier.svg", svg_doc(W, H, "".join(b), "Identity file — Manoj Kanna J",
         "Name Manoj Kanna J; based in Chennai; B.Tech CSE at SRM IST Ramapuram, CGPA 9.35; Technical Head at Logic Play "
         "Technical Club; AI & Data Intern at Deloitte in 2026; works across agentic AI, machine learning, computer vision and full-stack.",
         css, defs))


# ───────────────────────────────────────────────────────────── arsenal
S, H_, O = "solid", "half", "outline"
ARSENAL = [
    ("MACHINE LEARNING", CYAN, [("scikit-learn", S), ("XGBoost", S), ("CatBoost", S), ("SHAP", S), ("Pandas", S),
                                ("NumPy", S), ("TensorFlow / Keras", S), ("Calibration", S), ("Grouped CV", S),
                                ("Random Forest", O), ("MLP", O)]),
    ("AGENTIC AI", RED, [("CrewAI", S), ("Gemini", S), ("Groq", S), ("Pydantic", S),
                                    ("Prompt-injection defence", S), ("LangGraph", H_), ("LangFuse", H_), ("RAG", H_),
                                    ("Tool calling", H_)]),
    ("VISION & IOT", MAGENTA, [("YOLO", S), ("ByteTrack", S), ("OpenCV", S), ("MobileNetV2", S), ("Arduino", S)]),
    ("BACKEND & APIS", YELLOW, [("FastAPI", S), ("Flask", S), ("WebSockets", S), ("SQLAlchemy", S), ("REST APIs", S),
                                ("Streamlit", S), ("Supabase", H_), ("SQLite", O)]),
    ("FRONTEND & DATA VIZ", CYAN, [("React", S), ("Vite", S), ("Tailwind CSS", S), ("D3", S), ("Three.js", S)]),
    ("CLOUD & TOOLS", MAGENTA, [("Git", S), ("GitHub", S), ("Vercel", S), ("Docker", H_), ("AWS EC2 · S3 · Lambda", H_),
                                ("VS Code", O), ("Antigravity", O)]),
    ("LANGUAGES", YELLOW, [("Python", S), ("JavaScript", S), ("HTML", S), ("CSS", S), ("SQL", O), ("Java", O), ("C", O)]),
]


def flow_chips(items, x0: float, y0: float, max_w: float, color: str, size: float = 14) -> tuple[str, float]:
    x, y, out = x0, y0, []
    for label, kind in items:
        w = measure(label, MONO, size) + 20
        if x + w > x0 + max_w:
            x, y = x0, y + 40
        svg, w = chip(label, x, y, size, kind, color)
        out.append(svg)
        x += w + 9
    return "".join(out), y + 30


def arsenal() -> None:
    defs = bg_defs()
    b = []
    pad, gap, top = 20, 18, 108
    cols = [(0, 3), (3, 6)]
    col_w = (W - 2 * pad - 2 * gap) / 3
    y = top
    for lo, hi in cols:
        row_h = 0
        bodies = []
        for k, (name, color, items) in enumerate(ARSENAL[lo:hi]):
            x = pad + k * (col_w + gap)
            chips, end = flow_chips(items, x + 18, y + 64, col_w - 36, color)
            h = end - y + 22
            row_h = max(row_h, h)
            bodies.append((x, name, color, chips, items))
        for x, name, color, chips, items in bodies:
            b.append(f'<rect x="{num(x)}" y="{y}" width="{num(col_w)}" height="{num(row_h)}" fill="{PANEL}" stroke="{EDGE}" stroke-width="2"/>')
            b.append(f'<rect x="{num(x)}" y="{y}" width="8" height="{num(row_h)}" fill="{color}"/>')
            b.append(text(name, DISPLAY, 18, x + 22, y + 38, PAPER))
            n_s = sum(1 for _, kd in items if kd == S)
            b.append(text(f"{n_s:02d}/{len(items):02d}", MONO, 12, x + col_w - 16, y + 37, color, "end"))
            b.append(chips)
        y += row_h + gap
    # languages strip, full width
    name, color, items = ARSENAL[6]
    chips, end = flow_chips(items, pad + 230, y + 22, W - 2 * pad - 250, color)
    h = end - y + 22
    b.append(f'<rect x="{pad}" y="{y}" width="{W - 2 * pad}" height="{num(h)}" fill="{PANEL}" stroke="{EDGE}" stroke-width="2"/>'
             f'<rect x="{pad}" y="{y}" width="8" height="{num(h)}" fill="{color}"/>')
    b.append(text(name, DISPLAY, 19, pad + 22, y + h / 2 + 7, PAPER))
    b.append(chips)
    H = int(y + h + 30)

    # legend
    head = [f'<rect width="{W}" height="{H}" fill="url(#bg)"/>', f'<rect width="{W}" height="{H}" fill="url(#hatch)" opacity=".35"/>']
    wsvg, nodes = web(W - 40, 40, 300, 7, 5, VIOLET, start=90, sweep=90, width=1.1, opacity=.6)
    head.append(wsvg)
    head.append(text("HOW TO READ THE WEB", MONO, 13, pad, 40, CYAN, ls=1))
    x = pad
    for label, kind, note in [("Shipped", S, "in my projects"), ("Applied", H_, "at Deloitte & in club workshops"), ("Toolkit", O, "also in my skill set")]:
        svg, w = chip(label, x, 56, 14, kind, PAPER if kind != S else PAPER)
        head.append(svg)
        head.append(text(note, BODY, 15, x + w + 10, 76, MUTED))
        x += w + measure(note, BODY, 15) + 46
    save("assets/arsenal.svg", svg_doc(W, H, "".join(head + b), "Technical arsenal",
         "Skills grouped into machine learning, agentic AI, computer vision and IoT, backend, frontend, cloud and languages. "
         "Solid chips are used in my projects; half-filled were applied at Deloitte or in club workshops; dashed are also in my skill set.",
         "", defs))


# ──────────────────────────────────────────────────────────── projects
def stat_blocks(stats, x0: float, y0: float, bw: float, bh: float = 86, gap: float = 12) -> str:
    out = []
    for i, (v, label) in enumerate(stats):
        x = x0 + i * (bw + gap)
        out.append(f'<rect x="{num(x)}" y="{y0}" width="{num(bw)}" height="{bh}" fill="{INK}" stroke="{EDGE}" stroke-width="2"/>')
        out.append(f'<rect x="{num(x)}" y="{y0}" width="{num(bw)}" height="4" fill="{YELLOW}"/>')
        out.append(text(v, DISPLAY, autofit(v, DISPLAY, 28, bw - 24), x + 12, y0 + 42, YELLOW))
        for j, line in enumerate(wrap(label, MONO, 11, bw - 22)[:2]):
            out.append(text(line, MONO, 11, x + 12, y0 + 62 + j * 15, MUTED))
    return "".join(out)


def pipeline(steps, x: float, y0: float, gap: float, cid: str) -> str:
    """The build drawn as a strand of web: one node per stage, packets running down it."""
    y1 = y0 + gap * (len(steps) - 1)
    pts = []
    for i in range(len(steps)):
        pts.append(f"{num(x + (6 if i % 2 else -6))},{num(y0 + i * gap)}")
    line = "M" + " L".join(pts)
    out = [f'<path d="{line}" fill="none" stroke="{VIOLET}" stroke-width="3"/>',
           f'<path class="pk" d="{line}" fill="none" stroke="{YELLOW}" stroke-width="4" stroke-linecap="round" stroke-dasharray="12 {num(y1 - y0 + 40)}"/>']
    for i, (name, role) in enumerate(steps):
        cx = x + (6 if i % 2 else -6)
        cy = y0 + i * gap
        col = RED if i in (0, len(steps) - 1) else CYAN
        out.append(f'<circle cx="{num(cx)}" cy="{num(cy)}" r="10" fill="{INK}" stroke="{col}" stroke-width="3"/>'
                   f'<circle cx="{num(cx)}" cy="{num(cy)}" r="3.5" fill="{col}"/>')
        out.append(text(name, CONDENSED, 21, x + 30, cy + 2, PAPER))
        out.append(text(role, MONO, 11, x + 30, cy + 18, MUTED))
    return "".join(out)


def card_base(w: int, h: int, seed: int, spot: tuple[float, float]) -> tuple[str, list[str]]:
    rnd = random.Random(seed)
    defs = bg_defs() + f'<clipPath id="c"><rect width="{w}" height="{h}"/></clipPath>'
    b = [f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#bg)"/>',
         f'<rect width="{w}" height="{h}" fill="url(#hatch)" opacity=".45"/>',
         halftone_field(w * .45, 0, w * .55, h * .6, 11, DEEP, 4, lambda u, v: max(0, u - .2) * (1 - v), seed)]
    ws, _ = web(w + 20, -20, h * .9, 7, 6, VIOLET, start=90, sweep=90, width=1, opacity=.45)
    b.append(ws)
    b.append(splatter(*spot, 60, rnd.choice([RED, MAGENTA]), seed, n=40, drips=2, rmax=7))
    return defs, b


def card_head(b: list[str], code: str, label: str, title_lines: list[str], max_w: float, size: float = 58) -> float:
    tw = measure(code, MONO, 14) + 24
    b.append(f'<rect x="36" y="34" width="{num(tw)}" height="32" fill="{RED}"/>' + text(code, MONO, 14, 48, 56, INK, ls=.4))
    b.append(text(label, MONO, 13, 36 + tw + 14, 55, MUTED, ls=.8))
    y = 66
    size = min(autofit(t, DISPLAY, size, max_w) for t in title_lines)
    for t in title_lines:
        y += size * .95 + 10
        b.append(misprint(t, DISPLAY, size, 36, y, off=3))
    return y


def card_full(slug: str, code: str, label: str, title: list[str], tagline: str, stats, stack, steps, badge, seed: int) -> None:
    w, h = 1200, 470
    defs, b = card_base(w, h, seed, (690, 52))
    y = card_head(b, code, label, title, 640, 56)
    para, y = paragraph(tagline, BODY, 20, 36, y + 40, 640, 29)
    b.append(para)
    b.append(stat_blocks(stats, 36, y + 28, (640 - 36) / 4))
    chips, cx = [], 36
    for s in stack:
        svg, cw = chip(s, cx, h - 58, 12, O, PAPER, h=26, pad=8)
        if cx + cw > 700:
            break
        chips.append(svg)
        cx += cw + 7
    b.append("".join(chips))
    b.append(f'<rect x="740" y="34" width="2" height="{h - 68}" fill="{EDGE}"/>')
    b.append(text("SYSTEM MAP", MONO, 12, 772, 56, CYAN, ls=1.2))
    b.append(pipeline(steps, 790, 98, (h - 150) / (len(steps) - 1), slug))
    if badge:
        b.append(f'<g class="bob">{burst(1095, 92, 52, 76, 11, YELLOW, seed=seed)}'
                 + "".join(text(t, DISPLAY, autofit(t, DISPLAY, sz, 92), 1095, 92 + dy, RED, "middle") for t, sz, dy in badge) + '</g>')
    b.append(f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" fill="none" stroke="{EDGE}" stroke-width="3"/></g>')
    css = (".pk{animation:pk 2.8s steps(14) infinite}@keyframes pk{from{stroke-dashoffset:0}to{stroke-dashoffset:-%d}}"
           ".bob{animation:bob 2s steps(2) infinite;transform-origin:1095px 92px}@keyframes bob{50%%{transform:rotate(-4deg) scale(1.04)}}") % int(h)
    save(f"assets/projects/{slug}.svg", svg_doc(w, h, "".join(b), " ".join(title).title(), tagline, css, defs))


def card_half(slug: str, code: str, label: str, title: list[str], tagline: str, stats, stack, foot: str, badge, seed: int) -> None:
    w, h = 600, 500
    defs, b = card_base(w, h, seed, (575, 300))
    y = card_head(b, code, label, title, 520, 46)
    para, y = paragraph(tagline, BODY, 19, 36, y + 38, 520, 27)
    b.append(para)
    b.append(stat_blocks(stats, 36, y + 26, (528 - 12 * (len(stats) - 1)) / len(stats)))
    chips, cx, cy = [], 36, y + 136
    for s in stack:
        svg, cw = chip(s, cx, cy, 12, O, PAPER, h=26, pad=8)
        if cx + cw > w - 36:
            cx, cy = 36, cy + 34
            svg, cw = chip(s, cx, cy, 12, O, PAPER, h=26, pad=8)
        chips.append(svg)
        cx += cw + 7
    b.append("".join(chips))
    b.append(f'<rect x="0" y="{h - 46}" width="{w}" height="46" fill="{INK}"/><rect x="0" y="{h - 46}" width="{w}" height="2" fill="{RED}"/>')
    b.append(text(foot, MONO, 13, 36, h - 17, CYAN, ls=.4))
    if badge:
        t, sz = badge
        b.append(f'<g class="bob">{burst(520, 74, 36, 54, 10, YELLOW, seed=seed)}' + text(t, DISPLAY, (sz := min(sz, autofit(t, DISPLAY, sz, 64))), 520, 74 + sz * .36, RED, "middle") + '</g>')
    b.append(f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" fill="none" stroke="{EDGE}" stroke-width="3"/></g>')
    css = ".bob{animation:bob 2s steps(2) infinite;transform-origin:520px 74px}@keyframes bob{50%{transform:rotate(-5deg) scale(1.05)}}"
    save(f"assets/projects/{slug}.svg", svg_doc(w, h, "".join(b), " ".join(title).title(), tagline, css, defs))


def projects() -> None:
    card_full(
        "surgeguard", "EARTH-0926", "DIMENSION 01  ·  SEP 2026  ·  TEAM OF THREE", ["SURGEGUARD"],
        "Real-time crowd and queue prediction from live camera feeds: YOLO detection and ByteTrack tracking feed "
        "an explainable Crowd Stability Index built from five weighted indicators.",
        [("WINNER", "best implementation"), ("5", "weighted CSI indicators"),
         ("+15 MIN", "queue forecast horizon"), ("3", "alert channels")],
        ["Python", "YOLO", "ByteTrack", "OpenCV", "FastAPI", "WebSockets", "React", "Arduino"],
        [("LIVE CAMERA FEEDS", "video in"), ("YOLO", "person detection"), ("BYTETRACK", "tracking"),
         ("CROWD STABILITY INDEX", "five weighted indicators"), ("HOLT'S LINEAR TREND", "queues at +5 / +10 / +15 min"),
         ("FASTAPI + WEBSOCKETS", "real-time backend"), ("COMMAND CENTRE · STAFF APP · ARDUINO", "react, alerts, alarms")],
        [("WINNER", 21, 2), ("SENSORA 2.0", 10, 22)], 41)
    card_full(
        "prompt-injection", "EARTH-1026", "DIMENSION 02  ·  OCT 2026", ["PROMPT INJECTION", "RISK PREDICTION"],
        "A two-stage ML guard for LLM agents: TF-IDF + Logistic Regression flags planted instructions in tool outputs, "
        "and a calibrated XGBoost model predicts whether the agent would obey.",
        [("0.9999", "ROC-AUC, stage 1"), ("36,679", "AgentDojo runs, grouped CV"),
         ("28", "agents"), ("3.0%", "attack success, from 17.2%")],
        ["Python", "scikit-learn", "XGBoost", "SHAP", "Streamlit"],
        [("TOOL OUTPUT", "what the agent reads"), ("TF-IDF + LOGISTIC REG.", "stage 1: planted instruction?"),
         ("CALIBRATED XGBOOST", "stage 2: would the agent obey?"), ("REPLAYED RUNS", "attack success 17.2% -> 3.0%"),
         ("SHAP", "explanations"), ("STREAMLIT", "live dashboard")],
        [("-83%", 30, 4), ("ATTACK SUCCESS", 9, 22)], 17)
    card_full(
        "dop-xml", "EARTH-1125", "DIMENSION 03  ·  NOV 2025  ·  RESEARCH", ["DOP-XML"],
        "A full-stack dopamine prediction system: a CatBoost classifier with preprocessing and feature engineering, "
        "served through a Flask REST API (SQLAlchemy) and a React front end.",
        [("IEEE", "conference paper, published"), ("2", "ACM IKDD events"), ("2025", "IISER Pune, IIIT Bangalore"),
         ("CATBOOST", "classifier")],
        ["Python", "CatBoost", "Pandas", "Flask", "SQLAlchemy", "React"],
        [("DATA", "input features"), ("PREPROCESSING", "feature engineering"), ("CATBOOST", "classifier"),
         ("FLASK REST API", "with SQLAlchemy"), ("REACT", "front end")],
        [("IEEE", 26, 4), ("PUBLISHED", 10, 22)], 23)
    card_half("resume-analyser", "EARTH-0726", "DIMENSION 04  ·  JUL 2026", ["MULTI-AGENTIC", "RESUME ANALYSER"],
              "Five CrewAI agents screen a resume against a job description: skill match, SWOT and a hiring recommendation.",
              [("5", "crewai agents"), ("2", "llm providers: gemini, groq"), ("SWOT", "+ hiring call")],
              ["Python", "CrewAI", "Gemini", "Groq", "Pydantic", "Streamlit"],
              "SOURCE  >  github.com/manojkannaj8", ("AGENTS", 15), 9)
    card_half("repo-analyser", "EARTH-0226", "DIMENSION 05  ·  FEB 2026", ["GITHUB REPOSITORY", "ANALYSER"],
              "A repository analytics dashboard with dependency parsing and D3 visualisations over live GitHub API data.",
              [("LIVE", "deployed on vercel"), ("D3", "visualisations"), ("API", "live github data")],
              ["React", "Vite", "FastAPI", "Tailwind CSS", "D3"],
              "LIVE  >  repo-lens-nu.vercel.app", None, 13)


# ───────────────────────────────────────────────────────────── timeline
ROUTE = [
    ("AUG 2024", "SRM IST", "Starts B.Tech CSE. CGPA 9.35.", False),
    ("2025", "DOP-XML", "IEEE paper; ACM IKDD at IISER Pune & IIIT Bangalore.", False),
    ("JUN 2026", "DELOITTE", "AI & Data Intern: multi-agent systems, RAG, AWS.", True),
    ("AUG 2026", "LOGIC PLAY", "Technical Head. Ran VibeX; judged Stack Roulette.", False),
    ("SEP 2026", "SENSORA 2.0", "Best Implementation winner with SurgeGuard.", False),
    ("OCT 2026", "PROMPT INJECTION", "Two-stage ML guard for LLM agents.", False),
]


def route() -> None:
    H, mid = 560, 280
    defs = bg_defs()
    b = [f'<rect width="{W}" height="{H}" fill="url(#bg)"/>', f'<rect width="{W}" height="{H}" fill="url(#hatch)" opacity=".4"/>']
    xs = [110 + i * 196 for i in range(len(ROUTE))]
    # the strand, sagging between anchors
    d = f"M0 {mid}"
    prev = 0
    for x in xs + [W]:
        d += f"Q{num((prev + x) / 2)} {mid + 16} {num(x)} {mid}"
        prev = x
    b.append(f'<path d="{d}" fill="none" stroke="{VIOLET}" stroke-width="3"/>'
             f'<path d="{d}" fill="none" stroke="{CYAN}" stroke-width="1" transform="translate(0 -4)" opacity=".6"/>')
    b.append(f'<path class="pk" d="{d}" fill="none" stroke="{YELLOW}" stroke-width="4" stroke-linecap="round" stroke-dasharray="14 1300"/>')
    for i, (date, title, note, featured) in enumerate(ROUTE):
        x = xs[i]
        up = i % 2 == 0
        bw, bh = 270, 176
        bx = min(max(x - bw / 2, 14), W - bw - 14)
        by = mid - 50 - bh if up else mid + 50
        col = RED if featured else CYAN
        b.append(f'<path d="M{x} {mid}V{by + bh if up else by}" stroke="{col}" stroke-width="2" stroke-dasharray="4 4"/>')
        b.append(f'<rect x="{num(bx + 6)}" y="{by + 6}" width="{bw}" height="{bh}" fill="{INK}"/>')
        b.append(f'<rect x="{num(bx)}" y="{by}" width="{bw}" height="{bh}" fill="{PANEL}" stroke="{col}" stroke-width="{3 if featured else 2}"/>')
        b.append(f'<rect x="{num(bx)}" y="{by}" width="{bw}" height="34" fill="{col}"/>' + text(date, MONO, 15, bx + 14, by + 23, INK, ls=.8))
        b.append(text(title, CONDENSED, autofit(title, CONDENSED, 34, bw - 28), bx + 14, by + 72, PAPER))
        for j, line in enumerate(wrap(note, BODY, 19, bw - 28)[:3]):
            b.append(text(line, BODY, 19, bx + 14, by + 106 + j * 25, MUTED if not featured else PAPER))
        b.append(f'<circle cx="{x}" cy="{mid}" r="{13 if featured else 10}" fill="{INK}" stroke="{col}" stroke-width="3"/>'
                 f'<circle cx="{x}" cy="{mid}" r="4" fill="{col}"/>')
    css = ".pk{animation:pk 7s steps(40) infinite}@keyframes pk{to{stroke-dashoffset:-1314}}"
    save("assets/route.svg", svg_doc(W, H, "".join(b), "The route — experience timeline",
         "; ".join(f"{d}: {t} — {n}" for d, t, n, _ in ROUTE), css, defs))


# ───────────────────────────────────────────────────────────── headlines
def headlines() -> None:
    """A cream comic page in the middle of the night: the achievements."""
    H = 700
    g = 16
    defs = (dots_pattern("pd", "#E3D9C6", 9, 2) + dots_pattern("ink", INK, 8, 1.8)
            + dots_pattern("rd", "#C9142F", 7, 1.8) + hatch_pattern("ht", INK, 6, 1.4, 45)
            + f'<radialGradient id="rg" cx=".3" cy=".45" r=".7"><stop offset="0" stop-color="#3A1C8A"/><stop offset="1" stop-color="{INK}"/></radialGradient>')
    b = [f'<rect width="{W}" height="{H}" fill="{PAPER}"/>', f'<rect width="{W}" height="{H}" fill="url(#pd)"/>']

    def panel(x, y, w, h, fill, extra=""):
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>{extra}'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="5"/>')

    # big panel: SENSORA
    x, y, w, h = g, g, 724, 380
    panel(x, y, w, h, "url(#rg)")
    rays = "".join(f"M250 205L{num(250 + math.cos(a) * 900)} {num(205 + math.sin(a) * 900)}" for a in [i * math.tau / 44 for i in range(44)])
    b.append(f'<clipPath id="bp"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
             f'<g clip-path="url(#bp)"><path d="{rays}" stroke="{VIOLET}" stroke-width="2" opacity=".55"/>'
             + halftone_field(x, y, w, h, 10, MAGENTA, 3.4, lambda u, v: max(0, .55 - u) * v * 1.8, 2)
             + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="5"/></g>')
    b.append(f'<g class="pop">{burst(250, 205, 118, 172, 14, YELLOW, seed=12)}'
             + misprint("WINNER!", DISPLAY, 40, 250, 219, fill=RED, anchor="middle", off=0) + '</g>')
    b.append(text("SENSORA 2.0", DISPLAY, autofit("SENSORA 2.0", DISPLAY, 34, 262), 455, 120, PAPER))
    b.append(text("BEST IMPLEMENTATION", CONDENSED, 27, 457, 156, YELLOW, ls=.5))
    para, _ = paragraph("Won with SurgeGuard, a real-time crowd and queue prediction system, "
                        "built as a team of three.", BODY, 17, 457, 196, 265, 25)
    b.append(para)
    b.append(f'<rect x="{x}" y="{y + h - 44}" width="200" height="44" fill="{YELLOW}" stroke="{INK}" stroke-width="5"/>'
             + text("TEAM OF THREE", MONO, 14, x + 100, y + h - 16, INK, "middle", ls=1))

    # IEEE
    x2 = g * 2 + 724
    w2 = W - x2 - g
    panel(x2, g, w2, 182, CYAN, f'<rect x="{x2}" y="{g}" width="{w2}" height="182" fill="url(#ink)" opacity=".12"/>')
    b.append(text("PUBLISHED", DISPLAY, 38, x2 + 22, g + 62, INK))
    b.append(text("IEEE conference paper: DOP-XML", CONDENSED, 24, x2 + 22, g + 98, INK))
    para, _ = paragraph("Presented at ACM IKDD events at IISER Pune and IIIT Bangalore, 2025.", BODY, 16, x2 + 22, g + 130, w2 - 44, 22, INK)
    b.append(para)
    # patent
    y3 = g * 2 + 182
    panel(x2, y3, w2, 182, RED, f'<rect x="{x2}" y="{y3}" width="{w2}" height="182" fill="url(#rd)" opacity=".6"/>')
    b.append(misprint("PATENTED", DISPLAY, 38, x2 + 22, y3 + 62, off=0))
    b.append(text("An ML-based application", CONDENSED, 24, x2 + 22, y3 + 98, PAPER))
    para, _ = paragraph("Patent and research, alongside an IEEE conference publication.", BODY, 16, x2 + 22, y3 + 130, w2 - 44, 22, PAPER)
    b.append(para)

    # bottom row
    y4 = g * 2 + 380
    h4 = H - y4 - g
    cells = [("TOP 10", "of 300 teams", "HackBattle · VIT Vellore", INK, YELLOW, PAPER),
             ("TOP 6", "finalist", "Celestia 2.0", MAGENTA, INK, INK),
             ("9.35", "CGPA / 10", "B.Tech CSE · SRM IST Ramapuram", YELLOW, INK, INK),
             ("CLIENTS", "freelance & design", "Client portfolio & business websites; event posters", VIOLET, PAPER, PAPER)]
    cw = (W - g * 5) / 4
    for i, (big, small, note, fill, c1, c2) in enumerate(cells):
        cx = g + i * (cw + g)
        extra = f'<rect x="{num(cx)}" y="{y4}" width="{num(cw)}" height="{h4}" fill="url(#ht)" opacity=".08"/>'
        panel(num(cx), y4, num(cw), h4, fill, extra)
        b.append(text(big, DISPLAY, autofit(big, DISPLAY, 52, cw - 40), cx + 20, y4 + 82, c1))
        b.append(text(small.upper(), MONO, 13, cx + 22, y4 + 112, c2, ls=1))
        para, _ = paragraph(note, BODY, 16, cx + 22, y4 + 150, cw - 44, 22, c2)
        b.append(para)
    css = ".pop{animation:pop 2.4s steps(2) infinite;transform-origin:250px 205px}@keyframes pop{50%{transform:scale(1.05) rotate(-2deg)}}"
    save("assets/headlines.svg", svg_doc(W, H, "".join(b), "Headlines — achievements",
         "Winner, Best Implementation at SENSORA 2.0 with SurgeGuard (team of three); IEEE-published research DOP-XML, "
         "presented at ACM IKDD at IISER Pune and IIIT Bangalore; patented ML-based application; Top 10 of 300 at HackBattle; "
         "Top 6 finalist at Celestia 2.0; CGPA 9.35; freelance client websites.", css, defs))


# ───────────────────────────────────────────────────────────── next issue
NEXT = [
    ("AGENT SECURITY", RED, "Fine-tuned encoder detectors and Integrated Gradients: the next stage of the prompt-injection research."),
    ("EXPLAINABLE AI", MAGENTA, "Models that show their reasoning, from SHAP alerts to SurgeGuard's explainable stability index."),
    ("AGENTOPS", CYAN, "Tracing, evaluating and shipping multi-agent systems with LangGraph, LangFuse and AWS."),
    ("RAG FOR CODE", YELLOW, "Retrieval for private coding assistants, picking up from the in-house VS Code assistant at Deloitte."),
]


def next_issue() -> None:
    H = 330
    defs = bg_defs()
    b = [f'<rect width="{W}" height="{H}" fill="url(#bg)"/>', f'<rect width="{W}" height="{H}" fill="url(#hatch)" opacity=".4"/>']
    g = 18
    cw = (W - g * 5) / 4
    for i, (title, col, note) in enumerate(NEXT):
        x = g + i * (cw + g)
        y = 24
        h = H - 48
        b.append(f'<rect x="{num(x + 7)}" y="{y + 7}" width="{num(cw)}" height="{h}" fill="{col}" opacity=".9"/>')
        b.append(f'<rect x="{num(x)}" y="{y}" width="{num(cw)}" height="{h}" fill="{PANEL}" stroke="{col}" stroke-width="2.5"/>')
        b.append(text(f"#{27 + i}", DISPLAY, 46, x + 18, y + 64, col))
        b.append(text("COMING SOON", MONO, 11, x + cw - 16, y + 30, MUTED, "end", ls=1))
        b.append(text(title, CONDENSED, autofit(title, CONDENSED, 28, cw - 36), x + 18, y + 112, PAPER))
        if note:
            para, _ = paragraph(note, BODY, 16, x + 18, y + 146, cw - 36, 23, MUTED)
            b.append(para)
        else:
            for j, ww in enumerate([0.85, 0.6, 0.78, 0.4]):
                b.append(f'<rect class="rd" x="{num(x + 18)}" y="{y + 134 + j * 26}" width="{num((cw - 36) * ww)}" height="15" fill="{PAPER}"/>')
            b.append(text("agentic ai · patent · ieee", MONO, 11, x + 18, y + h - 20, col))
    css = ".rd{animation:rd 4s steps(1) infinite}@keyframes rd{0%,92%,100%{opacity:.9}94%{opacity:.2}96%{opacity:.9}97%{opacity:.3}}"
    save("assets/next-issue.svg", svg_doc(W, H, "".join(b), "Next issue — currently exploring",
         "Agent security (fine-tuned detectors, Integrated Gradients); explainable AI; "
         "AgentOps with LangGraph, LangFuse and AWS; retrieval for private coding assistants.", css, defs))


# ───────────────────────────────────────────────────────────── footer, buttons, divider
def footer() -> None:
    H = 300
    defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}"/>'
            f'<stop offset="1" stop-color="#2A1263"/></linearGradient>'
            f'<radialGradient id="gl" cx=".5" cy="1" r=".7"><stop offset="0" stop-color="{MAGENTA}" stop-opacity=".45"/>'
            f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>')
    b = [f'<rect width="{W}" height="{H}" fill="url(#bg)"/>', f'<rect width="{W}" height="{H}" fill="url(#gl)"/>']
    ws, _ = web(600, 330, 520, 15, 7, VIOLET, start=180, sweep=180, width=1, opacity=.5)
    b.append(ws)
    b.append(skyline(-20, W + 40, H, 30, 110, 3, "#170C3A", profile=lambda u: .5 + .5 * abs(math.sin(u * 3))))
    b.append(skyline(-10, W + 20, H, 20, 70, 8, INK, windows=YELLOW, towers=3, win_density=.14, rim=CYAN))
    cap = "TO BE CONTINUED…"
    cw = measure(cap, DISPLAY, 46) + 50
    b.append(f'<g transform="rotate(-3 600 110)"><rect x="{num(600 - cw / 2 + 8)}" y="72" width="{num(cw)}" height="80" fill="{RED}"/>'
             f'<rect x="{num(600 - cw / 2)}" y="64" width="{num(cw)}" height="80" fill="{YELLOW}" stroke="{INK}" stroke-width="4"/>'
             + text(cap, DISPLAY, 46, 600, 122, INK, "middle") + '</g>')
    b.append(text("THANKS FOR READING  //  MANOJ KANNA J  //  EARTH-MKJ", MONO, 13, 600, 186, PAPER, "middle", ls=1))
    save("assets/footer.svg", svg_doc(W, H, "".join(b), "To be continued…", "Closing panel: a lit city skyline under a web.", "", defs))


def button(slug: str, label: str, sub: str, col: str) -> None:
    w, h = 380, 92
    b = [f'<rect x="10" y="10" width="{w - 14}" height="{h - 14}" fill="{col}"/>',
         f'<rect x="2" y="2" width="{w - 14}" height="{h - 14}" fill="{INK}" stroke="{PAPER}" stroke-width="3"/>',
         f'<rect x="2" y="2" width="12" height="{h - 14}" fill="{col}"/>',
         text(label, DISPLAY, autofit(label, DISPLAY, 26, 300), 32, 42, PAPER),
         text(sub, MONO, 12, 33, 64, col, ls=.4)]
    save(f"assets/links/{slug}.svg", svg_doc(w, h, "".join(b), label.title(), sub))


def divider() -> None:
    H = 60
    d = "M0 30" + "".join(f"Q{x + 75} 44 {x + 150} 30" for x in range(0, W, 150))
    b = [f'<path d="{d}" fill="none" stroke="{VIOLET}" stroke-width="2.5"/>',
         f'<path d="{d}" fill="none" stroke="{CYAN}" stroke-width="1" transform="translate(0 -3)" opacity=".7"/>']
    for x in range(150, W, 150):
        b.append(f'<circle cx="{x}" cy="30" r="6" fill="{INK}" stroke="{RED if x == 600 else CYAN}" stroke-width="2.5"/>')
    b.append(f'<path d="{"".join(zigzag(600, 10, 22, a, 3, 5) for a in (-120, -90, -60))}" stroke="{RED}" stroke-width="2" fill="none"/>')
    save("assets/divider.svg", svg_doc(W, H, "".join(b), "Divider", "A strand of web."))


# ───────────────────────────────────────────────────────────── tech stack
# Logos from Simple Icons (scripts/icons.json, CC0). Tools without an official
# icon there get a lettered badge instead of an invented logo.
STACK = [
    ("LANGUAGES", YELLOW, [("python", "Python"), ("javascript", "JavaScript"), ("html5", "HTML5"), ("css", "CSS"),
                           ("openjdk", "Java"), ("c", "C"), ("SQL", "SQL")]),
    ("ML & DATA", CYAN, [("scikitlearn", "scikit-learn"), ("XGB", "XGBoost"), ("CAT", "CatBoost"), ("SHAP", "SHAP"),
                         ("pandas", "Pandas"), ("numpy", "NumPy")]),
    ("AGENTIC AI", RED, [("crewai", "CrewAI"), ("langgraph", "LangGraph"), ("LF", "LangFuse"),
                         ("googlegemini", "Gemini"), ("GROQ", "Groq"), ("pydantic", "Pydantic")]),
    ("VISION & IOT", MAGENTA, [("yolo", "YOLO"), ("BT", "ByteTrack"), ("opencv", "OpenCV"), ("arduino", "Arduino")]),
    ("BACKEND & DATA", YELLOW, [("flask", "Flask"), ("fastapi", "FastAPI"), ("streamlit", "Streamlit"),
                                ("sqlalchemy", "SQLAlchemy"), ("sqlite", "SQLite"), ("supabase", "Supabase")]),
    ("FRONTEND", CYAN, [("react", "React"), ("vite", "Vite"), ("tailwindcss", "Tailwind CSS"), ("d3", "D3")]),
    ("CLOUD & TOOLS", MAGENTA, [("AWS", "AWS"), ("docker", "Docker"), ("git", "Git"), ("github", "GitHub"),
                                ("VS", "VS Code"), ("AG", "Antigravity")]),
]


def tech_stack() -> None:
    import json
    from pathlib import Path
    icons = json.loads((Path(__file__).parent / "icons.json").read_text(encoding="utf-8"))
    pad, label_w, tw, th, gap = 24, 200, 112, 118, 12
    top = 30
    defs = bg_defs()
    used = set()
    tiles = []
    y = top
    n = 0
    for cat, color, items in STACK:
        tiles.append(f'<rect x="{pad}" y="{y + 10}" width="6" height="{th - 20}" fill="{color}"/>')
        tiles.append(text(cat, DISPLAY, autofit(cat, DISPLAY, 17, label_w - 30), pad + 18, y + th / 2 + 2, PAPER))
        tiles.append(text(f"{len(items):02d} TOOLS", MONO, 11, pad + 18, y + th / 2 + 22, color, ls=.8))
        for i, (key, name) in enumerate(items):
            x = pad + label_w + i * (tw + gap)
            cx = x + tw / 2
            tiles.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" fill="{PANEL}" stroke="{EDGE}" stroke-width="2"/>'
                         f'<rect x="{x}" y="{y}" width="{tw}" height="4" fill="{color}"/>')
            delay = f' style="animation-delay:{(n * .37) % 5:.2f}s"'
            if key in icons:
                used.add(key)
                s, ox, oy = 46 / 24, cx - 23, y + 22
                ref = f'href="#i-{key}"'
                tiles.append(f'<g transform="translate({num(ox)} {num(oy)}) scale({s:.4g})">'
                             f'<g class="fr"{delay}><use {ref} fill="{CYAN}" x="-1.2" y=".6"/>'
                             f'<use {ref} fill="{RED}" x="1.2" y="-.6"/></g><use {ref} fill="{PAPER}"/></g>')
            else:  # lettered badge for tools without an official icon
                size = autofit(key, DISPLAY, 26, 66)
                tiles.append(f'<rect x="{num(cx - 34)}" y="{y + 20}" width="68" height="50" fill="none" stroke="{PAPER}" stroke-width="2.5"/>')
                tiles.append(f'<g class="fr"{delay}>' + misprint(key, DISPLAY, size, cx, y + 45 + size * .36, anchor="middle", off=2) + '</g>')
            tiles.append(text(name, MONO, autofit(name, MONO, 12, tw - 14), cx, y + th - 18, MUTED, "middle"))
            n += 1
        y += th + 16
    H = int(y + top - 16)
    defs += "".join(f'<path id="i-{k}" d="{icons[k]["path"]}"/>' for k in sorted(used))
    b = [f'<rect width="{W}" height="{H}" fill="url(#bg)"/>', f'<rect width="{W}" height="{H}" fill="url(#hatch)" opacity=".35"/>']
    ws, _ = web(W + 10, H + 10, 380, 7, 6, VIOLET, start=180, sweep=90, width=1, opacity=.5)
    b.append(ws)
    b += tiles
    b.append(f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" fill="none" stroke="{EDGE}" stroke-width="3"/>')
    css = (".fr{animation:fr 5s steps(1) infinite}"
           "@keyframes fr{0%,6%,100%{transform:translate(0,0)}2%{transform:translate(-1.5px,1px)}4%{transform:translate(1.5px,-1px)}}")
    names = "; ".join(f"{cat.title()}: " + ", ".join(nm for _, nm in items) for cat, _, items in STACK)
    save("assets/tech-stack.svg", svg_doc(W, H, "".join(b), "Tech stack", names + ".", css, defs))


def build_all() -> None:
    for i, s in enumerate(SECTIONS):
        section_header(*s, i)
    dossier()
    arsenal()
    tech_stack()
    projects()
    route()
    headlines()
    next_issue()
    footer()
    divider()
    button("portfolio", "PORTFOLIO", "manojkj-portfolio.vercel.app", RED)
    button("linkedin", "LINKEDIN", "in/manojkannaj", CYAN)
    button("email", "EMAIL", "manojkannaj8@gmail.com", YELLOW)
