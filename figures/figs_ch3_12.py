"""Chapter 3 and Chapter 12 figures at printed size, colour key from figstyle."""
import sys, json
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
D = json.load(open("data/lab3_results.json"))

def fig_3_1():
    H = 4.1; fig, ax = canvas(H)
    bw, bh = 1.86, 0.92
    xl, xr = 0.14, W - 0.14 - bw
    # top panel: reader's computer
    panel(ax, 0.02, 2.30, W - 0.04, 1.78, "On the reader's computer")
    panel(ax, 0.02, 0.02, W - 0.04, 1.78, "In the provider's cloud", k="quantum")
    yt, yb = 2.48, 0.20
    box(ax, xl, yt, bw, bh, "Write the circuit in\nQiskit or a visual\ncomposer", k="today")
    box(ax, xr, yt, bw, bh, "Transpile to the\nprocessor's native\ngates and qubits", k="today")
    box(ax, xr, yb, bw, bh, "Queue, then run the\nrequested number of\nshots on the processor", k="quantum")
    box(ax, xl, yb, bw, bh, "Return the counts and\ndeduct processor time\nfrom the allowance", k="quantum")
    for (x, y, n, k) in [(xl, yt, 1, "today"), (xr, yt, 2, "today"), (xr, yb, 3, "quantum"), (xl, yb, 4, "quantum")]:
        badge(ax, x + 0.02, y + bh - 0.02, str(n), k=k)
    arrow(ax, xl + bw, yt + bh / 2, xr, yt + bh / 2)
    arrow(ax, xr + bw / 2, yt, xr + bw / 2, yb + bh)
    ax.text(xr + bw / 2 - 0.1, 2.05, "circuit sent\nover the internet", ha="right", va="center", style="italic", color=GREY, linespacing=1.05)
    arrow(ax, xr, yb + bh / 2, xl + bw, yb + bh / 2)
    arrow(ax, xl + bw / 2, yb + bh, xl + bw / 2, yt, color=c("quantum"), ls=(0, (4, 2)))
    ax.text(xl + bw / 2 + 0.1, 2.05, "results\nreturned", ha="left", va="center", style="italic", color=GREY, linespacing=1.05)
    save(fig, OUT, "Fig_3_1_cloud_workflow")

def fig_3_6():
    H = 2.35; fig, ax = canvas(H)
    y0, y1 = 1.55, 0.85
    x0, x1 = 0.55, W - 0.15
    for y, lab in [(y0, "$q_0$"), (y1, "$q_1$")]:
        ax.plot([x0, x1], [y, y], color=INK, lw=1.0, zorder=1)
        ax.text(x0 - 0.12, y, lab, ha="right", va="center")
    G = c("quantum")
    # H gate
    gx = 1.05
    ax.add_patch(Rectangle((gx - 0.2, y0 - 0.2), 0.4, 0.4, fc=f("quantum"), ec=G, lw=1.2, zorder=3))
    ax.text(gx, y0, "H", ha="center", va="center", fontweight="bold", zorder=4)
    # CNOT
    cx = 2.05
    ax.plot([cx, cx], [y0, y1 - 0.15], color=G, lw=1.4, zorder=2)
    ax.add_patch(Circle((cx, y0), 0.07, fc=G, ec=G, zorder=3))
    ax.add_patch(Circle((cx, y1), 0.15, fc="white", ec=G, lw=1.4, zorder=3))
    ax.plot([cx - 0.15, cx + 0.15], [y1, y1], color=G, lw=1.4, zorder=4)
    ax.plot([cx, cx], [y1 - 0.15, y1 + 0.15], color=G, lw=1.4, zorder=4)
    # measurements
    for mx, y in [(3.05, y0), (3.55, y1)]:
        ax.add_patch(Rectangle((mx - 0.2, y - 0.2), 0.4, 0.4, fc="white", ec=INK, lw=1.1, zorder=3))
        t = np.linspace(np.pi * 0.15, np.pi * 0.85, 30)
        ax.plot(mx + 0.13 * np.cos(t), y - 0.08 + 0.13 * np.sin(t), color=INK, lw=0.9, zorder=4)
        ax.plot([mx, mx + 0.11], [y - 0.08, y + 0.09], color=INK, lw=0.9, zorder=4)
    # stage labels beneath
    for x, lab in [(1.05, "superposition"), (2.075, "entanglement"), (3.45, "measurement")]:
        ax.text(x, 0.30, lab, ha="center", va="center")
    for xs in (1.55, 2.6):
        ax.plot([xs, xs], [0.12, 1.95], color=GREY, lw=0.7, ls=(0, (3, 2)), zorder=0)
    ax.text(x1, 2.22, "outcomes: 00 or 11, never 01 or 10", ha="right", va="center", style="italic", color=GREY)
    save(fig, OUT, "Fig_3_6_bell_circuit")

