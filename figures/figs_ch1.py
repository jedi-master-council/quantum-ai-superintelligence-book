"""Front-matter figures and Chapter 1 figures, drawn at printed size (4.5 in, 11 pt), colour key from figstyle."""
import sys, math
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"

# ------------------------------------------------------------ Front matter Fig. 1: book map
def book_map():
    parts = [("Part I. The quantum superintelligence hypothesis", "agi",
              ["Hypothesis and scorecard", "When will AGI arrive?", "First circuit on hardware", "Testing quantum power"],
              ["Scorecard for claims", "Personal AGI forecast", "First hardware run", "Benchmarking method"]),
             ("Part II. Quantum machine intelligence", "quantum",
              ["Quantum neural networks", "Why quantum AI is hard", "AI building quantum computers"],
              ["Trained quantum classifier", "Skill in spotting hype", "AI-for-quantum lab"]),
             ("Part III. Minds, brains and the singularity", "asi",
              ["A build roadmap to ASI", "Dating the singularity", "The quantum brain"],
              ["Superintelligence roadmap", "Dated singularity model", "Brain-emulation timeline"]),
             ("Part IV. Living with quantum superintelligence", "secure",
              ["Securing and controlling", "Watchlist 2030 to 2050"],
              ["Threat model", "Post-quantum lab", "Personal watchlist"])]
    links = ["what today's machines can and cannot do", "the limits of quantum learning", "dated estimates to monitor"]
    LH, HEAD, GAP = 0.245, 0.34, 0.40
    hs = [HEAD + LH * max(len(p[2]), len(p[3])) + 0.24 for p in parts]
    H = sum(hs) + GAP * 3 + 0.04
    fig, ax = canvas(H)
    y = H - 0.02; n = 1
    for i, (title, k, chs, gains) in enumerate(parts):
        h = hs[i]; y0 = y - h
        ax.add_patch(Rectangle((0.02, y0), W - 0.04, h, fc="white", ec=c(k), lw=LW, zorder=1))
        ax.add_patch(Rectangle((0.02, y - HEAD), W - 0.04, HEAD, fc=f(k), ec=c(k), lw=LW, zorder=1))
        ax.add_patch(Rectangle((0.02, y - HEAD), 0.07, HEAD, fc=c(k), ec="none", zorder=2))
        ax.text(0.18, y - HEAD / 2, title, va="center", fontweight="bold")
        for j, ch in enumerate(chs):
            yy = y - HEAD - 0.17 - j * LH
            badge(ax, 0.25, yy, str(n), k=k, r=0.1); n += 1
            ax.text(0.42, yy, ch, va="center")
        gy = y - HEAD - 0.06
        ax.add_patch(Rectangle((2.54, y0 + 0.07), 1.88, gy - y0 - 0.07, fc=f(k), ec="none", zorder=1))
        for j, g in enumerate(gains):
            ax.text(2.64, gy - 0.11 - j * LH, g, va="center")
        if i < 3:
            arrow(ax, 0.25, y0, 0.25, y0 - GAP)
            ax.text(0.42, y0 - GAP / 2, "carries forward " + links[i], va="center", style="italic", color=GREY)
        y = y0 - GAP
    save(fig, OUT, "FrontMatter_Fig_1_book_map")

