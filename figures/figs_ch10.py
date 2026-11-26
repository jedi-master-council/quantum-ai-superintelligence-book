"""Chapter 10 figures."""
import sys, json
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
R = json.load(open("data/lab10_results.json"))

def tidy(ax, grid="both"):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(True, axis=grid if grid != "both" else "both", color="#C5CBD2", lw=0.5, ls=(0, (1, 2)))
    ax.set_axisbelow(True)

def fig_10_1():
    H = 4.6; fig, ax = canvas(H)
    cols = [("Record", "activity: which\nneurons fire,\nand when", "1"),
            ("Map", "wiring: every\nneuron and\nsynapse", "2"),
            ("Model", "equations for\neach neuron,\nand a body", "3")]
    bw, bh, gap = 1.36, 1.05, 0.12; x = 0.08; ytop = H - 0.38
    panel(ax, 0.02, ytop - bh - 0.10, 3 * bw + 2 * gap + 0.12, bh + 0.40, "Three capabilities", k="mind")
    xs = []
    for t, d, n in cols:
        box(ax, x, ytop - bh, bw, bh, d, title=t, k="mind", align="left")
        badge(ax, x + bw - 0.14, ytop - 0.14, n, k="mind")
        xs.append(x + bw / 2); x += bw + gap
    # emulation box below, arrows labelled
    ey = 1.42; box(ax, 0.55, ey, 3.40, 0.78, "a model that reproduces the behaviour\nof a specific brain at a stated level of detail", title="Brain emulation", k="mind", align="left")
    labels = ["data to fit\nand test", "structure", "dynamics"]
    for xc, lab in zip(xs, labels):
        x2 = min(max(xc, 0.75), 3.75)
        arrow(ax, xc, ytop - bh - 0.10, x2, ey + 0.78, color=c("mind"))
    ax.text(xs[0] - 0.62, 2.52, labels[0], ha="left", va="center", fontsize=9.5, color=INK,
            bbox=dict(fc="white", ec="none", pad=0.5), zorder=5)
    ax.text(xs[1] + 0.06, 2.52, labels[1], ha="left", va="center", fontsize=9.5, color=INK,
            bbox=dict(fc="white", ec="none", pad=0.5), zorder=5)
    ax.text(xs[2] + 0.06, 2.52, labels[2], ha="left", va="center", fontsize=9.5, color=INK,
            bbox=dict(fc="white", ec="none", pad=0.5), zorder=5)
    # quantum contributions at bottom
    box(ax, 0.04, 0.08, 2.10, 0.95, "quantum sensors (wearable\nMEG) improve recording", title="Plausible quantum role", k="quantum", align="left")
    box(ax, 2.36, 0.08, 2.10, 0.95, "quantum computers to run\nthe model: no evidence", title="Unsupported role", k="missing", align="left", ls="--")
    arrow(ax, 1.09, 1.03, 1.09, ey, color=c("quantum"), ls="--")
    ax.text(1.16, 1.22, "better data", ha="left", va="center", fontsize=9.5, bbox=dict(fc="white", ec="none", pad=0.5), zorder=5)
    arrow(ax, 3.41, 1.03, 3.41, ey, color=c("missing"), ls=":")
    ax.text(3.48, 1.22, "speed-up?", ha="left", va="center", fontsize=9.5, bbox=dict(fc="white", ec="none", pad=0.5), zorder=5)
    save(fig, OUT, "Fig_10_1_emulation_pipeline")

def fig_10_2():
    L = R["spiking"]; st, si = L["raster"]; st = np.array(st); si = np.array(si)
    fig = plt.figure(figsize=(W, 4.8))
    a1 = fig.add_axes([0.13, 0.57, 0.84, 0.37]); a2 = fig.add_axes([0.13, 0.10, 0.84, 0.30])
    sel = si < 200
    e = sel & (si < 160); i = sel & (si >= 160)
    a1.scatter(st[e] * 1000, si[e], s=1.2, color=c("mind"), lw=0, label="excitatory")
    a1.scatter(st[i] * 1000, si[i], s=1.2, color=c("secure"), lw=0, label="inhibitory")
    a1.set_xlim(0, 250); a1.set_ylim(-2, 202); a1.set_xlabel("Time (ms)"); a1.set_ylabel("Neuron")
    a1.text(0, 1.04, "(a) Spikes of 200 of 1,000 neurons", transform=a1.transAxes, ha="left", va="bottom")
    a1.legend(loc="upper right", bbox_to_anchor=(1.03, 1.13), ncol=2, frameon=False, markerscale=5, handletextpad=0.2)
    tidy(a1, grid=None)
    d = L["drive"]; x = [k["nu_rel"] for k in d]
    a2.plot(x, [k["rate_E"] for k in d], "-o", color=c("mind"), ms=4, lw=1.6)
    for k in d:
        if 0.9 < k["nu_rel"] < 1.1:
            a2.text(k["nu_rel"] + 0.08, k["rate_E"], f"CV {k['cv_isi']:.2f}", ha="left", va="center", fontsize=9.5)
        elif k["nu_rel"] < 0.9:
            a2.text(k["nu_rel"] - 0.04, k["rate_E"] + 2.5, f"CV {k['cv_isi']:.2f}", ha="center", va="bottom", fontsize=9.5)
        else:
            a2.text(k["nu_rel"] + 0.07, k["rate_E"] - 1.5, f"CV {k['cv_isi']:.2f}", ha="left", va="top", fontsize=9.5)
    a2.set_xlabel("External drive (multiple of the threshold rate)"); a2.set_ylabel("Mean rate (Hz)")
    a2.set_ylim(0, 52); a2.set_xlim(0.6, 4.6)
    a2.text(0, 1.04, "(b) Firing rate and irregularity (CV of intervals) against drive", transform=a2.transAxes, ha="left", va="bottom")
    tidy(a2)
    save(fig, OUT, "Fig_10_2_spiking_network")

