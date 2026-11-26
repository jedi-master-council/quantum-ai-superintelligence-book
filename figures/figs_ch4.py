"""Chapter 4 figures."""
import sys, json, math
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
D = json.load(open("data/lab4_results.json"))

def fig_4_1():
    """Amplitude amplification for 3 qubits, marked state 101: amplitudes after 0, 1 and 2 iterations."""
    N = 8; m = 5
    def amps(k):
        th = math.asin(1 / math.sqrt(N))
        am = math.sin((2 * k + 1) * th); ao = math.cos((2 * k + 1) * th) / math.sqrt(N - 1)
        return [am if i == m else ao for i in range(N)]
    fig = plt.figure(figsize=(W, 3.3))
    labels = [format(i, "03b") for i in range(N)]
    for j, k in enumerate((0, 1, 2)):
        ax = fig.add_axes([0.15 + j * 0.285, 0.25, 0.25, 0.60])
        a = amps(k)
        ax.bar(range(N), a, 0.7, color=[c("quantum") if i == m else f("today") for i in range(N)],
               ec=[c("quantum") if i == m else c("today") for i in range(N)], lw=0.8)
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_ylim(-0.2, 1.18); ax.set_xticks([m]); ax.set_xticklabels(["101"])
        ax.set_title(f"after {k} iteration" + ("s" if k != 1 else ""), pad=4)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        if j == 0:
            ax.set_ylabel("Amplitude")
        else:
            ax.set_yticklabels([])
        ax.text(m, a[m] + 0.04, f"{a[m] ** 2:.2f}", ha="center", va="bottom")
    fig.text(0.55, 0.04, "Eight possible answers; the marked answer 101 in green. Number above the bar: probability of measuring it.",
             ha="center", va="bottom", wrap=True)
    save(fig, OUT, "Fig_4_1_amplitude_amplification")

def fig_4_2():
    s = D["sweep_3q"]
    it = [r["iterations"] for r in s]
    fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0.14, 0.14, 0.84, 0.64])
    xs = np.linspace(0, 6, 300); th = math.asin(1 / math.sqrt(8))
    ax.plot(xs, np.sin((2 * xs + 1) * th) ** 2, color=GREY, lw=1.0, ls=(0, (4, 2)), label="theory")
    ax.plot(it, [r["ideal"] for r in s], "o", mfc="white", mec=c("today"), mew=1.5, ms=7, label="ideal simulator")
    ax.plot(it, [r["fez"] for r in s], "s-", color=c("quantum"), ms=6, lw=1.6, label="noise model of IBM Fez")
    ax.axhline(1 / 8, color=c("today"), lw=0.8, ls=":")
    ax.text(6.1, 1 / 8 + 0.02, "random\nguess", va="bottom", ha="right", color=GREY, linespacing=1.0)
    ax.set_xlabel("Grover iterations"); ax.set_ylabel("Probability of answer 101")
    ax.set_ylim(0, 1.05); ax.set_xticks(it)
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, handlelength=1.6, columnspacing=0.8)
    save(fig, OUT, "Fig_4_2_grover_iterations")

def fig_4_3():
    s = D["scaling"]; n = [r["n"] for r in s]
    fig = plt.figure(figsize=(W, 4.4)); ax = fig.add_axes([0.14, 0.30, 0.84, 0.54])
    ax.plot(n, [r["ideal"] for r in s], "o-", mfc="white", mec=c("today"), color=c("today"), mew=1.5, ms=7, label="ideal simulator")
    ax.plot(n, [r["fez"] for r in s], "s-", color=c("quantum"), ms=6, lw=1.8, label="IBM Fez (Heron) noise")
    ax.plot(n, [r["sherbrooke"] for r in s], "^--", color=c("quantum"), mfc="white", ms=7, lw=1.4, label="IBM Sherbrooke (Eagle) noise")
    ax.plot(n, [r["random_guess"] for r in s], ":", color=INK, lw=1.2, label="random guess")
    for r in s[1:]:
        last = r["n"] == s[-1]["n"]
        ax.text(r["n"] + (-0.1 if last else 0.08), r["fez"] + 0.03, f"{r['fez']:.2f}", ha="right" if last else "left", bbox=dict(fc="white", ec="none", pad=0.4))
    ax.set_xticks(n); ax.set_ylim(0, 1.08)
    ax.set_xlabel("Qubits (search space of 2 to the power n answers)"); ax.set_ylabel("Probability of correct answer")
    top = ax.secondary_xaxis("top"); top.set_xticks(n); top.set_xticklabels([str(r["fez_2q"]) for r in s])
    top.set_xlabel("Two-qubit gates after transpilation (IBM Fez)")
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.spines["right"].set_visible(False)
    fig.legend(loc="lower center", frameon=False, ncol=2, bbox_to_anchor=(0.5, 0.0), columnspacing=1.0)
    save(fig, OUT, "Fig_4_3_grover_scaling")

def fig_4_4():
    rows = [(2019, "Random-circuit sampling,\n53 qubits (Google)", 2022, "Same samples in about\n15 h on 512 GPUs"),
            (2023, "Kicked Ising dynamics,\n127 qubits (IBM)", 2023, "Tensor-network and\nPauli simulations, faster"),
            (2025, "Quantum Echoes,\nverifiable OTOC (Google)", None, "No classical match\npublished at writing")]
    H = 3.9; fig, ax = canvas(H)
    ax.text(0.02, H - 0.05, "Quantum claim", va="top", fontweight="bold")
    ax.text(2.50, H - 0.05, "Classical response", va="top", fontweight="bold")
    y = H - 0.40
    for qy, qt, cy, ct in rows:
        box(ax, 0.02, y - 0.92, 1.98, 0.92, qt, title=str(qy), k="quantum", align="left")
        if cy:
            box(ax, 2.50, y - 0.92, 1.98, 0.92, ct, title=str(cy), k="today", align="left")
            arrow(ax, 2.00, y - 0.46, 2.50, y - 0.46, color=GREY)
        else:
            box(ax, 2.50, y - 0.92, 1.98, 0.92, ct, title="open", k="missing", align="left", ls="--")
            arrow(ax, 2.00, y - 0.46, 2.50, y - 0.46, color=c("missing"), ls=(0, (4, 2)))
        y -= 1.14
    save(fig, OUT, "Fig_4_4_advantage_claims")

if __name__ == "__main__":
    for fn in (fig_4_1, fig_4_2, fig_4_3, fig_4_4):
        fn()
    print("done")
