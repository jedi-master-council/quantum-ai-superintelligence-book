"""Chapter 11 figures."""
import sys, json
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
R = json.load(open("data/lab11_results.json"))

def tidy(ax, grid="both"):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(True, axis=grid, color="#C5CBD2", lw=0.5, ls=(0, (1, 2)))
    ax.set_axisbelow(True)

def lbl(ax, x, y, s, ha="left"):
    ax.text(x, y, s, ha=ha, va="center", fontsize=9.5, zorder=6, bbox=dict(fc="white", ec="none", pad=0.4))

def fig_11_1():
    H = 5.6; fig, ax = canvas(H)
    panel(ax, 0.02, 2.95, 2.13, 2.60, "Developer domain", k="today")
    panel(ax, 2.35, 2.95, 2.13, 2.60, "Quantum cloud provider", k="quantum")
    panel(ax, 0.02, 0.95, 4.46, 1.75, "Deployment domain", k="today")
    box(ax, 0.12, 4.25, 1.93, 0.80, "weights, training\ndata, evaluations", title="AI assets", k="today", align="left")
    box(ax, 0.12, 3.08, 1.93, 0.80, "circuits and\nhybrid workflows", title="Quantum jobs", k="today", align="left")
    box(ax, 2.45, 4.10, 1.93, 0.95, "results, calibration\nand device data", title="Quantum processor", k="quantum", align="left")
    box(ax, 2.45, 3.08, 1.93, 0.62, "tampered or\nleaked results", k="secure", align="left")
    badge(ax, 4.30, 3.62, "3", k="secure")
    box(ax, 0.12, 1.05, 1.93, 1.20, "serves users and\nacts through tools;\nmay be misused or\nmisaligned", title="Deployed model", k="asi", align="left")
    badge(ax, 1.95, 2.17, "4", k="secure")
    box(ax, 2.45, 1.05, 1.93, 1.20, "storage, backups,\ncommunication", title="Encrypted channels", k="today", align="left")
    arrow(ax, 2.05, 3.60, 2.45, 4.30, color=INK); lbl(ax, 2.25, 3.98, "TLS", ha="center")
    arrow(ax, 3.41, 4.10, 3.41, 3.70, color=c("secure"), ls="--")
    arrow(ax, 1.08, 4.25, 1.08, 3.88, color=INK)
    arrow(ax, 1.08, 3.08, 1.08, 2.25, color=INK); lbl(ax, 1.14, 2.82, "release")
    arrow(ax, 2.05, 1.65, 2.45, 1.65, color=INK)
    box(ax, 2.45, 0.05, 1.93, 0.72, "records traffic today to\ndecrypt with a future CRQC", k="secure", align="left")
    box(ax, 0.12, 0.05, 1.93, 0.72, "steals or alters weights\nand quantum jobs", k="secure", align="left")
    badge(ax, 4.30, 0.70, "1", k="secure"); badge(ax, 1.95, 0.70, "2", k="secure")
    arrow(ax, 3.41, 0.77, 3.41, 1.05, color=c("secure"), ls="--")
    arrow(ax, 1.08, 0.77, 1.08, 1.05, color=c("secure"), ls="--")
    save(fig, OUT, "Fig_11_1_threat_model")

def fig_11_2():
    H = 4.4; fig, ax = canvas(H)
    box(ax, 0.02, 3.45, 1.35, 0.80, "weights file", title="Model", k="today", align="left")
    box(ax, 1.57, 3.45, 1.35, 0.80, "X25519", title="Classical KEM", k="today", align="left")
    box(ax, 3.12, 3.45, 1.36, 0.80, "ML-KEM-768", title="Post-quantum", k="secure", align="left")
    box(ax, 2.10, 2.15, 1.85, 0.75, "combine two secrets\ninto one AES key", title="HKDF-SHA256", k="secure", align="left")
    box(ax, 0.02, 0.95, 1.95, 0.85, "encrypt and\nauthenticate", title="AES-256-GCM", k="secure", align="left")
    box(ax, 2.40, 0.95, 2.08, 0.85, "file, size, SHA-256,\nalgorithms", title="Manifest", k="today", align="left")
    box(ax, 2.40, 0.02, 2.08, 0.70, "Ed25519 + ML-DSA-65", title=None, k="secure")
    for xs in (2.24, 3.80):
        arrow(ax, xs, 3.45, 3.02 if xs < 3 else 3.30, 2.90, color=c("secure"))
    lbl(ax, 2.30, 3.15, "secret 1"); lbl(ax, 3.62, 3.15, "secret 2")
    arrow(ax, 0.70, 3.45, 0.70, 1.80); lbl(ax, 0.76, 2.60, "plaintext")
    arrow(ax, 2.10, 2.52, 1.40, 1.80, color=c("secure")); lbl(ax, 1.68, 2.24, "key", ha="right")
    arrow(ax, 2.40, 1.38, 1.97, 1.38, color=INK); lbl(ax, 2.19, 1.55, "bound in", ha="center")
    arrow(ax, 3.44, 0.95, 3.44, 0.72, color=c("secure")); lbl(ax, 3.50, 0.84, "signed by")
    save(fig, OUT, "Fig_11_2_hybrid_envelope")