# ------------------------------------------------------------ Front matter Fig. 2: colour key
def colour_key():
    rows = [("today", "Today's AI and classical\ncomputing", "Stage 1 of Fig. 1.1; classical\nbaselines; evidence"),
            ("agi", "Artificial general\nintelligence (AGI)", "Stage 2 of Fig. 1.1; AGI\nforecasts; Part I"),
            ("asi", "Superintelligence (ASI)", "Stage 3 of Fig. 1.1; the\nintelligence explosion; Part III"),
            ("sing", "Technological singularity", "Stage 4 of Fig. 1.1; singularity\nmodels and dates"),
            ("quantum", "Quantum hardware and\nquantum AI", "Quantum processors, circuits\nand Claims A to C; Part II"),
            ("mind", "Minds and brains", "Quantum mind; brain\nemulation; interfaces"),
            ("secure", "Security, control and\ngovernance", "Threats, safeguards and\nregulation; Part IV"),
            ("missing", "Missing or unconfirmed\ninformation", "Results not yet shown;\ninformation still needed")]
    RH, HD = 0.50, 0.30
    H = HD + RH * len(rows) + 0.04
    fig, ax = canvas(H)
    X0, X1, X2 = 0.02, 0.60, 2.42
    top = H - 0.02
    ax.add_patch(Rectangle((X0, top - HD), W - 0.04, HD, fc="#E9ECEF", ec="none"))
    for x, t in [(X0 + 0.06, "Colour"), (X1 + 0.06, "Stands for"), (X2 + 0.06, "Where it appears")]:
        ax.text(x, top - HD / 2, t, va="center", fontweight="bold")
    ax.plot([X0, W - 0.02], [top, top], color=INK, lw=1.0)
    ax.plot([X0, W - 0.02], [top - HD, top - HD], color=INK, lw=0.7)
    for i, (k, m, wh) in enumerate(rows):
        y1 = top - HD - i * RH; y0 = y1 - RH
        ax.add_patch(FancyBboxPatch((X0 + 0.08, y0 + 0.08), 0.42, RH - 0.16, boxstyle="round,pad=0,rounding_size=0.03",
                                    fc=f(k), ec=c(k), lw=1.6, ls="--" if k == "missing" else "-"))
        ax.text(X1 + 0.06, (y0 + y1) / 2, m, va="center", linespacing=1.05)
        ax.text(X2 + 0.06, (y0 + y1) / 2, wh, va="center", linespacing=1.05)
        ax.plot([X0, W - 0.02], [y0, y0], color=INK if i == len(rows) - 1 else "#C5CBD2", lw=1.0 if i == len(rows) - 1 else 0.6)
    for x in (X1, X2):
        ax.plot([x, x], [top - HD - RH * len(rows), top], color="#C5CBD2", lw=0.6)
    save(fig, OUT, "FrontMatter_Fig_2_colour_key")

# ------------------------------------------------------------ Fig. 1.1
def fig_1_1():
    H = 6.0; fig, ax = canvas(H)
    T = H - 0.42
    sx, sw, sh, gap = 0.12, 1.76, 0.52, 0.90
    pb = T - (4 * sh + 3 * gap) - 0.12
    panel(ax, 0.02, pb, 2.10, H - 0.02 - pb, "Capability path")
    panel(ax, 2.40, pb, 2.08, H - 0.02 - pb, "Quantum claims tested", k="quantum")
    stages = [("Today's AI: foundation\nmodels and agents", "today"), ("Artificial general\nintelligence (AGI)", "agi"),
              ("Superintelligence\n(ASI)", "asi"), ("Technological\nsingularity", "sing")]
    ys = []
    for i, (s_, k) in enumerate(stages):
        y0 = T - sh - i * (sh + gap); ys.append(y0)
        box(ax, sx, y0, sw, sh, s_, k=k)
        badge(ax, sx + 0.02, y0 + sh - 0.02, str(i + 1), k=k)
    trans = ["general ability across\nhuman tasks", "abilities beyond the\nbest human minds", "self-improvement\noutruns prediction"]
    axx = 1.70; mids = []
    for i in range(3):
        y1 = ys[i]; y2 = ys[i + 1] + sh
        arrow(ax, axx, y1, axx, y2)
        m = (y1 + y2) / 2; mids.append(m)
        ax.text(axx - 0.1, m, trans[i], ha="right", va="center", style="italic", color=GREY, linespacing=1.1)
    claims = [("Claim A  Acceleration", "Quantum hardware speeds\nup AI enough to bring\nAGI forward\nTested in Chapters 4 to 8"),
              ("Claim B  Necessity", "General intelligence\nneeds quantum effects\nor quantum hardware\nTested in Chapter 10"),
              ("Claim C  Trigger", "Quantum-enabled AI\nstarts a self-improving\nrunaway\nTested in Chapters 7 and 9")]
    cx, cw, ch = 2.50, 1.88, 1.28
    bx = 2.00
    targets = [(mids[0], axx + 0.04), (ys[1] + sh / 2, sx + sw), ((mids[1] + mids[2]) / 2, bx)]
    centres = [T - 0.85, T - 2.25, T - 3.65]
    G = c("quantum")
    for (t, b), cm, (tg, xe) in zip(claims, centres, targets):
        box(ax, cx, cm - ch / 2, cw, ch, b, title=t, k="quantum", align="left")
        chan = 2.24
        ax.plot([cx, chan, chan], [cm, cm, tg], color=G, lw=1.1, ls=(0, (4, 2)), zorder=3)
        arrow(ax, chan, tg, xe + 0.01, tg, color=G, ls=(0, (4, 2)))
    ax.plot([bx, bx], [mids[2], mids[1]], color=G, lw=1.4, zorder=3)
    for m in (mids[1], mids[2]):
        ax.plot([axx + 0.03, bx], [m, m], color=G, lw=1.4, zorder=3)
    box(ax, 0.02, 0.0, W - 0.04, 0.44, "Evidence: complexity theory, hardware results, neuroscience, labs", k="today")
    arrow(ax, 3.44, 0.44, 3.44, pb, color=GREY)
    save(fig, OUT, "Fig_1_1_quantum_superintelligence_hypothesis")