def fig_10_3():
    L = R["timeline"]
    pts = [(1986, 7e3, "C. elegans", (6, -2)), (2023, 5.48e5, "larval fly", (-56, 0)), (2024, 5.45e7, "adult fly", (7, -6)),
           (2024, 1.5e8, "human, 1 mm$^3$", (-78, 0)), (2025, 5e8, "mouse, 1 mm$^3$", (6, 2))]
    fig = plt.figure(figsize=(W, 3.9)); ax = fig.add_axes([0.15, 0.14, 0.82, 0.80])
    ax.axhspan(5e10, 2e11, color=f("mind"), zorder=0); ax.text(1981, 1.1e11, "whole mouse brain", va="center", fontsize=9.5)
    ax.axhspan(1e14, 1e15, color=f("mind"), zorder=0); ax.text(1981, 3.2e14, "whole human brain", va="center", fontsize=9.5)
    for x, y, lab, off in pts:
        ax.plot(x, y, "o", color=c("mind"), ms=5, zorder=3)
        ax.annotate(lab, (x, y), xytext=off, textcoords="offset points", fontsize=9.5, va="center", zorder=4,
                    bbox=dict(fc="white", ec="none", pad=0.3))
    # projection: median and 10-90 years per tenfold
    yrs = np.linspace(2025, 2075, 200)
    for T, ls in ((5.5, "-"), (3.0, ":"), (8.0, ":")):
        ax.plot(yrs, 5e8 * 10 ** ((yrs - 2025) / T), color=c("missing"), ls=ls, lw=1.4, zorder=2)
    ax.text(2041, 2e7, "projection: tenfold every\n3, 5.5 or 8 years", fontsize=9.5, ha="left", va="center", color=INK,
            bbox=dict(fc="white", ec="none", pad=0.3))
    ax.set_yscale("log"); ax.set_xlim(1980, 2075); ax.set_ylim(1e3, 3e15)
    ax.set_xlabel("Year"); ax.set_ylabel("Synapses in largest connectome")
    ax.minorticks_off(); tidy(ax)
    save(fig, OUT, "Fig_10_5_connectome_growth")

def fig_10_4():
    rows = [("Microtubule superposition,\nTegmark (2000)", 1e-20, 1e-13, "quantum"),
            ("Microtubule superposition,\nHagan et al. (2002)", 1e-5, 1e-4, "quantum"),
            ("Single spike\n(action potential)", 1e-3, 2e-3, "mind"),
            ("Neural firing and\nbrain rhythms", 1e-3, 1e-1, "mind")]
    fig = plt.figure(figsize=(W, 2.9)); ax = fig.add_axes([0.38, 0.18, 0.59, 0.78])
    for i, (lab, lo, hi, k) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, np.log10(hi) - np.log10(lo), left=np.log10(lo), height=0.5, color=f(k), ec=c(k), lw=1.0,
                ls="--" if i == 1 else "-")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.set_xlim(-21, 0); ax.set_xticks(range(-20, 1, 4)); ax.set_xticklabels([f"$10^{{{k}}}$" for k in range(-20, 1, 4)])
    ax.set_xlabel("Time (seconds)"); tidy(ax, grid="x"); ax.tick_params(axis="y", length=0)
    save(fig, OUT, "Fig_10_3_decoherence")

def fig_10_5():
    L = R["quantum_neuron"]
    fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0.14, 0.15, 0.83, 0.62])
    sty = {"4": (c("quantum"), "o", "4 inputs, 3 qubits"), "8": (c("mind"), "s", "8 inputs, 4 qubits")}
    for k, (col, mk, lab) in sty.items():
        p = np.array(L[k]["points"]); jit = (0.012 if k == "4" else -0.012)
        ax.scatter(p[:, 0] + jit, p[:, 1], s=16, marker=mk, facecolor="white", edgecolor=col, lw=1.1, label=lab, zorder=3)
    ax.plot([0, 1], [0, 1], color=GREY, lw=0.8, ls=":", zorder=1); ax.text(0.80, 0.86, "ideal", color=GREY, rotation=0, ha="right")
    ax.axhline(0.5, color=GREY, lw=0.7, ls="--"); ax.text(0.02, 0.52, "firing threshold", color=GREY, va="bottom")
    ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("Ideal output, $|\\langle \\psi_w | \\psi_i \\rangle|^2$"); ax.set_ylabel("Output under Fez noise")
    tidy(ax)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.16, 1.02), ncol=2, frameon=False, handletextpad=0.2)
    save(fig, OUT, "Fig_10_4_quantum_neuron")

if __name__ == "__main__":
    for fn in (fig_10_1, fig_10_2, fig_10_3, fig_10_4, fig_10_5):
        fn()
