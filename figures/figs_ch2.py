"""Chapter 2 figures."""
import sys, json, importlib.util
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
LAB = sys.argv[2] if len(sys.argv) > 2 else "../labs/chapter-02/agi_forecast.py"

def load_lab():
    spec = importlib.util.spec_from_file_location("lab", LAB); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def fig_2_1():
    pts = [("Dartmouth proposal", 1955, 1956, "agi", True), ("Turing", 1950, 2000, "agi", True),
           ("Simon", 1965, 1985, "agi", True), ("Vinge", 1993, 2023, "asi", True),
           ("Kurzweil", 1999, 2029, "agi", False), ("Kurzweil", 2005, 2045, "sing", False),
           ("Grace et al. survey", 2016, 2061, "agi", False), ("Grace et al. survey", 2023, 2047, "agi", False)]
    fig = plt.figure(figsize=(W, 3.9)); ax = fig.add_axes([0.13, 0.25, 0.84, 0.72])
    ax.axhspan(15, 25, color="#F1F3F5", zorder=0)
    ax.text(1947, 24.4, "15 to 25 years ahead", va="top", style="italic", color=GREY)
    off = {"Dartmouth proposal": (2, -1, "left"), "Turing": (2, 0, "left"), "Simon": (2, -2.5, "left"), "Vinge": (-2, 2.5, "right"),
           ("Kurzweil", 1999): (2, -3, "left"), ("Kurzweil", 2005): (2, 2.4, "left"),
           ("Grace et al. survey", 2016): (-2, 2.5, "right"), ("Grace et al. survey", 2023): (-1.5, -4, "right")}
    for name, made, target, k, passed in pts:
        ahead = target - made
        ax.plot([made], [ahead], marker="o", ms=8, color=c(k) if not passed else "white", mec=c(k), mew=1.8, zorder=4)
        dx, dy, ha = off.get((name, made), off.get(name))
        ax.text(made + dx, ahead + dy, f"{name} ({made})", ha=ha, va="center", bbox=dict(fc="white", ec="none", pad=0.5), zorder=5)
    ax.set_xlim(1945, 2030); ax.set_ylim(-3, 52)
    ax.set_xlabel("Year the prediction was made"); ax.set_ylabel("Years ahead predicted")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", ms=7, mfc="white", mec=INK, mew=1.5, label="date has passed"),
         Line2D([], [], marker="o", ls="", ms=7, color=INK, label="date still ahead"),
         Line2D([], [], marker="s", ls="", ms=7, color=c("agi"), label="AGI"),
         Line2D([], [], marker="s", ls="", ms=7, color=c("asi"), label="ASI"),
         Line2D([], [], marker="s", ls="", ms=7, color=c("sing"), label="singularity")]
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0), columnspacing=1.0, handletextpad=0.4)
    save(fig, OUT, "Fig_2_1_historical_predictions")

def fig_2_2():
    H = 5.3; fig, ax = canvas(H)
    cols = [("Ask the experts", "Surveys and\nindividual\npredictions",
             "Experts' judgement\nreflects the field's\nunderstanding", "Answers shift\nwith the wording\nof the question"),
            ("Extrapolate inputs", "Training compute,\ndata, investment",
             "Capability follows\ninputs; a compute\nthreshold exists", "The threshold is\nunknown; trends\ncan bend"),
            ("Extrapolate outputs", "Benchmarks; length\nof tasks agents\ncomplete",
             "The measured trend\ncontinues to a\ngeneral level", "Benchmarks\nsaturate; narrow\ntasks mislead")]
    cw = 1.42; gap = (W - 0.04 - 3 * cw) / 2
    rows = [("Input", 0.80), ("Assumes", 0.80), ("Fails when", 0.80)]
    top = H - 0.14
    for j, (t, a, b, d) in enumerate(cols):
        x = 0.02 + j * (cw + gap)
        box(ax, x, top - 0.42, cw, 0.42, t, k="agi", bold=True, lw=1.1)
        badge(ax, x + 0.02, top - 0.02, str(j + 1), k="agi")
        y = top - 0.42 - 0.14
        for (lab, h), txt, kk in zip(rows, (a, b, d), ("today", "today", "missing")):
            ax.text(x + 0.06, y - 0.02, lab, va="top", style="italic", color=GREY)
            box(ax, x, y - 0.22 - h, cw, h, txt, k=kk, ls="--" if kk == "missing" else "-")
            y = y - 0.22 - h - 0.10
        arrow(ax, x + cw / 2, y + 0.10, x + cw / 2, 0.62)
    box(ax, 0.02, 0.0, W - 0.04, 0.62, "Personal forecast: the three distributions\ncombined with weights chosen by the reader", k="agi", bold=False, lw=1.3)
    save(fig, OUT, "Fig_2_2_three_methods")