# ------------------------------------------------------------ Fig. 1.2 strands
def fig_1_2():
    lanes = [("Intelligence\nexplosion", "asi"), ("Quantum\ncomputing", "quantum"),
             ("Quantum\nmind", "mind"), ("Quantum\nmachine\nlearning", "quantum")]
    ev = [(1965, 0, "Good"), (1982, 1, "Feynman"), (1989, 2, "Penrose"), (1993, 0, "Vinge"), (1994, 1, "Shor"),
          (1996, 1, "Grover"), (2000, 2, "Tegmark"), (2005, 0, "Kurzweil"), (2014, 0, "Bostrom"),
          (2014, 2, "Hameroff\nand Penrose"), (2017, 3, "Biamonte"), (2018, 1, "Preskill"), (2018, 3, "McClean"),
          (2019, 3, "Tang"), (2025, 1, "Google\nQuantum AI")]
    years = sorted(set(e[0] for e in ev))
    rh = {y: (0.42 if any(e[0] == y and "\n" in e[2] for e in ev) else 0.27) for y in years}
    adds = [("Runaway", "machines that\nredesign\nthemselves", "Claim C"),
            ("Power", "far more\ncomputing\nfor AI", "Claim A"),
            ("Mind", "thought may\nrequire\nquantum\nphysics", "Claim B"),
            ("Methods", "quantum\nlearning\nalgorithms", "Claim A")]
    LX, LWd = 0.46, 1.005
    HEAD = 0.66; body = sum(rh.values()); ADD = 1.48; GAPA = 0.34; HB = 0.50
    H = HEAD + body + 0.10 + ADD + GAPA + HB + 0.02
    fig, ax = canvas(H)
    top = H - 0.02
    grid = "#C5CBD2"
    for j, (name, k) in enumerate(lanes):
        x = LX + j * LWd
        ax.add_patch(Rectangle((x, top - HEAD - body), LWd, HEAD + body, fc=f(k), ec="none", alpha=0.55, zorder=0))
        ax.text(x + LWd / 2, top - 0.02, name, ha="center", va="top", fontweight="bold", linespacing=1.0)
        ax.add_patch(Rectangle((x, top - HEAD), LWd, 0.05, fc=c(k), ec="none", zorder=2))
    ax.text(0.04, top - 0.02, "Year", va="top", fontweight="bold")
    # grid: horizontal rule under every year row, vertical rules between lanes
    y = top - HEAD
    ax.plot([0.02, W - 0.02], [y, y], color=INK, lw=0.8, zorder=1)
    for yr in years:
        h = rh[yr]; ym = y - h / 2
        ax.text(0.04, ym, str(yr), va="center")
        for e in ev:
            if e[0] == yr:
                j = e[1]; x = LX + j * LWd; k = lanes[j][1]
                ax.add_patch(FancyBboxPatch((x + 0.05, y - h + 0.035), LWd - 0.10, h - 0.07, boxstyle="round,pad=0,rounding_size=0.03",
                                            fc="white", ec=c(k), lw=LW, zorder=3))
                ax.text(x + LWd / 2, ym, e[2], ha="center", va="center", zorder=4, linespacing=1.0)
        y -= h
        ax.plot([0.02, W - 0.02], [y, y], color=grid, lw=0.6, zorder=1)
    for j in range(5):
        x = LX + j * LWd
        ax.plot([x, x], [y, top - 0.0], color=grid, lw=0.6, zorder=1)
    ax.plot([0.02, W - 0.02], [y, y], color=INK, lw=0.8, zorder=1)
    # contribution boxes
    y -= 0.10
    ax.text(0.04, y - 0.10, "Adds", va="top", fontweight="bold")
    for j, (t, b, cl) in enumerate(adds):
        x = LX + j * LWd; k = lanes[j][1]
        y0 = y - ADD
        ax.add_patch(FancyBboxPatch((x + 0.05, y0), LWd - 0.10, ADD, boxstyle="round,pad=0,rounding_size=0.03", fc=f(k), ec=c(k), lw=1.1, zorder=2))
        ax.text(x + LWd / 2, y - 0.07, t, ha="center", va="top", fontweight="bold", zorder=3)
        ax.text(x + LWd / 2, y - 0.30, b, ha="center", va="top", linespacing=1.05, zorder=3)
        ax.add_patch(FancyBboxPatch((x + 0.16, y0 + 0.07), LWd - 0.32, 0.24, boxstyle="round,pad=0,rounding_size=0.03", fc="white", ec=c("quantum"), lw=1.0, zorder=3))
        ax.text(x + LWd / 2, y0 + 0.19, cl, ha="center", va="center", zorder=4)
        arrow(ax, x + LWd / 2, y0, x + LWd / 2, HB, color=c(k))
    box(ax, 0.02, 0.0, W - 0.04, HB, "The quantum superintelligence hypothesis\n(three claims, Fig. 1.1)", k="today", fill=False, lw=1.3, bold=True)
    save(fig, OUT, "Fig_1_2_four_strands")

