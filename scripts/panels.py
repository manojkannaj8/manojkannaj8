"""Project cards and the tech-stack logo wall."""
from __future__ import annotations

from svgkit import (BODY, CONDENSED, CYAN, DEEP, DISPLAY, INK, MAGENTA, MONO, MUTED, NIGHT,
                    PAPER, RED, VIOLET, YELLOW, burst, chip, dots_pattern, halftone_field,
                    hatch_pattern, measure, misprint, num, paragraph, save, svg_doc, text, web, wrap)

W = 1200
PANEL = "#0E0A1F"
EDGE = "#2E1D66"

def bg_defs() -> str:
    return (f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{INK}"/>'
            f'<stop offset="1" stop-color="{NIGHT}"/></linearGradient>'
            + hatch_pattern("hatch", "#24145A", 6, 1, -30) + dots_pattern("dots", VIOLET, 7, 1.5))


def autofit(t: str, font: str, size: float, max_w: float) -> float:
    return min(size, size * max_w / measure(t, font, size))


S, H_, O = "solid", "half", "outline"


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


def card_base(w: int, h: int, seed: int) -> tuple[str, list[str]]:
    defs = bg_defs() + f'<clipPath id="c"><rect width="{w}" height="{h}"/></clipPath>'
    b = [f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#bg)"/>',
         f'<rect width="{w}" height="{h}" fill="url(#hatch)" opacity=".45"/>',
         halftone_field(w * .45, 0, w * .55, h * .6, 11, DEEP, 4, lambda u, v: max(0, u - .2) * (1 - v), seed)]
    ws, _ = web(w + 20, -20, h * .9, 7, 6, VIOLET, start=90, sweep=90, width=1, opacity=.45)
    b.append(ws)
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
    defs, b = card_base(w, h, seed)
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


def projects() -> None:
    card_full(
        "surgeguard", "SEP 2026", "SENSORA 2.0 WINNER  ·  TEAM OF THREE", ["SURGEGUARD"],
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
        "prompt-injection", "OCT 2026", "ML FOR LLM-AGENT SECURITY", ["PROMPT INJECTION", "RISK PREDICTION"],
        "A two-stage ML guard for LLM agents: TF-IDF + Logistic Regression flags planted instructions in tool outputs, "
        "and a calibrated XGBoost model predicts whether the agent would obey.",
        [("0.9999", "ROC-AUC, stage 1"), ("36,679", "AgentDojo runs, grouped CV"),
         ("28", "agents"), ("3.0%", "attack success, from 17.2%")],
        ["Python", "scikit-learn", "XGBoost", "SHAP", "Streamlit"],
        [("TOOL OUTPUT", "what the agent reads"), ("TF-IDF + LOGISTIC REG.", "stage 1: planted instruction?"),
         ("CALIBRATED XGBOOST", "stage 2: would the agent obey?"), ("REPLAYED RUNS", "attack success 17.2% -> 3.0%"),
         ("SHAP", "explanations"), ("STREAMLIT", "live dashboard")],
        [("-83%", 30, 4), ("ATTACK SUCCESS", 9, 22)], 17)


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
    projects()
    tech_stack()
