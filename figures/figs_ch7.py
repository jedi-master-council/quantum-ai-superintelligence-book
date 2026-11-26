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

E7 = json.load(open("data/lab7_extensions_results.json"))

def fig_7_4():
    R = E7["calibration"]["rows"]; T = [r["duration_ns"] for r in R]
    fl = lambda v: max(v, 1e-7)
    fig = plt.figure(figsize=(W, 3.9)); ax = fig.add_axes([0.15, 0.13, 0.82, 0.60])
    ax.semilogy(T, [fl(r["gaussian_error"]) for r in R], "--s", color=GREY, ms=4, lw=1.3, mfc="white", label="Gaussian pulse from the nominal model")
    ax.semilogy(T, [fl(r["drag_error"]) for r in R], ":^", color=GREY, ms=4, lw=1.5, mfc="white", label="with textbook DRAG correction")
    ax.semilogy(T, [fl(r["learned_error"]) for r in R], "-o", color=c("quantum"), ms=4, lw=1.8, label="tuned by a black-box optimiser")
    ax.axhline(1e-3, color=GREY, lw=0.7, ls=(0, (4, 3))); ax.text(23.8, 8e-4, "error 0.001", ha="right", va="top", color=GREY, fontsize=9.5)
    ax.text(23.8, 1.6e-7, "at or below $10^{-7}$", ha="right", va="bottom", color=c("quantum"), fontsize=9.5)
    ax.set_xlabel("Gate duration (ns)"); ax.set_ylabel("Gate error"); ax.set_xticks(T); ax.set_ylim(5e-8, 0.5); ax.minorticks_off()
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=1, frameon=False)
    save(fig, OUT, "Fig_7_4_learned_calibration")

def fig_7_5():
    C = E7["compilation_search"]; names = list(C)
    labels = ["QFT and inverse\n(6 qubits)", "Bernstein-Vazirani\n(8 + 1 qubits)", "Random mirror\n(8 qubits)"]
    fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0.14, 0.20, 0.84, 0.62])
    x = np.arange(len(names)); w = 0.26
    for k, (key, col, fc, lab) in enumerate([("best_cz", c("quantum"), c("quantum"), "best of 100"), ("median_cz", c("quantum"), f("quantum"), "median"),
                                             ("worst_cz", GREY, "white", "worst of 100")]):
        v = [C[n][key] for n in names]
        ax.bar(x + (k - 1) * w, v, w, color=fc, ec=col, lw=1.0, label=lab)
        for xi, vi in zip(x + (k - 1) * w, v):
            ax.text(xi, vi + 1.5, f"{vi:.0f}", ha="center", va="bottom", fontsize=9.5)
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylabel("Two-qubit gates after compilation"); ax.set_ylim(0, 125)
    ax.yaxis.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=3, frameon=False)
    save(fig, OUT, "Fig_7_5_compilation_search")

if __name__ == "__main__":
    for fn in (fig_7_1, fig_7_2, fig_7_3, fig_7_4, fig_7_5):
        fn()
    print("done")