# ------------------------------------------------------------ Fig. 1.3 forecasts
def fig_1_3():
    rows = [("Vinge (1993)", "superhuman intelligence\nwithin thirty years", None, 2023, "asi"),
            ("Kurzweil (2005, 2024)", "human-level AI", None, 2029, "agi"),
            ("Grace et al. (2025)", "machines beat humans\nat every task", 2027, 2047, "agi"),
            ("Kurzweil (2005, 2024)", "singularity", None, 2045, "sing"),
            ("Grace et al. (2025)", "all occupations\nautomatable", 2037, 2116, "agi")]
    fig = plt.figure(figsize=(W, 4.6))
    ax = fig.add_axes([0.385, 0.25, 0.585, 0.74])
    n = len(rows)
    ax.set_xlim(2015, 2125); ax.set_ylim(-0.5, n - 0.5); ax.invert_yaxis()
    ax.axvspan(2015, 2026, color="#E9ECEF", zorder=0)
    ax.axvline(2026, color=INK, lw=1.0, zorder=1)
    ax.text(2027.5, -0.40, "2026", va="top", ha="left", style="italic")
    for i in range(n + 1):
        ax.axhline(i - 0.5, color="#C5CBD2", lw=0.6, zorder=0)
    for x in (2040, 2060, 2080, 2100, 2120):
        ax.axvline(x, color="#E1E5EA", lw=0.6, zorder=0)
    labs = []
    for i, (who, what, lo, hi, k) in enumerate(rows):
        col = c(k)
        labs.append(f"{who}\n{what}")
        if lo:
            ax.plot([lo, hi], [i, i], color=col, lw=3.2, solid_capstyle="butt", zorder=3)
            ax.plot([lo], [i], marker="|", ms=12, mew=2, color=col, zorder=3)
            ax.plot([hi], [i], marker="o", ms=7, color=col, zorder=4)
            ax.text(lo, i + 0.30, str(lo), ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)
            ax.text(hi, i + 0.30, str(hi), ha="center" if hi < 2110 else "right", va="center", bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)
        else:
            ax.plot([hi], [i], marker="o", ms=7.5, color=col, zorder=4)
            if hi < 2026:
                ax.text(2028, i, f"{hi}: date has passed", va="center", bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)
            else:
                ax.text(hi + 2.5, i, str(hi), va="center", bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)
    ax.set_yticks(range(n)); ax.set_yticklabels(labs, linespacing=1.05)
    ax.tick_params(axis="y", length=0, pad=4)
    ax.set_xticks([2020, 2040, 2060, 2080, 2100, 2120])
    [ax.spines[s_].set_visible(False) for s_ in ("left", "right", "top")]
    # legend beneath
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    h1 = [Line2D([], [], marker="o", ls="", color=INK, ms=6, label="one forecaster's date"),
          Line2D([], [], marker="|", ls="-", color=INK, ms=9, mew=2, lw=2.5, label="survey: 10% to 50% chance")]
    h2 = [Patch(fc="#E9ECEF", label="years already passed"), Patch(fc=c("agi"), label="AGI (Stage 2)"),
          Patch(fc=c("asi"), label="ASI (Stage 3)"), Patch(fc=c("sing"), label="singularity (Stage 4)")]
    hh = [h1[0], h2[0], h1[1], h2[1], h2[2], h2[3]]
    fig.legend(handles=[h1[0], h1[1], h2[0], h2[1], h2[2], h2[3]], loc="lower center", bbox_to_anchor=(0.5, 0.0),
               frameon=False, ncol=2, handlelength=1.8, columnspacing=1.2)
    save(fig, OUT, "Fig_1_3_published_forecasts")

