"""Chapter 7 figures."""
import sys, json
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
D = json.load(open("data/lab7_results.json"))

def fig_7_1():
    layers = [("Device design", "learned models of qubit\nlayouts and materials", "study"),
              ("Calibration\nand control", "reinforcement learning\ndesigns robust gates", "demo"),
              ("Compilation", "AlphaTensor-Quantum cuts\nT-gate counts", "demo"),
              ("Error mitigation", "learned corrections to noisy\nexpectation values", "demo"),
              ("Error-correction\ndecoding", "AlphaQubit decoders on\nprocessor data, real time", "demo")]
    sty = {"demo": ("quantum", "-", "demonstrated"), "study": ("today", "--", "under study")}
    H = 4.75; fig, ax = canvas(H)
    lw_, rw_ = 1.62, 2.30; lx, rx = 0.02, W - 0.02 - 2.30
    top = H - 0.02
    ax.text(lx, top, "Layer of the quantum stack", va="top", fontweight="bold")
    ax.text(rx, top, "What AI contributes", va="top", fontweight="bold")
    rh = 0.78; y = top - 0.32
    for i, (layer, contrib, st) in enumerate(layers):
        k, ls, lab = sty[st]
        y0 = y - rh
        box(ax, lx, y0 + 0.06, lw_, rh - 0.12, layer, k="quantum", bold=True)
        box(ax, rx, y0 + 0.06, rw_, rh - 0.12, contrib, k=k, ls=ls)
        arrow(ax, rx, y0 + rh / 2, lx + lw_, y0 + rh / 2, color=c(k), ls=(0, (4, 2)) if ls == "--" else "-")
        y = y0
    ax.plot([0.10, 0.50], [0.18, 0.18], color=c("quantum"), lw=1.4)
    ax.text(0.58, 0.18, "demonstrated in published work", va="center")
    ax.plot([2.85, 3.25], [0.18, 0.18], color=c("today"), lw=1.4, ls=(0, (4, 2)))
    ax.text(3.33, 0.18, "under study", va="center")
    save(fig, OUT, "Fig_7_1_ai_quantum_stack")

def fig_7_2():
    r = D["lab7_1"]
    groups = [("Unseen random circuits", r["random_test"]), ("GHZ circuit (never seen)", r["ghz"])]
    fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0.14, 0.14, 0.84, 0.64])
    w = 0.25; x = np.arange(2)
    sty = [("raw", "no correction", "white", c("today")), ("readout", "readout calibration", f("today"), c("today")),
           ("ml", "learned correction", c("quantum"), c("quantum"))]
    for j, (k, lab, fc, ec) in enumerate(sty):
        vals = [g[1][k] for g in groups]
        ax.bar(x + (j - 1) * w, vals, w * 0.92, color=fc, ec=ec, lw=1.0, label=lab)
        for xi, v in zip(x + (j - 1) * w, vals):
            ax.text(xi, v + 0.001, f"{v:.3f}", ha="center", va="bottom")
    ax.set_xticks(x); ax.set_xticklabels([g[0] for g in groups])
    ax.set_ylabel("Distance from ideal result"); ax.set_ylim(0, 0.068)
    ax.yaxis.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, handlelength=1.2, columnspacing=0.8)
    save(fig, OUT, "Fig_7_2_learned_mitigation")

def fig_7_3():
    s = D["lab7_2_sweep"]; q = [x["q"] for x in s]
    fig = plt.figure(figsize=(W, 3.5)); ax = fig.add_axes([0.15, 0.15, 0.82, 0.68])
    ax.plot(q, [x["minimum_weight_logical_error"] for x in s], "o--", color=c("today"), mfc="white", ms=7, lw=1.4, label="minimum-weight decoder")
    ax.plot(q, [x["learned_logical_error"] for x in s], "s-", color=c("quantum"), ms=6, lw=1.8, label="learned decoder")
    for x in s[2:]:
        red = 1 - x["learned_logical_error"] / x["minimum_weight_logical_error"]
        ax.text(x["q"] + 0.002, x["learned_logical_error"] - 0.0015, f"{red * 100:.0f}% fewer", ha="left", va="top")
    ax.set_xlabel("Probability of a correlated pair flip on each neighbouring pair")
    ax.set_ylabel("Logical error rate"); ax.set_xticks(q); ax.set_ylim(0, 0.038); ax.set_xlim(-0.004, 0.098)
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False)
    save(fig, OUT, "Fig_7_3_learned_decoder")

if __name__ == "__main__":
    for fn in (fig_7_1, fig_7_2, fig_7_3):
        fn()
    print("done")
