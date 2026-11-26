"""Chapter 9 figures."""
import sys, json
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
R = json.load(open("data/singularity_results.json"))

def fig_9_1():
    t = np.linspace(0, 30, 600); r = 0.35
    fig = plt.figure(figsize=(W, 3.8)); ax = fig.add_axes([0.15, 0.14, 0.82, 0.60])
    for a, ls, lab in [(0.7, (0, (5, 2)), "α = 0.7: ideas get harder to find"), (1.0, "-", "α = 1.0: steady exponential growth"),
                       (1.2, (0, (1.5, 1.5)), "α = 1.2: runaway growth")]:
        if a == 1.0:
            logI = r * t
        else:
            base = 1 + (1 - a) * r * t
            with np.errstate(invalid="ignore", divide="ignore"):
                logI = np.where(base > 0, np.log(base) / (1 - a), np.inf)
        I = np.exp(np.minimum(logI, np.log(1e6)))
        ax.semilogy(t, I, color=c("sing") if a > 1 else (c("asi") if a == 1 else c("agi")), ls=ls, lw=1.9, label=lab)
    ax.axhline(1000, color=GREY, lw=0.8, ls=":")
    ax.text(0.5, 1300, "transition threshold: 1,000 × AGI", ha="left", va="bottom", color=GREY)
    ax.set_xlim(0, 30); ax.set_ylim(0.8, 1e5)
    ax.set_xlabel("Years after AGI"); ax.set_ylabel("Capability (AGI = 1)")
    ax.minorticks_off(); ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.18, 1.0), ncol=1, frameon=False, handlelength=2.4)
    save(fig, OUT, "Fig_9_1_growth_regimes")

def fig_9_2():
    H = 4.6; fig, ax = canvas(H)
    inputs = [("AGI date", "personal forecast,\nChapter 2", "agi"),
              ("Returns α", "0.6 to 1.3", "asi"),
              ("Growth rate r", "median 0.35 per year", "asi"),
              ("Physical limit", "at most about 20×\nper year", "today"),
              ("Quantum factor q", "after error-corrected\nmachines, 2032 to 2042", "quantum")]
    bw, bh = 1.95, 0.66; y = H - 0.08
    for i, (t, d, k) in enumerate(inputs):
        y0 = y - bh
        box(ax, 0.02, y0, bw, bh, d, title=t, k=k, align="left", ls="--" if k == "quantum" else "-")
        arrow(ax, 0.02 + bw, y0 + bh / 2, 2.55, 2.30, color=GREY)
        y = y0 - 0.16
    box(ax, 2.55, 1.55, 1.93, 1.50, "Simulate growth of\ncapability after AGI:\n$dI/dt = r\\,I^{\\alpha}$", title="Monte Carlo model", k="today", align="left")
    arrow(ax, 3.52, 1.55, 3.52, 1.05)
    box(ax, 2.55, 0.10, 1.93, 0.95, "year capability\nreaches 1,000 × AGI", title="Transition date", k="sing", align="left")
    save(fig, OUT, "Fig_9_2_model_structure")

def fig_9_3():
    yrs = R["cdf_years"]
    fig = plt.figure(figsize=(W, 4.0)); ax = fig.add_axes([0.14, 0.30, 0.83, 0.66])
    sty = {"no quantum": (c("sing"), "-", 2.2), "quantum, evidence of Part II": (c("quantum"), (0, (5, 2)), 1.6),
           "quantum, hypothesis": (c("quantum"), (0, (1.5, 1.5)), 1.8)}
    for k, (col, ls, lw) in sty.items():
        ax.plot(yrs, R["cdf"][k], color=col, ls=ls, lw=lw, label=k)
    ax.axvline(2045, color=GREY, lw=0.8)
    ax.text(2045.8, 0.95, "Kurzweil: 2045", va="top", color=GREY)
    ax.axhline(0.5, color=GREY, lw=0.6, ls=":")
    ax.set_xlim(2025, 2150); ax.set_ylim(0, 1)
    ax.set_xlabel("Year"); ax.set_ylabel("Probability of transition by year")
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.legend(loc="lower left", ncol=1, frameon=False, bbox_to_anchor=(0.02, 0.0), handlelength=2.6)
    save(fig, OUT, "Fig_9_3_transition_dates")

def fig_9_4():
    g = R["gap_by_alpha"]; labs = list(g.keys())
    vals = [g[k]["median_years_agi_to_transition"] for k in labs]
    fig = plt.figure(figsize=(W, 3.0)); ax = fig.add_axes([0.14, 0.20, 0.83, 0.74])
    ax.bar(range(len(labs)), vals, 0.6, color=[f("asi"), f("asi"), f("sing"), f("sing")], ec=[c("asi"), c("asi"), c("sing"), c("sing")], lw=1.0)
    for i, v in enumerate(vals):
        ax.text(i, v + 1, f"{v:.0f} years", ha="center", va="bottom")
    ax.set_xticks(range(len(labs))); ax.set_xticklabels([k.replace("-", " to ") for k in labs])
    ax.set_xlabel("Returns to self-improvement, α"); ax.set_ylabel("Median years, AGI to transition")
    ax.set_ylim(0, 62); ax.yaxis.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    save(fig, OUT, "Fig_9_4_returns")

if __name__ == "__main__":
    for fn in (fig_9_1, fig_9_2, fig_9_3, fig_9_4):
        fn()
    print("done")