def fig_2_3():
    r = json.load(open("data/agi_forecast_results.json"))
    yrs = r["cdf_years"]
    fig = plt.figure(figsize=(W, 4.3)); ax = fig.add_axes([0.14, 0.33, 0.83, 0.64])
    sty = [("survey", (0, (6, 2)), 1.6, "Method 1: expert survey"), ("compute", (0, (1.5, 1.5)), 1.8, "Method 2: compute threshold"),
           ("horizon", (0, (7, 2, 1.5, 2)), 1.6, "Method 3: task-horizon trend"), ("combined", "-", 2.6, "Combined, equal weights")]
    for k, ls, lw, lab in sty:
        ax.plot(yrs, r["cdf"][k], color=c("agi") if k == "combined" else INK if k != "survey" else GREY, ls=ls, lw=lw, label=lab)
    ax.axhline(0.5, color=GREY, lw=0.7)
    ax.text(2099, 0.52, "50%", ha="right", va="bottom", color=GREY)
    ax.set_xlim(2025, 2100); ax.set_ylim(0, 1)
    ax.set_xlabel("Year"); ax.set_ylabel("Probability AGI by year")
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.legend(loc="lower left", ncol=1, frameon=False, bbox_to_anchor=(0.02, 0.0), handlelength=2.6)
    ax.set_xticks([2030, 2050, 2070, 2090])
    save(fig, OUT, "Fig_2_3_forecast_distributions")

def fig_2_4():
    m = load_lab()
    def run(fn, **kw):
        for k, v in kw.items(): setattr(m, k, v)
        m.RNG = np.random.default_rng(2026)
        return m.summary(fn())
    base = dict(REQUIRED_OOM_LOG10_MEDIAN=4.0, DOUBLING_MONTHS=(4.0, 12.0))
    rows = [("Compute: 2 orders of magnitude needed", run(m.compute, **{**base, "REQUIRED_OOM_LOG10_MEDIAN": 2.0})),
            ("Compute: 4 orders of magnitude (default)", run(m.compute, **base)),
            ("Compute: 6 orders of magnitude needed", run(m.compute, **{**base, "REQUIRED_OOM_LOG10_MEDIAN": 6.0})),
            ("Horizon: doubling 4 to 12 months (default)", run(m.horizon, **base)),
            ("Horizon: doubling 10 to 20 months", run(m.horizon, **{**base, "DOUBLING_MONTHS": (10.0, 20.0)}))]
    json.dump({n: s for n, s in rows}, open("data/agi_sensitivity.json", "w"), indent=1)
    fig = plt.figure(figsize=(W, 3.5)); ax = fig.add_axes([0.04, 0.14, 0.92, 0.84])
    n = len(rows); ax.set_ylim(-0.6, n - 0.2); ax.invert_yaxis(); ax.set_xlim(2024, 2052)
    for i, (lab, s) in enumerate(rows):
        ax.text(2024.4, i - 0.36, f"{lab}: median {s['median']:.0f}", va="center")
        ax.plot([s["p10"], s["p90"]], [i, i], color=c("agi"), lw=3, solid_capstyle="butt")
        ax.plot([s["median"]], [i], "o", color=c("agi"), ms=7, mec="white", mew=1)
        ax.axhline(i + 0.5, color="#C5CBD2", lw=0.6)
    ax.set_yticks([]); [ax.spines[k].set_visible(False) for k in ("left", "right", "top")]
    ax.set_xlabel("Year (bar: 10% to 90% range; dot: median)")
    save(fig, OUT, "Fig_2_4_sensitivity")

if __name__ == "__main__":
    for fn in (fig_2_1, fig_2_2, fig_2_3, fig_2_4):
        fn()
    print("done")
