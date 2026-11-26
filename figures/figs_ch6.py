"""Chapter 6 figures."""
import sys, json
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
D = json.load(open("data/lab6_results.json"))

def fig_6_1():
    rows = [("Loading data", "Classical data must\nbe written into\namplitudes; the cost\ncan cancel the gain", "Quantum data from\nsensors and\nsimulation;\nstructured inputs", "missing"),
            ("Barren plateaus", "Gradients vanish\nexponentially as\nqubits are added", "Local costs, shallow\ncircuits, careful\ninitialisation", "today"),
            ("Dequantisation", "Classical algorithms\nmatch the claimed\nspeed-up", "Tasks with proven\nseparations; quantum\ndata", "missing"),
            ("Noise", "Errors accumulate\nwith circuit depth", "Error mitigation now;\nerror correction later", "today")]
    H = 5.75; fig, ax = canvas(H)
    cx = [0.02, 1.30, 2.96]; cw = [1.16, 1.56, 1.52]
    top = H - 0.02
    for x, w, t in zip(cx, cw, ["Barrier", "Why it matters", "Research response"]):
        ax.text(x + 0.04, top, t, va="top", fontweight="bold")
    ax.plot([0.02, W - 0.02], [top - 0.28, top - 0.28], color=INK, lw=0.9)
    rh = 1.25; y = top - 0.36
    for i, (b, why, resp, k) in enumerate(rows):
        y0 = y - rh
        box(ax, cx[0], y0 + 0.08, cw[0], rh - 0.16, b, k="quantum", bold=True)
        box(ax, cx[1], y0 + 0.08, cw[1], rh - 0.16, why, k="today", fill=False)
        box(ax, cx[2], y0 + 0.08, cw[2], rh - 0.16, resp, k=k, ls="--" if k == "missing" else "-")
        arrow(ax, cx[0] + cw[0], y0 + rh / 2, cx[1], y0 + rh / 2, color=GREY)
        arrow(ax, cx[1] + cw[1], y0 + rh / 2, cx[2], y0 + rh / 2, color=GREY)
        y = y0
        if i < 3:
            ax.plot([0.02, W - 0.02], [y, y], color="#C5CBD2", lw=0.6)
    save(fig, OUT, "Fig_6_1_barriers")

def fig_6_2():
    r = D["rows"]; n = [x["n"] for x in r]
    fig = plt.figure(figsize=(W, 4.1)); ax = fig.add_axes([0.15, 0.30, 0.82, 0.66])
    sty = [("deep_global", "deep circuit, global cost", "-", "s", c("quantum"), c("quantum")),
           ("shallow_global", "shallow circuit, global cost", "--", "s", c("quantum"), "white"),
           ("deep_local", "deep circuit, local cost", "-", "o", INK, INK),
           ("shallow_local", "shallow circuit, local cost", "--", "o", INK, "white")]
    for k, lab, ls, mk, col, mf in sty:
        ax.semilogy(n, [x[k] for x in r], ls=ls, marker=mk, color=col, mfc=mf, mec=col, ms=6, lw=1.5, label=lab)
    ax.set_xlabel("Number of qubits"); ax.set_ylabel("Variance of the gradient")
    ax.set_xticks(n); ax.minorticks_off()
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.legend(loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0), columnspacing=1.0)
    save(fig, OUT, "Fig_6_2_barren_plateau")

