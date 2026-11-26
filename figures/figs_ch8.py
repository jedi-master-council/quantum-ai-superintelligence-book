"""Chapter 8 figures."""
import sys, json
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
R = json.load(open("data/roadmap_results.json"))

def fig_8_1():
    ms = [("M1", "Agents complete\nweek-long tasks", "today", "Reliability of\nalgorithms", False),
          ("M2", "AI carries out most\nAI research", "today", "Compute for\nexperiments", False),
          ("M3", "AGI: every task,\nbetter and cheaper", "agi", "Energy, materials\nand robotics", True),
          ("M4", "ASI: far beyond\nthe best humans", "asi", "Energy and\nalgorithmic insight", True)]
    H = 5.15; fig, ax = canvas(H)
    top = H - 0.02
    ax.text(0.14, top, "Milestone", va="top", fontweight="bold")
    ax.text(2.02, top, "Binding constraint", va="top", fontweight="bold")
    ax.text(3.50, top, "Quantum\nrelief", va="top", fontweight="bold", linespacing=1.0)
    rh, g = 0.86, 0.36; y = top - 0.50
    for i, (m, t, k, cons, q) in enumerate(ms):
        y0 = y - rh
        box(ax, 0.14, y0, 1.66, rh, t, k=k)
        badge(ax, 0.16, y0 + rh - 0.02, m[1], k=k)
        box(ax, 2.02, y0 + 0.08, 1.30, rh - 0.16, cons, k="today", fill=False)
        arrow(ax, 1.80, y0 + rh / 2, 2.02, y0 + rh / 2, color=GREY)
        if q:
            box(ax, 3.50, y0 + 0.08, 0.98, rh - 0.16, "materials\nand energy", k="quantum", ls="--")
            arrow(ax, 3.50, y0 + rh / 2, 3.32, y0 + rh / 2, color=c("quantum"), ls=(0, (4, 2)))
        else:
            ax.text(3.99, y0 + rh / 2, "none", ha="center", va="center", color=GREY, style="italic")
        if i < 3:
            arrow(ax, 0.97, y0, 0.97, y0 - g)
        y = y0 - g
    save(fig, OUT, "Fig_8_1_roadmap")

def fig_8_2():
    cons = ["Training compute", "Data", "Energy", "Chip manufacturing", "Algorithms", "Robotics", "Capital and regulation"]
    ms = ["M1", "M2", "M3", "M4"]
    # 2 = binding, 1 = important, 0 = minor (author's assessment, Sect. 8.3)
    M = np.array([[1, 2, 1, 2], [1, 1, 1, 1], [0, 1, 2, 2], [1, 1, 1, 1], [2, 1, 1, 2], [0, 0, 2, 1], [1, 1, 1, 1]])
    qrel = [False, False, True, True, False, False, False]
    H = 3.9; fig, ax = canvas(H)
    x0 = 1.72; cw = 0.52; top = H - 0.42; rh = 0.44
    for j, m in enumerate(ms):
        ax.text(x0 + j * cw + cw / 2, H - 0.08, m, ha="center", va="top", fontweight="bold")
    ax.text(x0 + 4 * cw + 0.38, H - 0.08, "Quantum\nrelief", ha="center", va="top", fontweight="bold", linespacing=1.0)
    for i, cname in enumerate(cons):
        y = top - i * rh
        ax.text(0.04, y - rh / 2, cname, va="center")
        for j in range(4):
            v = M[i, j]
            r = [0.05, 0.10, 0.16][v]
            ax.add_patch(Circle((x0 + j * cw + cw / 2, y - rh / 2), r, fc=INK if v == 2 else (GREY if v == 1 else "white"), ec=INK, lw=0.8))
        if qrel[i]:
            ax.text(x0 + 4 * cw + 0.38, y - rh / 2, "possible", ha="center", va="center", color=c("quantum"), fontweight="bold")
        ax.plot([0.02, W - 0.02], [y - rh, y - rh], color="#C5CBD2", lw=0.6)
    ax.plot([0.02, W - 0.02], [top, top], color=INK, lw=0.8)
    ly = 0.12
    for k, (v, t) in enumerate([(2, "binding"), (1, "important"), (0, "minor")]):
        xx = 0.20 + k * 1.25
        r = [0.05, 0.10, 0.16][v]
        ax.add_patch(Circle((xx, ly), r * 0.8, fc=INK if v == 2 else (GREY if v == 1 else "white"), ec=INK, lw=0.8))
        ax.text(xx + 0.22, ly, t, va="center")
    save(fig, OUT, "Fig_8_2_constraint_matrix")

def fig_8_3():
    names = list(R["classical"].keys()); n = len(names)
    cols = ["today", "today", "agi", "asi"]
    fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0.03, 0.15, 0.94, 0.83])
    ax.set_ylim(-0.6, n - 0.3); ax.invert_yaxis(); ax.set_xlim(2025, 2060)
    for i, (nm, k) in enumerate(zip(names, cols)):
        a = R["classical"][nm]; b = R["quantum"][nm]
        ax.text(2025.4, i - 0.34, f"{nm}: median {a['median']:.0f}", va="center")
        ax.plot([a["p10"], a["p90"]], [i + 0.02, i + 0.02], color=c(k), lw=4, solid_capstyle="butt")
        ax.plot([a["median"]], [i + 0.02], "o", color=c(k), ms=7, mec="white")
        ax.plot([b["p10"], b["p90"]], [i + 0.22, i + 0.22], color=c("quantum"), lw=1.6, ls=(0, (3, 1.5)))
        ax.axhline(i + 0.5, color="#C5CBD2", lw=0.6)
    ax.set_yticks([]); [ax.spines[s].set_visible(False) for s in ("left", "right", "top")]
    ax.set_xlabel("Year (bar: 10% to 90%; dashed green: with quantum relief)")
    save(fig, OUT, "Fig_8_3_roadmap_dates")

if __name__ == "__main__":
    for fn in (fig_8_1, fig_8_2, fig_8_3):
        fn()
    print("done")