def fig_11_3():
    S = R["lab11_1"]["sizes_bytes"]
    rows = [("X25519", "public_key", "ciphertext", "today"), ("ML-KEM-768", "public_key", "ciphertext", "secure"),
            ("RSA-3072 (OAEP)", "public_key", "ciphertext", "today"), ("Ed25519", "public_key", "signature", "today"),
            ("ML-DSA-65", "public_key", "signature", "secure"), ("RSA-3072 (PSS)", "public_key", "signature", "today")]
    fig = plt.figure(figsize=(W, 3.9)); ax = fig.add_axes([0.30, 0.25, 0.66, 0.72])
    yy = np.arange(len(rows))[::-1]
    for y, (n, a, b, k) in zip(yy, rows):
        ax.barh(y + 0.18, S[n][a], 0.34, color=f(k), ec=c(k), lw=1.0)
        ax.barh(y - 0.18, S[n][b], 0.34, color=c(k), ec=c(k), lw=1.0)
        ax.text(S[n][a] * 1.15, y + 0.18, f"{S[n][a]:,}", va="center", fontsize=9.5)
        ax.text(S[n][b] * 1.15, y - 0.18, f"{S[n][b]:,}", va="center", fontsize=9.5)
    ax.set_yticks(yy); ax.set_yticklabels([r[0] for r in rows]); ax.tick_params(axis="y", length=0)
    ax.set_xscale("log"); ax.set_xlim(10, 2e4); ax.set_xlabel("Bytes (logarithmic scale)")
    ax.axhline(2.5, color=GREY, lw=0.6)
    ax.text(2500, 5.45, "Key\nestablishment", fontstyle="italic", va="center")
    ax.text(1600, 2.75, "Signatures", fontstyle="italic", va="center")
    ax.minorticks_off(); tidy(ax, grid="x")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(fc="white", ec=INK, label="public key"), Patch(fc=INK, ec=INK, label="ciphertext or signature")],
               loc="lower left", bbox_to_anchor=(0.02, 0.0), ncol=2, frameon=False)
    save(fig, OUT, "Fig_11_3_sizes")

def fig_11_4():
    C = R["lab11_2_curve"]; xs = C["shelf_life_years"]
    fig = plt.figure(figsize=(W, 3.4)); ax = fig.add_axes([0.14, 0.17, 0.83, 0.68])
    sty = {"2026": ("-", 2.0), "2030": ((0, (5, 2)), 1.7), "2035": ((0, (1.5, 1.5)), 1.9)}
    for k, (ls, lw) in sty.items():
        ax.plot(xs, C["p_exposed"][k], color=c("secure"), ls=ls, lw=lw, label=f"migration starts {k}")
    for a, (lo, hi), yv in (("weights", (2, 5), 1.04), ("personal data", (10, 25), 1.04)):
        ax.annotate("", (lo, yv), (hi, yv), arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.9), annotation_clip=False)
        ax.text((lo + hi) / 2, yv + 0.02, a, ha="center", va="bottom", color=INK, fontsize=9.5)
    ax.set_xlim(0, 30); ax.set_ylim(0, 1.0)
    ax.set_xlabel("Years the asset must stay secret (shelf life)"); ax.set_ylabel("Probability of exposure")
    tidy(ax, grid="both")
    ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="none")
    save(fig, OUT, "Fig_11_4_mosca")

if __name__ == "__main__":
    for fn in (fig_11_1, fig_11_2, fig_11_3, fig_11_4):
        fn()