def fig_6_3():
    H = 2.6; fig, ax = canvas(H)
    y = 1.55
    ax.add_patch(FancyArrowPatch((0.15, y), (W - 0.15, y), arrowstyle="<|-|>", mutation_scale=12, lw=1.3, color=INK))
    ax.text(0.15, y + 0.18, "trainable,\nclassically simulable", ha="left", va="bottom", linespacing=1.05)
    ax.text(W - 0.15, y + 0.18, "hard to simulate,\nhard to train", ha="right", va="bottom", linespacing=1.05)
    pts = [(0.75, "shallow circuits,\nlocal costs", "today"), (2.25, "structured or\nsymmetric models", "today"), (3.75, "deep random\ncircuits", "quantum")]
    for x, t, k in pts:
        ax.add_patch(Circle((x, y), 0.08, fc=c(k), ec="white", zorder=5))
        ax.text(x, y - 0.18, t, ha="center", va="top", linespacing=1.05)
    box(ax, 1.30, 0.02, 1.90, 0.40, "useful advantage needs both", k="missing", ls="--")
    save(fig, OUT, "Fig_6_3_trainability_tradeoff")

E = json.load(open("data/lab6_extensions_results.json"))

def _tidy(ax):
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

def fig_6_4():
    V = E["noise_plateau"]["variance"]
    fig = plt.figure(figsize=(W, 3.9)); ax = fig.add_axes([0.15, 0.13, 0.82, 0.60])
    sty = {"0.0": ("-", "o", "no noise"), "0.01": ((0, (5, 2)), "s", "p = 0.01 per qubit per layer"), "0.03": ((0, (1.5, 1.5)), "^", "p = 0.03 per qubit per layer")}
    for k, (ls, mk, lab) in sty.items():
        d = [int(x) for x in V[k]]; ax.semilogy(d, list(V[k].values()), ls=ls, marker=mk, color=c("quantum"), ms=4, lw=1.6, mfc="white", label=lab)
    ax.set_xlabel("Circuit depth (layers)"); ax.set_ylabel("Variance of the gradient"); ax.set_xticks([1, 2, 4, 8, 12, 16, 20])
    ax.minorticks_off(); _tidy(ax)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=1, frameon=False)
    save(fig, OUT, "Fig_6_4_noise_plateau")

def fig_6_5():
    A = E["amplitude_encoding"]; q = [a["qubits"] for a in A]
    fig = plt.figure(figsize=(W, 3.9)); ax = fig.add_axes([0.15, 0.13, 0.82, 0.60])
    ax.semilogy(q, [a["cx"] for a in A], "-o", color=c("quantum"), ms=4, lw=1.7, label="amplitude encoding: CX gates")
    ax.semilogy(q, [a["amplitudes"] for a in A], ":", color=GREY, lw=1.2, label="number of values loaded, $2^n$")
    ax.semilogy(q, q, "--s", color=GREY, ms=4, lw=1.2, mfc="white", label="angle encoding of n values: rotations")
    ax.set_xlabel("Qubits, n"); ax.set_ylabel("Count"); ax.set_xticks(q); ax.minorticks_off(); _tidy(ax)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=1, frameon=False)
    save(fig, OUT, "Fig_6_5_loading_cost")

def fig_6_6():
    Z = E["zne"]["results"]; q = [z["qubits"] for z in Z]
    fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0.15, 0.14, 0.82, 0.66])
    ax.plot(q, [1] * len(q), ":", color=GREY, lw=1.2, label="ideal")
    ax.plot(q, [z["extrapolated"] for z in Z], "-o", color=c("quantum"), ms=4, lw=1.7, label="zero-noise extrapolation")
    ax.plot(q, [z["raw"] for z in Z], "--s", color=c("quantum"), ms=4, lw=1.2, mfc="white", label="unmitigated")
    ax.plot(q, [z["folded5"] for z in Z], ls=(0, (1.5, 1.5)), marker="^", color=GREY, ms=4, lw=1.2, mfc="white", label="noise scaled by 5")
    ax.set_ylim(0.68, 1.02); ax.set_xticks(q); ax.set_xlabel("GHZ qubits"); ax.set_ylabel("Probability of a correct outcome"); _tidy(ax)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False)
    save(fig, OUT, "Fig_6_6_zne")

if __name__ == "__main__":
    for fn in (fig_6_1, fig_6_2, fig_6_3, fig_6_4, fig_6_5, fig_6_6):
        fn()
    print("done")
