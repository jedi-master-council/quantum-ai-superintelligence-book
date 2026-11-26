"""Shared style for all book figures.
Figures are drawn at printed size (4.5 in text width) with 11 pt Times-metric text,
so figure text matches the body text. Colours follow the book's colour key:
each colour always stands for the same concept (see FrontMatter Fig. 2)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle
from PIL import Image

W = 4.5
FS = 11
INK = "#1B1F24"
# ---- colour key: (line colour, fill colour)
KEY = {
    "today":   ("#56626E", "#EEF1F4"),   # today's AI and classical computing; evidence
    "agi":     ("#1F5FAE", "#E4EEFA"),   # artificial general intelligence; Part I
    "asi":     ("#C8601C", "#FCEBDD"),   # superintelligence and the intelligence explosion; Part III
    "sing":    ("#6B3FA0", "#EFE7F7"),   # technological singularity
    "quantum": ("#2E7D3A", "#E3F2E5"),   # quantum hardware and quantum machine intelligence; Part II
    "mind":    ("#00808A", "#DDF1F2"),   # minds and brains
    "secure":  ("#B3261E", "#FBE7E5"),   # security, control and governance; Part IV
    "missing": ("#B58900", "#FFF5C7"),   # missing or unconfirmed information
}
LABELS = {
    "today": "Today's AI and classical computing",
    "agi": "Artificial general intelligence (AGI)",
    "asi": "Superintelligence (ASI)",
    "sing": "Technological singularity",
    "quantum": "Quantum hardware and quantum machine intelligence",
    "mind": "Minds and brains",
    "secure": "Security, control and governance",
    "missing": "Missing or unconfirmed information",
}
GREY = KEY["today"][0]
LW = 0.9
plt.rcParams.update({"font.family": "Liberation Serif", "font.size": FS, "pdf.fonttype": 42, "svg.fonttype": "none",
                     "axes.titlesize": FS, "axes.labelsize": FS, "xtick.labelsize": FS, "ytick.labelsize": FS,
                     "legend.fontsize": FS, "text.color": INK, "axes.edgecolor": INK, "axes.linewidth": 0.8,
                     "xtick.color": INK, "ytick.color": INK, "xtick.major.width": 0.8, "ytick.major.width": 0.8,
                     "mathtext.fontset": "stix", "lines.linewidth": 1.6})

def c(k): return KEY[k][0]
def f(k): return KEY[k][1]

def canvas(h, w=W):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    return fig, ax

def save(fig, out, name):
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}/{name}.{ext}")
    fig.savefig(f"{out}/{name}.png", dpi=600)
    im = Image.open(f"{out}/{name}.png").convert("RGB")
    im.save(f"{out}/{name}.png", dpi=(600, 600))
    im.save(f"{out}/{name}.tif", dpi=(600, 600), compression="tiff_lzw")
    plt.close(fig)

def box(ax, x, y, w, h, text="", k="today", fill=True, title=None, align="center", pad=0.08, lw=LW, bold=False, ls="-"):
    ec, fc = KEY[k]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.03",
                                fc=fc if fill else "white", ec=ec, lw=lw, ls=ls, zorder=2))
    tx = x + w / 2 if align == "center" else x + pad
    if title is None:
        ax.text(tx, y + h / 2, text, ha=align, va="center", zorder=3, linespacing=1.15,
                fontweight="bold" if bold else "normal")
    else:
        ax.text(tx, y + h - pad, title, ha=align, va="top", fontweight="bold", zorder=3)
        ax.text(tx, y + h - pad - 0.22, text, ha=align, va="top", zorder=3, linespacing=1.15)

def stripe(ax, x, y, h, k, w=0.05):
    """Coloured key stripe on the left edge of a box."""
    ax.add_patch(Rectangle((x, y), w, h, fc=c(k), ec="none", zorder=3))

def panel(ax, x, y, w, h, label=None, k="today"):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=c(k), lw=0.8, ls=(0, (4, 2.5)), zorder=1))
    if label:
        ax.text(x + 0.08, y + h - 0.06, label, ha="left", va="top", style="italic", color=INK, zorder=3)

def arrow(ax, x1, y1, x2, y2, color=INK, ls="-", lw=1.1, rad=0.0, head=10):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=head, lw=lw, color=color,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=4, shrinkA=0, shrinkB=0))

def badge(ax, x, y, s, k="today", r=0.11):
    ax.add_patch(Circle((x, y), r, fc=c(k), ec="white", lw=0.8, zorder=5))
    ax.text(x, y - 0.004, s, ha="center", va="center", color="white", fontweight="bold", zorder=6)