# ------------------------------------------------------------ Fig. 1.4 break-even
def fig_1_4():
    RQ = 1e3; RC = [1e9, 1e12]
    N = np.logspace(6, 20, 400)
    fig = plt.figure(figsize=(W, 4.5))
    ax = fig.add_axes([0.15, 0.27, 0.70, 0.71])
    ax.loglog(N, (math.pi / 4) * np.sqrt(N) / RQ, color=c("quantum"), lw=2.0, label="quantum, 1,000 steps/s")
    for rc, col, ls, lab in zip(RC, [GREY, INK], [(0, (6, 2)), (0, (7, 2, 1.5, 2))], ["classical, $10^{9}$/s", "classical, $10^{12}$/s"]):
        ax.loglog(N, N / rc, color=col, lw=1.8, ls=ls, label=lab)
        ns = ((math.pi / 4) * rc / RQ) ** 2
        ax.plot([ns], [ns / rc], "o", color=INK, ms=5.5, zorder=5)
    ax.annotate("break-even\nafter 10 min", xy=(6.2e11, 617), xytext=(1e8, 3e4), ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7), linespacing=1.0)
    ax.annotate("break-even\nafter 7 days", xy=(6.2e17, 6.2e5), xytext=(1e17, 1.0), ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7), linespacing=1.0)
    ax.set_xlim(1e6, 1e20); ax.set_ylim(1e-3, 1e9)
    ax.set_xticks([1e6, 1e10, 1e14, 1e18]); ax.set_yticks([1e-3, 1, 1e3, 1e6, 1e9])
    ax.set_xlabel("Number of candidates to search, $N$"); ax.set_ylabel("Time to finish (seconds)")
    ax.legend(loc="upper left", bbox_to_anchor=(-0.2, -0.13), frameon=False, handlelength=2.4)
    ax.minorticks_off(); ax.spines["top"].set_visible(False)
    ax.grid(True, which="major", color="#C5CBD2", lw=0.5, ls=(0, (1, 2)))
    ax.set_axisbelow(True)
    r = ax.twinx(); r.set_yscale("log"); r.set_ylim(ax.get_ylim()); r.minorticks_off()
    r.set_yticks([3600, 86400, 3.156e7]); r.set_yticklabels(["1 hour", "1 day", "1 year"]); r.spines["top"].set_visible(False)
    save(fig, OUT, "Fig_1_4_quadratic_break_even")

# ------------------------------------------------------------ Fig. 1.5 loop
def fig_1_5():
    H = 5.55; fig, ax = canvas(H)
    CW = 1.38; LX = 0.02; RX = W - 0.02 - CW
    HEADH = 0.40
    top = H - 0.02
    # column headers
    box(ax, LX, top - HEADH, CW, HEADH, "AI systems", k="today", bold=True, lw=1.2)
    box(ax, RX, top - HEADH, CW, HEADH, "Quantum hardware", k="quantum", bold=True, lw=1.2)
    links = [("Neural-network\ndecoders", "Error\ncorrection", "R", "demo", "shown on real\nprocessor data"),
             ("Learned control\nand tuning", "Qubit\ncalibration", "R", "study", "reviewed in\nChapter 7"),
             ("Learned circuit\noptimisation", "Compilation\nand routing", "R", "study", "reviewed in\nChapter 7"),
             ("Model training\nand inference", "Quantum\nalgorithms", "L", "none", "no speed-up\nshown at scale"),
             ("New training\ndata", "Simulation of\nmolecules", "L", "study", "narrow cases,\nChapter 7")]
    sty = {"demo": (c("quantum"), "-", 1.8), "study": (GREY, (0, (1.5, 2)), 1.4), "none": (c("missing"), (0, (5, 2.5)), 1.8)}
    rh, g = 0.56, 0.16
    y = top - HEADH - 0.30
    ax.text(W / 2, y + 0.12, "AI improves quantum hardware", ha="center", va="center", fontweight="bold")
    ys = []
    for i, (l, r, d, st, lab) in enumerate(links):
        if i == 3:
            y -= 0.34
            ax.text(W / 2, y + 0.16, "Quantum hardware improves AI", ha="center", va="center", fontweight="bold")
        y0 = y - rh
        box(ax, LX, y0, CW, rh, l, k="today")
        box(ax, RX, y0, CW, rh, r, k="quantum")
        col, ls, lw = sty[st]
        ym = y0 + rh / 2 - 0.06
        if d == "R":
            arrow(ax, LX + CW, ym, RX, ym, color=col, ls=ls, lw=lw)
        else:
            arrow(ax, RX, ym, LX + CW, ym, color=col, ls=ls, lw=lw)
        ax.text(W / 2, ym + 0.05, lab, ha="center", va="bottom", linespacing=1.0, fontsize=FS)
        ys.append(y0); y = y0 - g
    # legend
    ly = y - 0.06
    items = [("demo", "demonstrated"), ("study", "under study"), ("none", "not shown")]
    x = 0.08
    for st, t in items:
        col, ls, lw = sty[st]
        ax.plot([x, x + 0.42], [ly, ly], color=col, ls=ls, lw=lw)
        ax.text(x + 0.50, ly, t, va="center")
        x += 1.50
    # claim C box
    box(ax, 0.02, 0.0, W - 0.04, 0.60, "Claim C (Fig. 1.1) needs both directions to deliver gains\nthat grow with each cycle. Only the first row is shown today.",
        k="quantum", fill=False, lw=1.2)
    save(fig, OUT, "Fig_1_5_ai_quantum_loop")

