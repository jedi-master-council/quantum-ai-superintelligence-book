"""Chapter 5 figures."""
import sys, json
import numpy as np
from figstyle import *
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig"
D = json.load(open("data/lab5_results.json"))

def fig_5_1():
    H = 2.75; fig, ax = canvas(H)
    yq = [1.75, 0.95]; x0 = 0.42
    for y, lab in zip(yq, ["$q_0$", "$q_1$"]):
        ax.plot([x0, W - 0.30], [y, y], color=INK, lw=1.0, zorder=1)
        ax.text(x0 - 0.08, y, lab, ha="right", va="center")
    bw, gap = 0.20, 0.03
    x = x0 + 0.10
    for l in range(3):
        lx = x - 0.05
        for (kind, lab) in [("today", "x"), ("quantum", "θ"), ("quantum", "θ")]:
            for j, y in enumerate(yq):
                t = (f"R$_Y$({lab}$_{j + 1}$)" if lab == "x" else "")
                ax.add_patch(Rectangle((x, y - 0.17), bw, 0.34, fc=f(kind), ec=c(kind), lw=0.9, zorder=3))
            x += bw + gap
        cx = x + 0.04
        ax.plot([cx, cx], yq, color=c("quantum"), lw=1.2, zorder=2)
        for y in yq:
            ax.add_patch(Circle((cx, y), 0.05, fc=c("quantum"), ec=c("quantum"), zorder=3))
        x = cx + 0.08
        ax.add_patch(Rectangle((x, yq[0] - 0.17), bw, 0.34, fc=f("quantum"), ec=c("quantum"), lw=0.9, zorder=3))
        ax.add_patch(Rectangle((x, yq[1] - 0.17), bw, 0.34, fc=f("quantum"), ec=c("quantum"), lw=0.9, zorder=3))
        x += bw + 0.10
        ax.add_patch(Rectangle((lx, 0.62), x - lx - 0.10, 1.48, fill=False, ec=GREY, lw=0.7, ls=(0, (3, 2)), zorder=0))
        ax.text((lx + x - 0.10) / 2, 2.17, f"layer {l + 1}", ha="center", va="bottom", style="italic", color=GREY)
    # measurement
    mx = W - 0.30
    ax.add_patch(Rectangle((mx - 0.02, yq[0] - 0.17), 0.30, 0.34, fc="white", ec=INK, lw=0.9, zorder=3))
    ax.text(mx + 0.13, yq[0], "Z", ha="center", va="center", zorder=4)
    # key
    ax.add_patch(Rectangle((0.42, 0.10), 0.26, 0.22, fc=f("today"), ec=c("today"), lw=0.9))
    ax.text(0.74, 0.21, "data: R$_Y$(x$_1$), R$_Y$(x$_2$)", va="center")
    ax.add_patch(Rectangle((2.45, 0.10), 0.26, 0.22, fc=f("quantum"), ec=c("quantum"), lw=0.9))
    ax.text(2.77, 0.21, "trainable rotations", va="center")
    save(fig, OUT, "Fig_5_1_vqc_circuit")

def fig_5_2():
    h = D["vqc_history"]; ep = [r["epoch"] for r in h]
    fig = plt.figure(figsize=(W, 3.1)); ax = fig.add_axes([0.13, 0.16, 0.72, 0.80])
    ax.plot(ep, [r["loss"] for r in h], color=c("quantum"), lw=1.8, label="training loss (left axis)")
    ax.set_xlabel("Epoch"); ax.set_ylabel("Mean squared error"); ax.set_ylim(0, max(r["loss"] for r in h) * 1.1)
    r = ax.twinx(); r.plot(ep, [x["test_acc"] for x in h], color=INK, lw=1.4, ls=(0, (5, 2)), label="test accuracy (right axis)")
    r.set_ylim(0.5, 1.0); r.set_ylabel("Test accuracy")
    ax.grid(True, color="#C5CBD2", lw=0.5, ls=(0, (1, 2))); ax.set_axisbelow(True)
    l1, a1 = ax.get_legend_handles_labels(); l2, a2 = r.get_legend_handles_labels()
    ax.legend(l1 + l2, a1 + a2, loc="center right", ncol=1, frameon=False, handlelength=2.0)
    save(fig, OUT, "Fig_5_2_training_curve")

def fig_5_3():
    g = np.array(D["grid"]["x"]); Z = np.array(D["grid"]["vqc"])
    X = np.array(D["test_points"]["X"]); y = np.array(D["test_points"]["y"])
    fig = plt.figure(figsize=(W, 3.9)); ax = fig.add_axes([0.13, 0.13, 0.84, 0.70])
    from matplotlib.colors import ListedColormap
    ax.contourf(g, g, Z, levels=[-1, 0, 1], colors=[f("quantum"), "#FFFFFF"], alpha=1.0)
    ax.contour(g, g, Z, levels=[0], colors=[c("quantum")], linewidths=1.6)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], s=16, marker="o", facecolors="white", edgecolors=INK, linewidths=0.8, label="class 0")
    ax.scatter(X[y == 1, 0], X[y == 1, 1], s=16, marker="o", color=INK, label="class 1")
    ax.set_xlabel("Feature 1 (scaled to 0 to π)"); ax.set_ylabel("Feature 2")
    from matplotlib.patches import Patch
    h, l = ax.get_legend_handles_labels()
    h.append(Patch(fc=f("quantum"), ec=c("quantum"), label="classified as 1")); l.append("predicted class 1")
    ax.legend(h, l, loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=3, frameon=False, handletextpad=0.3, columnspacing=0.8)
    save(fig, OUT, "Fig_5_3_decision_boundary")

def fig_5_4():
    rows = [("Logistic regression", D["logistic_test_acc"], D["logistic_params"], "today"),
            ("Neural network, untuned", D["mlp_untuned_test_acc"], D["mlp_params"], "today"),
            ("Neural network, tuned", D["mlp_test_acc"], D["mlp_params"], "today"),
            ("SVM, RBF kernel", D["rbf_svm_test_acc"], None, "today"),
            ("SVM, quantum kernel", D["qkernel_test_acc"], None, "quantum"),
            ("Quantum classifier, ideal", D["vqc_test_acc"], D["vqc_params"], "quantum"),
            ("Quantum classifier, IBM Fez noise", D["vqc_noisy_fez_test_acc"], D["vqc_params"], "quantum")]
    fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0.03, 0.14, 0.94, 0.84])
    n = len(rows); ax.set_ylim(-0.6, n - 0.4); ax.invert_yaxis(); ax.set_xlim(0.5, 1.0)
    for i, (lab, acc, p, k) in enumerate(rows):
        ax.barh(i + 0.12, acc - 0.5, left=0.5, height=0.36, color=f(k), ec=c(k), lw=0.9)
        ax.text(0.505, i - 0.27, lab + (f"  ({p} parameters)" if p else ""), va="center")
        ax.text(acc + 0.004, i + 0.12, f"{acc:.3f}", va="center")
    ax.set_yticks([]); [ax.spines[s].set_visible(False) for s in ("left", "right", "top")]
    ax.set_xlabel("Test accuracy on 200 points")
    save(fig, OUT, "Fig_5_4_model_comparison")

if __name__ == "__main__":
    for fn in (fig_5_1, fig_5_2, fig_5_3, fig_5_4):
        fn()
    print("done")