def fig_3_7():
    keys = ["00", "01", "10", "11"]; S = D["shots"]
    ide = [D["bell_ideal"].get(k, 0) / S for k in keys]; noi = [D["bell_noisy"].get(k, 0) / S for k in keys]
    fig = plt.figure(figsize=(W, 3.5)); ax = fig.add_axes([0.14, 0.15, 0.84, 0.70])
    xs = np.arange(4)
    ax.bar(xs - 0.2, ide, 0.38, color=f("today"), ec=c("today"), lw=0.9, label="Ideal simulator")
    ax.bar(xs + 0.2, noi, 0.38, color=c("quantum"), ec=c("quantum"), lw=0.9, label="Noise model of IBM Fez (Heron)")
    for x, v in zip(xs, noi):
        ax.text(x + 0.2, v + 0.012, f"{v:.3f}", ha="center")
    ax.set_xticks(xs); ax.set_xticklabels(keys); ax.set_xlabel("Measured bit string (qubit 1, qubit 0)")
    ax.set_ylabel(f"Probability ({S:,} shots)"); ax.set_ylim(0, 0.6)
    ax.spines["right"].set_visible(False); ax.spines["top"].set_visible(False)
    ax.yaxis.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(-0.16, 1.0), ncol=1)
    ax.text(1.5, 0.30, "errors: 3.3% of shots", ha="center", va="bottom")
    for xb, v in [(1.2, noi[1]), (2.2, noi[2])]:
        ax.annotate("", xy=(xb, v + 0.045), xytext=(1.5, 0.29), arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    save(fig, OUT, "Fig_3_7_bell_ideal_vs_noisy")

def fig_3_8():
    n = [r["n"] for r in D["ghz"]]; p = [r["p_correct"] for r in D["ghz"]]; g2 = [r["two_qubit_gates"] for r in D["ghz"]]
    fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0.15, 0.14, 0.82, 0.66])
    ax.axhline(1.0, color=GREY, ls=(0, (5, 2)), lw=1.2, label="Ideal simulator")
    ax.plot(n, p, marker="o", ms=5, color=c("quantum"), lw=1.8, label="Noise model of IBM Fez (Heron)")
    ax.set_xlabel("Number of entangled qubits (GHZ state)"); ax.set_ylabel("Probability correct")
    ax.set_ylim(0.8, 1.02); ax.set_xticks(n[::2])
    ax.spines["right"].set_visible(False)
    top = ax.secondary_xaxis("top"); top.set_xticks(n[::2]); top.set_xticklabels([str(g) for g in g2[::2]])
    top.set_xlabel("Native two-qubit gates after transpilation")
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower left")
    save(fig, OUT, "Fig_3_8_ghz_scaling")