# ------------------------------------------------------------ Fig. 1.6 four-question test
def fig_1_6():
    H = 6.6; fig, ax = canvas(H)
    qx, qw = 0.02, 2.78
    steps = [("New announcement", "about quantum AI", None),
             ("1  Which claim?", "Decide whether it bears on\nClaim A, B or C", "today"),
             ("2  Classical baseline?", "Is the best classical method\nreported for comparison?", "today"),
             ("3  Full costs?", "Are data loading, error\ncorrection and repetitions\nall counted?", "today"),
             ("4  Scale that matters?", "Is the task one that limits\nAI progress, at useful size?", "today"),
             ("Record the evidence", "Enter it as supporting or\ncounting against the claim\nin Table 1.1", "agi")]
    hs = [0.56, 0.78, 0.78, 0.98, 0.78, 0.98]
    g = (H - 0.04 - sum(hs)) / 5
    y = H - 0.02; pos = []
    for (t, b, k), h in zip(steps, hs):
        y0 = y - h
        box(ax, qx, y0, qw, h, b, title=t, k=k or "today", fill=k is not None, align="left", lw=1.2 if k in (None, "agi") else LW)
        pos.append((y0, h)); y = y0 - g
    for i in range(5):
        ya = pos[i][0]; yb = pos[i + 1][0] + pos[i + 1][1]
        arrow(ax, 0.5, ya, 0.5, yb)
        if i >= 2:
            ax.text(0.62, (ya + yb) / 2, "yes", va="center", style="italic", color=GREY)
    rx, rw = 3.22, W - 3.22 - 0.02
    y2 = pos[2][0] + pos[2][1] / 2; y3 = pos[3][0] + pos[3][1] / 2; y4 = pos[4][0] + pos[4][1] / 2
    top_b = y2 + 0.42; bot_b = y3 - 0.62
    box(ax, rx, bot_b, rw, top_b - bot_b, "Cannot be\njudged yet.\nNote what is\nmissing and\nask for it.", k="missing", ls="--", lw=1.2)
    for yy in (y2, y3):
        arrow(ax, qx + qw, yy, rx, yy, color=c("missing"))
        ax.text((qx + qw + rx) / 2, yy + 0.04, "no", ha="center", va="bottom", style="italic", color=GREY)
    box(ax, rx, y4 - 0.48, rw, 0.96, "Narrow result.\nIt does not\nmove the\nclaim.", k="today", fill=False, lw=1.2)
    arrow(ax, qx + qw, y4, rx, y4, color=GREY)
    ax.text((qx + qw + rx) / 2, y4 + 0.04, "no", ha="center", va="bottom", style="italic", color=GREY)
    save(fig, OUT, "Fig_1_6_judging_an_announcement")

if __name__ == "__main__":
    for fn in (book_map, colour_key, fig_1_1, fig_1_2, fig_1_3, fig_1_4, fig_1_5, fig_1_6):
        fn()
    print("done")
