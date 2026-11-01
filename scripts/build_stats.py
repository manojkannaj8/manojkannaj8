"""Renders assets/signal.svg — live GitHub numbers and a contribution skyline.

Runs daily in GitHub Actions (see .github/workflows/signal.yml). Reads public
data only. If the API call fails, the last committed SVG is left untouched,
so the README never shows a broken image.

Local run: GITHUB_TOKEN=$(gh auth token) python scripts/build_stats.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request

from svgkit import (BODY, CONDENSED, CYAN, DISPLAY, INK, MAGENTA, MONO, MUTED, NIGHT, PAPER, RED,
                    VIOLET, YELLOW, dots_pattern, hatch_pattern, measure, num, save, svg_doc, text, web)

LOGIN = os.environ.get("PROFILE_LOGIN", "manojkannaj8")
QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes { stargazerCount languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}"""


def fetch() -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body or not body.get("data", {}).get("user"):
        raise RuntimeError(body.get("errors"))
    return body["data"]["user"]


def render(u: dict) -> str:
    W, H = 1200, 470
    cc = u["contributionsCollection"]
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cc["contributionCalendar"]["weeks"]]
    first_days = [w["contributionDays"][0]["date"] for w in cc["contributionCalendar"]["weeks"]]
    repos = u["repositories"]
    langs: dict[str, int] = {}
    for n in repos["nodes"]:
        for e in n["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1])
    total = sum(langs.values()) or 1
    days = [d["contributionCount"] for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    streak = run = 0
    for c in days:
        run = run + 1 if c else 0
        streak = max(streak, run)

    defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{INK}"/>'
            f'<stop offset="1" stop-color="{NIGHT}"/></linearGradient>'
            + hatch_pattern("hatch", "#24145A", 6, 1, -30) + dots_pattern("dots", INK, 6, 1.4)
            + f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1263"/>'
            f'<stop offset="1" stop-color="{INK}"/></linearGradient>')
    b = [f'<rect width="{W}" height="{H}" fill="url(#bg)"/>', f'<rect width="{W}" height="{H}" fill="url(#hatch)" opacity=".4"/>',
         f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" fill="none" stroke="#2E1D66" stroke-width="3"/>']

    # numbers
    tiles = [(cc["contributionCalendar"]["totalContributions"], "contributions, 1 yr"),
             (cc["totalCommitContributions"], "commits, 1 yr"), (cc["totalPullRequestContributions"], "pull requests"),
             (repos["totalCount"], "public repos"), (len(langs), "languages in code"), (streak, "longest streak, days")]
    for i, (v, label) in enumerate(tiles):
        x, y = 30 + (i % 2) * 190, 34 + (i // 2) * 100
        b.append(f'<rect x="{x}" y="{y}" width="176" height="88" fill="{INK}" stroke="#2E1D66" stroke-width="2"/>'
                 f'<rect x="{x}" y="{y}" width="176" height="4" fill="{[CYAN, RED, YELLOW, MAGENTA, CYAN, RED][i]}"/>')
        b.append(text(f"{v:,}", DISPLAY, 34, x + 14, y + 50, PAPER))
        b.append(text(label.upper(), MONO, 10, x + 15, y + 72, MUTED, ls=.3))

    # language mix, sprayed as one bar
    x0, bw = 430, 740
    b.append(text("LANGUAGE MIX  //  PUBLIC REPOS, BY BYTES", MONO, 12, x0, 50, CYAN, ls=1))
    x = x0
    cols = [CYAN, RED, YELLOW, MAGENTA, VIOLET, MUTED]
    legend_x = x0
    for i, (name, size) in enumerate(top[:6]):
        w = bw * size / total
        col = cols[i]
        b.append(f'<rect x="{num(x)}" y="66" width="{num(max(w - 3, 2))}" height="30" fill="{col}"/>')
        if i < 5:
            label = f"{name} {size / total:.0%}"
            b.append(f'<rect x="{num(legend_x)}" y="112" width="10" height="10" fill="{col}"/>')
            b.append(text(label, BODY, 15, legend_x + 16, 122, PAPER))
            legend_x += measure(label, BODY, 15) + 40
        x += w
    b.append(f'<rect x="{x0}" y="66" width="{bw}" height="30" fill="url(#dots)" opacity=".35"/>')

    # contribution skyline
    sx, sy, sw, sh = 430, 150, 740, 290
    b.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#sky)" stroke="#2E1D66" stroke-width="2"/>')
    ws, _ = web(sx + sw - 10, sy + 10, 200, 6, 4, VIOLET, start=90, sweep=90, width=1, opacity=.5)
    b.append(ws)
    b.append(text("CONTRIBUTION SKYLINE  //  ONE BUILDING PER WEEK", MONO, 12, sx + 16, sy + 26, CYAN, ls=1))
    peak = max(weeks + [1])
    n = len(weeks)
    gw = (sw - 32) / n
    ground = sy + sh - 34
    bodies, lights = [], []
    for i, c in enumerate(weeks):
        bx = sx + 16 + i * gw
        h = 10 + (c / peak) ** .7 * 180 if c else 6
        bodies.append(f"M{num(bx)} {num(ground - h)}h{num(gw - 2)}v{num(h)}h{num(-gw + 2)}z")
        for k in range(min(c, int(h // 9))):
            lights.append(f"M{num(bx + 3)} {num(ground - 8 - k * 9)}h{num(max(gw - 8, 2))}v4h{num(-max(gw - 8, 2))}z")
    b.append(f'<path d="{"".join(bodies)}" fill="#0B0718" stroke="{CYAN}" stroke-width=".8" stroke-opacity=".5"/>')
    b.append(f'<path class="lit" d="{"".join(lights)}" fill="{YELLOW}"/>')
    b.append(f'<rect x="{sx}" y="{ground}" width="{sw}" height="2" fill="{RED}"/>')
    seen = set()
    for i, day in enumerate(first_days):
        m = day[:7]
        if m not in seen and day[8:10] <= "07":
            seen.add(m)
            label = dt.date.fromisoformat(day).strftime("%b").upper()
            b.append(text(label, MONO, 10, sx + 16 + i * gw, ground + 20, MUTED))
    b.append(text(f"PEAK WEEK: {peak}", MONO, 11, sx + sw - 16, sy + 26, YELLOW, "end"))

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y").upper()
    b.append(text(f"LAST SIGNAL: {stamp}  //  REFRESHED DAILY BY GITHUB ACTIONS", MONO, 11, 30, 440, MUTED, ls=.6))
    b.append(text("Public activity only.", BODY, 14, 30, 418, MUTED))
    css = ".lit{animation:lit 3s steps(1) infinite}@keyframes lit{0%,88%,100%{opacity:1}90%{opacity:.4}93%{opacity:1}95%{opacity:.6}}"
    desc = (f"{tiles[0][0]} contributions in the last year, {tiles[1][0]} commits, {tiles[2][0]} pull requests, "
            f"{repos['totalCount']} public repositories. Top languages: " + ", ".join(n for n, _ in top[:5]) + ".")
    return svg_doc(W, H, "".join(b), "The signal — GitHub activity", desc, css, defs)


if __name__ == "__main__":
    try:
        data = fetch()
    except Exception as e:  # keep the last good SVG
        print(f"signal: fetch failed, keeping previous assets/signal.svg ({e})")
        sys.exit(0)
    save("assets/signal.svg", render(data))