def fig_12_1():
    cols = [("Quantum hardware", "quantum", ["Logical qubits sustained", "Logical error rates", "Error-corrected\nalgorithm demonstrations"]),
            ("AI capability", "agi", ["Autonomous task length", "Expert benchmarks\nnot yet saturated", "AI-led research results"]),
            ("Brains and bodies", "mind", ["Size of whole-brain\nsimulations", "Brain-computer\ninterface outcomes", "General-purpose robots"]),
            ("Resources and rules", "secure", ["Training compute\nand energy", "Investment in quantum\nand AI", "Governance and\nexport controls"])]
    cw, chh = 2.18, 2.55
    H = 2 * chh + 0.12; fig, ax = canvas(H)
    n = 1
    for i, (t, k, items) in enumerate(cols):
        x = 0.02 + (i % 2) * (cw + 0.10); y = H - 0.02 - (i // 2 + 1) * chh - (i // 2) * 0.08
        ax.add_patch(Rectangle((x, y), cw, chh, fc="white", ec=c(k), lw=LW))
        ax.add_patch(Rectangle((x, y + chh - 0.38), cw, 0.38, fc=f(k), ec=c(k), lw=LW))
        ax.add_patch(Rectangle((x, y + chh - 0.38), 0.06, 0.38, fc=c(k), ec="none"))
        ax.text(x + 0.14, y + chh - 0.19, t, va="center", fontweight="bold")
        for j, it in enumerate(items):
            by = y + chh - 0.38 - 0.10 - (j + 1) * 0.66 + 0.06
            box(ax, x + 0.10, by, cw - 0.20, 0.58, "", k=k, fill=False)
            badge(ax, x + 0.26, by + 0.29, str(n), k=k, r=0.1); n += 1
            ax.text(x + 0.44, by + 0.29, it, va="center", linespacing=1.05)
    save(fig, OUT, "Fig_12_1_watchlist")

def fig_12_2():
    steps = [("Record the indicators", "Note each indicator's current value,\nwith its source and date", None),
             ("Compare with the thresholds", "Mark indicators that have crossed\nor moved towards their thresholds", None),
             ("Rerun the models", "", ["AGI forecast", "Singularity model", "Brain timeline"]),
             ("Revise the dated estimates", "Write down each new estimate and\nthe reason it changed", None),
             ("Set next year's thresholds", "Raise any threshold that has\nbeen crossed", None)]
    bw, bh, g = 3.6, 0.80, 0.28
    H = len(steps) * bh + (len(steps) - 1) * g + 0.04; fig, ax = canvas(H)
    y = H - 0.02; pos = []
    for i, (t, b, chips) in enumerate(steps):
        y0 = y - bh
        box(ax, 0.02, y0, bw, bh, b, title=f"{i + 1}  {t}", k="today", align="left")
        if chips:
            ks = ["agi", "sing", "mind"]; cx = 0.10
            widths = [1.02, 1.28, 1.12]
            for ch, k, wdt in zip(chips, ks, widths):
                ax.add_patch(FancyBboxPatch((cx, y0 + 0.10), wdt, 0.30, boxstyle="round,pad=0,rounding_size=0.03", fc=f(k), ec=c(k), lw=LW, zorder=3))
                ax.text(cx + wdt / 2, y0 + 0.25, ch, ha="center", va="center", zorder=4)
                cx += wdt + 0.06
        pos.append(y0); y = y0 - g
    for i in range(4):
        arrow(ax, 0.40, pos[i], 0.40, pos[i + 1] + bh)
    # return loop on the right
    rx = bw + 0.32
    ax.plot([0.02 + bw, rx], [pos[4] + bh / 2] * 2, color=INK, lw=1.1)
    ax.plot([rx, rx], [pos[4] + bh / 2, pos[0] + bh / 2], color=INK, lw=1.1)
    arrow(ax, rx, pos[0] + bh / 2, 0.02 + bw, pos[0] + bh / 2)
    ax.text(rx + 0.08, (pos[0] + pos[4] + bh) / 2, "once a\nyear", ha="left", va="center", style="italic", color=GREY, linespacing=1.05)
    save(fig, OUT, "Fig_12_2_annual_review")

if __name__ == "__main__":
    for fn in (fig_3_1, fig_3_6, fig_3_7, fig_3_8, fig_12_1, fig_12_2):
        fn()
    print("done")
