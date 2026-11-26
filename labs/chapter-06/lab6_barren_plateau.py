"""Chapter 6 lab: reproduce a barren plateau and test one remedy.

A hardware-efficient circuit (RY and RZ on every qubit, then a ladder of CZ gates) is drawn at
random. The gradient of the cost with respect to the first parameter is computed exactly with
the parameter-shift rule, for 300 random parameter settings, and its variance is recorded.
  Global cost: probability that the whole register returns to |0...0> (cost = 1 - that probability).
  Local cost:  average over qubits of the probability that each qubit is measured in |0>.
Deep circuits use depth equal to the number of qubits; shallow circuits use 2 layers.
Following McClean et al. (2018) and Cerezo et al. (2021), a barren plateau is a variance that falls
exponentially with the number of qubits.
Runs on a laptop with NumPy in about two minutes.
"""
import json
import numpy as np

rng = np.random.default_rng(6)
SAMPLES = 300

def apply_1q(psi, U, q, n):
    psi = psi.reshape([2] * n)
    psi = np.moveaxis(np.tensordot(U, psi, axes=([1], [q])), 0, q)
    return psi.reshape(-1)

def ry(t): c, s = np.cos(t / 2), np.sin(t / 2); return np.array([[c, -s], [s, c]], dtype=complex)
def rz(t): return np.array([[np.exp(-1j * t / 2), 0], [0, np.exp(1j * t / 2)]], dtype=complex)

def cz_ladder(n):
    idx = np.arange(2 ** n); sign = np.ones(2 ** n)
    for q in range(n - 1):
        b1 = (idx >> (n - 1 - q)) & 1; b2 = (idx >> (n - 2 - q)) & 1
        sign *= np.where((b1 & b2) == 1, -1, 1)
    return sign

def state(theta, n, layers, ladder):
    psi = np.zeros(2 ** n, dtype=complex); psi[0] = 1
    th = theta.reshape(layers, n, 2)
    for l in range(layers):
        for q in range(n):
            psi = apply_1q(psi, ry(th[l, q, 0]), q, n)
            psi = apply_1q(psi, rz(th[l, q, 1]), q, n)
        psi = psi * ladder
    return psi

def costs(psi, n):
    p = np.abs(psi) ** 2
    glob = 1 - p[0]
    pr = p.reshape([2] * n)
    loc = 1 - np.mean([pr.sum(axis=tuple(a for a in range(n) if a != q))[0] for q in range(n)])
    return glob, loc

def grad_variance(n, layers):
    ladder = cz_ladder(n); P = layers * n * 2
    g_glob, g_loc = [], []
    for _ in range(SAMPLES):
        th = rng.uniform(0, 2 * np.pi, P)
        e = np.zeros(P); e[0] = np.pi / 2
        gp, lp = costs(state(th + e, n, layers, ladder), n)
        gm, lm = costs(state(th - e, n, layers, ladder), n)
        g_glob.append((gp - gm) / 2); g_loc.append((lp - lm) / 2)
    return float(np.var(g_glob)), float(np.var(g_loc))

if __name__ == "__main__":
    out = {"samples": SAMPLES, "rows": []}
    for n in range(2, 13, 2):
        deep_g, deep_l = grad_variance(n, n)
        sh_g, sh_l = grad_variance(n, 2)
        row = {"n": n, "deep_global": deep_g, "deep_local": deep_l, "shallow_global": sh_g, "shallow_local": sh_l}
        out["rows"].append(row); print(row)
    ns = np.array([r["n"] for r in out["rows"]])
    for k in ("deep_global", "deep_local", "shallow_global", "shallow_local"):
        v = np.array([r[k] for r in out["rows"]])
        slope = np.polyfit(ns, np.log2(v), 1)[0]
        out[k + "_log2_slope_per_qubit"] = float(slope)
        print(k, "variance halves every", round(-1 / slope, 2) if slope < 0 else "n/a", "qubits; slope", round(slope, 3))
    json.dump(out, open("lab6_results.json", "w"), indent=1)
